import asyncio
from src.util.logger import Logger
from src.helper.config import Config
from discord.ext import commands, tasks
from src.handler.xp_handler import XpHandler

class XpTrackLoop(commands.Cog):

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.config = Config()
        self.xp_handler = XpHandler(self.bot)
        self.xp_track.start()

    # Check xp
    @tasks.loop(seconds=Config().checker_interval)
    async def xp_track(self):
        await self.xp_handler.check_tracking()

    @xp_track.before_loop
    async def before_xp_track(self) -> None:
        return await self.bot.wait_until_ready()

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(XpTrackLoop(bot))
    return Logger().log("INFO", "XP Tracker loop loaded!")