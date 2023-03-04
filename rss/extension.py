
from discord.ext import commands

from .mangadex.cog import MangaDex as MangaDexCog
from .yurisquad.dynasty_cog import Dynasty as DynastyCog

async def setup(bot: commands.Bot):
    await bot.add_cog(MangaDexCog(bot))
    await bot.add_cog(DynastyCog(bot))