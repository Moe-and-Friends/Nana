
import discord
from discord.ext import commands

from .mangadex.cog import MangaDex as MangaDexCog

async def setup(bot: commands.Bot):
    await bot.add_cog(MangaDexCog(bot))