from src.util.logger import Logger
from src.helper.config import Config
from discord.ext import commands, tasks
from src.handler.medal_handler import MedalHandler

class CleanImagesLoop(commands.Cog):

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.logger = Logger()
        self.config = Config()
        self.medal_handler = MedalHandler()
        self.clean_images.start()

    # Clean the images folder every 10 minutes
    @tasks.loop(seconds=600)
    async def clean_images(self):
        await self.medal_handler.delete_all_images()

    @clean_images.before_loop
    async def before_clean_images(self) -> None:
        return await self.bot.wait_until_ready()

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(CleanImagesLoop(bot))
    return Logger().log("INFO", "Clean api images loop loaded!")