
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
    
    async def process_message(self, message: discord.Message):
        """
        Call this method to get a list of webhooks (as json-encoded dicts) for all
        Mangadex-related URLs in a given Discord message.
        """
        chapter_urls = self.CHAPTER_PATTERN.finditer(message.content)
        return await self._generate_chapter_webhooks(chapter_urls, message)

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
