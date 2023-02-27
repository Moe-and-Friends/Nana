
import discord
from discord.ext import commands

from config import settings, RSS_OBSERVED_CHANNELS

from . import api_service as MAS
from . import webhook_templates as WT
from ..shared import discord_api_service as DAS

import re
from typing import List

# Note: This really doesn't necessarily have to be a Cog.
class MangaDex(commands.Cog, name = "MangaDex"):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # Pattern to match MangaDex chapter URLs of the forms:
    # [https://]mangadex.org/chapter/<UUID>[/page#]
    # Where the URL protocol and page number are optional.
    # Capture Group 1 is the chapter UUID
    # Capture Group 2 is the page number (optional)
    CHAPTER_PATTERN = re.compile(r'(?:https://)?mangadex.org/chapter/([\w-]+)(?:/(\d+))?')

    # Pattern to match MangaDex manga URLs of the forms:
    # [https://]mangadex.org/title/<UUID>[/name]
    # Where the URL protocol and human-readable name are optional.
    # Capture Group 1 is the chapter UUID
    # Capture Group 2 is the name (optional)
    MANGA_PATTERN = re.compile(r'(?:https://)?mangadex.org/title/([\w-]+)(?:/(\S+))?')

    async def _generate_chapter_webhook(self, uuid: str, url: str, discord_message: discord.Message):
        chapter_details = MAS.Chapter.get_chapter_details(uuid)
        if (chapter_details and chapter_details.manga_uuid):
            manga_details = MAS.Manga.get_manga_details(chapter_details.manga_uuid)
            return WT.build_chapter_webhook(discord_message, chapter_details, manga_details, url)

    async def _generate_chapter_webhooks(self, urls: List[re.Match], discord_message: discord.Message):
        webhooks = list()
        for url in urls:
            chapter_url = url.group(0)
            chapter_uuid = url.group(1)
            if webhook := await self._generate_chapter_webhook(chapter_uuid, chapter_url, discord_message):
                webhooks.append(webhook)
        return webhooks

    async def _generate_manga_webhook(self, uuid: str, discord_message: discord.Message):
        manga_details = MAS.Manga.get_manga_details(uuid)
        return WT.build_manga_webhook_full(discord_message, manga_details)

    async def _generate_manga_webhooks(self, uuids: List[str], discord_message: discord.Message):
        webhooks = list()
        for uuid in uuids:
            if webhook := await self._generate_manga_webhook(uuid, discord_message):
                webhooks.append(webhook)
        return webhooks

    async def _generate_manga_webhooks_from_re_matches(self, urls: List[re.Match], discord_message: discord.Message):
        # We can disregard the full url string here; it will be built again later.
        uuids = [u.group(1) for u in urls]
        return await self._generate_manga_webhooks(uuids, discord_message)
    
    async def process_message(self, message: discord.Message):
        """
        Call this method to get a list of webhooks (as json-encoded dicts) for all
        Mangadex-related URLs in a given Discord message.
        """
        webhooks = list()

        chapter_urls = self.CHAPTER_PATTERN.finditer(message.content)
        webhooks.extend(await self._generate_chapter_webhooks(chapter_urls, message))
        
        # Double regex is technically inefficient, but Discord message QPS ceiling rate helps.
        manga_urls = self.MANGA_PATTERN.finditer(message.content)
        webhooks.extend(await self._generate_manga_webhooks_from_re_matches(manga_urls, message))

        return webhooks

    @commands.Cog.listener("on_message")
    async def on_fluff_rss_message(self, message: discord.Message):
        # Ignore all messages from bots, including self.
        if message.author.bot:
            return

        # Only process messages in channels being observed.
        if message.channel.id not in settings.get(RSS_OBSERVED_CHANNELS):
            return

        # Create a list of all webhooks, and then send them.
        webhooks = list()
        webhooks.extend(await self.process_message(message))
        DAS.send_webhooks(webhooks)
