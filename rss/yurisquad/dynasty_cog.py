import discord
from discord.ext import commands

from config import settings, RSS_OBSERVED_CHANNELS

from ..shared import discord_api_service as DAS
from ..shared import beautifulsoup_service as BSS

import re
from typing import List

class Dynasty(commands.Cog, name="Dynasty"):

    """
    Pattern to match Dynasty Readers.
    Group 0: Total match
    Group 1: "series" or "chapters"
    Group 2: Series/Chapters reference section.
    """
    DYNASTY_PATTERN = re.compile(r"(?:https|http)://dynasty-scans\.com/(chapters|series)/([\w-]+)")

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def process_message(self, message: discord.Message):
        webhooks = list()
        # Find and extract all the URLs in the message
        dynasty_matches = self.DYNASTY_PATTERN.finditer(message.content)
        dynasty_urls = [match.group(0) for match in dynasty_matches]
        # Scrape the title tag metadata off the headers
        for url in dynasty_urls:
            metadata = BSS.fetch_page_metadata(url) 
            metadata.colour = 8514 # Dynasty Blue
            webhooks.append(DAS.generate_webhook(message, metadata))
        return webhooks

    @commands.Cog.listener("on_message")
    async def on_fluff_rss_message(self, message: discord.Message):
        # Ignore all messages from bots, including self.
        if message.author.bot:
            return

        # Only process messages in channels being observed.
        if message.channel.id not in settings.get(RSS_OBSERVED_CHANNELS):
            return
        
        webhooks = list()
        webhooks.extend(await self.process_message(message))
        DAS.send_webhooks(webhooks)