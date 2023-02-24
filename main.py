import discord
from discord.ext.commands import Bot, ExtensionAlreadyLoaded

from rss.cog import RssCog
from rss.cog import MangaDex

import config
from config import settings

intents = discord.Intents.default()
intents.message_content = True
bot = Bot("nana", intents = intents)

@bot.event
async def on_ready():
    try:
        await bot.add_cog(RssCog(bot)) # Add Fluff-RSS scanner
        await bot.add_cog(MangaDex(bot)) # Fluff-RSS sub bot for MangaDex
    except ExtensionAlreadyLoaded:
        pass

bot.run(settings.get(config.DISCORD_TOKEN))
