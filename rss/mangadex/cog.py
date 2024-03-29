
import discord
from discord.ext import commands

from config import settings, RSS_OBSERVED_CHANNELS

from ..shared import discord_api_service as DAS
from ..shared import beautifulsoup_service as BSS

import re
from typing import List


class MangaDex(commands.Cog, name="MangaDex"):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # Pattern to match MangaDex chapter URLs of the forms:
    # [https://]mangadex.org/chapter/<UUID>[/page#]
    # Where the URL protocol and page number are optional.
    # Capture Group 1 is the chapter UUID
    # Capture Group 2 is the page number (optional)
    CHAPTER_PATTERN = re.compile(r'(?:https|http)://mangadex.org/chapter/([\w-]+)(?:/(\d+))?')

    # Pattern to match MangaDex manga URLs of the forms:
    # [https://]mangadex.org/title/<UUID>[/name]
    # Where the URL protocol and human-readable name are optional.
    # Capture Group 1 is the chapter UUID
    # Capture Group 2 is the name (optional)
    MANGA_PATTERN = re.compile(r'(?:https|http)://?mangadex.org/title/([\w-]+)(?:/(\S+))?')

    # The yellow-orangish colour used for Mangadex embed previews
    MANGADEX_COLOUR = 15102792

    async def _generate_chapter_webhooks(self, urls: List[re.Match]):
        metadata = list()
        for url in urls:
            chapter_url = url.group(0)
            chapter_og_metadata = BSS.fetch_page_metadata(chapter_url)
            if chapter_og_metadata:
                chapter_og_metadata.colour = self.MANGADEX_COLOUR
                metadata.append(chapter_og_metadata)
        return metadata

    async def _generate_manga_webhooks(self, urls: List[str]):
        metadata = list()
        for url in urls:
            manga_og_metadata = BSS.fetch_page_metadata(url)
            if manga_og_metadata:
                manga_og_metadata.colour = self.MANGADEX_COLOUR
                metadata.append(manga_og_metadata)
        return metadata

    async def _generate_manga_webhooks_from_re_matches(self, urls: List[re.Match]):
        urls = [u.group(0) for u in urls]
        return await self._generate_manga_webhooks(urls)

    async def process_message(self, message: discord.Message):
        """
        Call this method to get a list of webhooks (as json-encoded dicts) for all
        Mangadex-related URLs in a given Discord message.
        """
        metadata = list()

        chapter_urls = self.CHAPTER_PATTERN.finditer(message.content)
        metadata.extend(await self._generate_chapter_webhooks(chapter_urls))

        # Double regex is technically inefficient, but Discord message QPS ceiling rate helps.
        manga_urls = self.MANGA_PATTERN.finditer(message.content)
        metadata.extend(await self._generate_manga_webhooks_from_re_matches(manga_urls))

        return metadata

    @commands.Cog.listener("on_message")
    async def on_fluff_rss_message(self, message: discord.Message):
        # Ignore all messages from bots, including self.
        if message.author.bot:
            return

        # Only process messages in channels being observed.
        if message.channel.id not in settings.get(RSS_OBSERVED_CHANNELS):
            return

        # Create a list of all webhooks, and then send them.
        metadata = await self.process_message(message)
        webhooks = [DAS.generate_webhook(message, m) for m in metadata]
        DAS.send_webhooks(webhooks)
