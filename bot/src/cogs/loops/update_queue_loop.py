from src.util.logger import Logger
from src.helper.config import Config
from discord.ext import commands, tasks
from src.handler.queue_handler import QueueHandler

class UpdateQueueLoop(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.logger = Logger()
        self.config = Config()
        self.queue_handler = QueueHandler(bot)
        self.update_queue_embed.start()

    # Update queue embed message
    @tasks.loop(seconds=Config().update_embeds_delay)
    async def update_queue_embed(self):
        await self.queue_handler.update_queue_embed()

    # Force update queue embed message
    async def force_update_queue_embed(self) -> None:
        await self.update_queue_embed()

    @update_queue_embed.before_loop
    async def before_update_queue_embed(self) -> None:
        return await self.bot.wait_until_ready()

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(UpdateQueueLoop(bot))
    return Logger().log("INFO", "Update queue loop loaded!")
