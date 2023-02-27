import asyncio
import discord
from discord.ext.commands import Bot, ExtensionAlreadyLoaded

import config
from config import settings

intents = discord.Intents.default()
intents.message_content = True
bot = Bot("nana", intents = intents)

EXTENSIONS = [
    "rss.cog"
]

async def load_extensions():
    for extension in EXTENSIONS:
        try:
            await bot.load_extension(extension)
        except ExtensionAlreadyLoaded:
            await bot.reload_extension(extension)

@bot.event
async def on_ready():
    await load_extensions()

bot.run(settings.get(config.DISCORD_TOKEN))
