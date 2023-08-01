import asyncio, discord
from queue import Queue
from discord.ext import commands
from src.util.logger import Logger
from src.helper.config import Config
from src.steam.checker import Checker
from src.helper.datetime import DateTime
from concurrent.futures import ThreadPoolExecutor

class QueueHandler:
    def __init__(self, bot: commands.Bot = None):
        self.bot = bot
        self.queue = Queue()
        self.logger = Logger()
        self.config = Config()
        self.checker = Checker()
        self.datetime_helper = DateTime()
        self.proccessing = False
        self.check_results = {}

    # Pushes an order to the queue
    def push_order(self, order):
        self.queue.put(order)

    # Returns the queue length
    def get_queue_length(self):
        return self.queue.qsize()

    # Returns the queue data as a list
    def get_queue_data(self):
        return self.queue.queue
    
    # Return if the queue is being processed
    def is_queue_processing(self):
        return self.proccessing

    # Processes the queue
    async def process_queue(self):
        try:

            while not self.queue.empty():
                self.proccessing = True
                order = self.queue.get()
                steamid64 = order['steamid64']
                queue_id = order['queue_id']
                requested_by = order['requested_by']

                self.logger.log("INFO", f"Processing order {queue_id} from user {requested_by} for Steam ID: {steamid64}.")

                # Use asyncio's run_in_executor to run blocking functions in a thread
                with ThreadPoolExecutor(max_workers=int(1)) as executor:
                    for _ in range(int(1)):
                        success, result = await asyncio.get_event_loop().run_in_executor(executor, self.checker.get_player_info, steamid64, queue_id)

                self.check_results[steamid64] = (success, result)

                # Remove the completed order from the queue
                self.queue.task_done()
                await asyncio.sleep(1)

            self.proccessing = False
            
        except Exception as e:
            self.proccessing = False
            self.logger.log("ERROR", f"Error processing queue: {e}")

    # Function to get the results of a check
    async def get_check_results(self, steamid64):
        results = self.check_results.get(steamid64)
        return results  # If the check was not done yet, return (None, None)

    # Checks if the queue is empty and if it's not empty nor being processed, processes it
    async def force_check_start(self):
        try:
            if not self.queue.empty() and not self.proccessing:
                await self.process_queue()
        except Exception as e:
            self.proccessing = False
            self.logger.log("ERROR", f"Error force-checking the queue: {e}")

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
        data = self.get_queue_data()
        length = self.get_queue_length()

        # Set the embed description
        if length > 0:
            description = "`User`/`ID`\n"
            for index, order in enumerate(data, start=1):
                steamid64, requested_by = order['steamid64'], order['requested_by']
                emoji = self.config.loading_green_emoji_id if index == 1 else self.config.loading_red_emoji_id
                description = description + f" > • {emoji} <@{requested_by}> • `{steamid64}`\n"
        else:
            description = f"{self.config.discord_emoji_id} There's no orders in queue."

        # Create the embed
        embed = discord.Embed(title="📝 CSGO Queue.", description=description, color=0xb34760)
        embed.set_footer(text=f"Total: {length} • Last updated: {self.datetime_helper.get_current_timestamp().strftime('%H:%M:%S')}", icon_url=self.config.csgo_tracker_logo)
        embed.set_thumbnail(url=self.config.csgo_tracker_logo)
        embed.set_image(url=self.config.rainbow_line_gif)

        # Edit the message
        await queue_message.edit(embed=embed)