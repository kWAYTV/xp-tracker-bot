from src.util.logger import Logger
from src.helper.config import Config
from discord.ext import commands, tasks
from src.handler.leaderboard_handler import LeaderboardHandler

class UpdateLeaderboardLoop(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.logger = Logger()
        self.config = Config()
        self.update_leaderboard_embed.start()
        self.leaderboard_handler = LeaderboardHandler(bot)

    # Update leaderboard embed message
    @tasks.loop(seconds=Config().checker_interval)  # you can change this to any value you like
    async def update_leaderboard_embed(self):
        await self.leaderboard_handler.update_leaderboard_embed()

    # Force update leaderboard embed message
    async def force_update_leaderboard_embed(self) -> None:
        await self.update_leaderboard_embed()

    @update_leaderboard_embed.before_loop
    async def before_update_leaderboard_embed(self) -> None:
        return await self.bot.wait_until_ready()

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(UpdateLeaderboardLoop(bot))
    return Logger().log("INFO", "Update leaderboard loop loaded!")
