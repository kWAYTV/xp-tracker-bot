from src.util.logger import Logger
from src.helper.config import Config
from discord.ext import commands, tasks
from src.manager.guild_manager import GuildManager

class CleanDeletedGuildsLoop(commands.Cog):

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.logger = Logger()
        self.config = Config()
        self.guild_manager = GuildManager()
        self.clean_guilds_loop.start()

    @tasks.loop(minutes=5)  # Run every 5 minutes
    async def clean_guilds_loop(self):
        self.guild_manager.clean_guilds()
        
    @clean_guilds_loop.before_loop
    async def before_clean_guilds_loop(self):
        await self.wait_until_ready()  # Make sure the bot is ready before starting the loop

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(CleanDeletedGuildsLoop(bot))
    return Logger().log("INFO", "Clean deleted guilds loop loaded!")