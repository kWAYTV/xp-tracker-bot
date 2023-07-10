import discord
from datetime import datetime
from src.util.logger import Logger
from src.helper.config import Config
from discord.ext import commands, tasks
from src.handler.queue_handler import QueueHandler

class UpdateQueueLoop(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.logger = Logger()
        self.config = Config()
        self.queue_handler = QueueHandler()
        self.update_queue_embed.start()

    # Update queue embed message
    @tasks.loop(seconds=45)
    async def update_queue_embed(self):

        if not self.config.queue_embed_switch: return

        # Fetch the message and channel
        try:
            queue_channel = self.bot.get_channel(Config().queue_embed_channel_id)
            queue_message = await queue_channel.fetch_message(Config().queue_embed_message_id)
        except Exception as e:
            self.logger.log("ERROR", f"Failed to fetch queue embed message, use the /queue_embed command and wait for the queue to update. Error: {e}")
            return

        # Get the queue data and length
        data = self.queue_handler.get_queue_data()
        length = self.queue_handler.get_queue_length()

        # Set the embed description
        if length > 0:
            description = "`User`/`ID`\n"
            for index, order in enumerate(data):
                steamid64 = order['steamid64']
                requested_by = order['requested_by']
                emoji = self.config.loading_green_emoji_id if index == 0 else self.config.loading_red_emoji_id
                description = description + f" > • {emoji} <@{requested_by}> • `{steamid64}`\n"
        else:
            description = f"{self.config.discord_emoji_id} There's no orders in queue."

        # Create the embed
        embed = discord.Embed(title="📝 CSGO Queue.", description=description, color=0xb34760)
        embed.set_footer(text=f"Total: {length} • Last updated: {datetime.utcnow().strftime('%H:%M:%S')}", icon_url=self.config.csgo_tracker_logo)
        embed.set_thumbnail(url=self.config.csgo_tracker_logo)

        # Edit the message
        await queue_message.edit(embed=embed)

    # Force update queue embed message
    async def force_update_queue_embed(self) -> None:
        await self.update_queue_embed()

    @update_queue_embed.before_loop
    async def before_update_queue_embed(self) -> None:
        return await self.bot.wait_until_ready()

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(UpdateQueueLoop(bot))
    return Logger().log("INFO", "Update queue loop loaded!")
