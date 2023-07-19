# Imports
import discord, os
from colorama import Fore
from discord.ext import commands
from src.util.logger import Logger
from src.helper.config import Config
from src.manager.xp_manager import XpManager
from src.manager.file_manager import FileManager
from src.manager.timeout_manager import TimeoutManager

# Define the bot & load the commands, events and loops
class Bot(commands.Bot):
    def __init__(self) -> None:
        self.logger = Logger()
        self.file_manager = FileManager()
        self.xp_manager = XpManager()
        self.timeout_manager = TimeoutManager()
        super().__init__(command_prefix=Config().bot_prefix, help_command=None, intents=discord.Intents.all())

    # Function to load the extensions
    async def setup_hook(self) -> None:
        self.logger.clear()
        self.logger.log("INFO", f"Starting bot...")

        # Check for file inputs
        self.file_manager.check_input()
        self.logger.clear()

        # Load the cogs
        self.logger.log("INFO", "Loading cogs...")
        for filename in os.listdir("./src/cogs/commands"):
            if filename.endswith(".py") and not filename.startswith("_"):
                await self.load_extension(f"src.cogs.commands.{filename[:-3]}")
        self.logger.clear()

        # Load the events
        self.logger.log("INFO", "Loading events...")
        for filename in os.listdir("./src/cogs/events"):
            if filename.endswith(".py") and not filename.startswith("_"):
                await self.load_extension(f"src.cogs.events.{filename[:-3]}")
        self.logger.clear()

        # Load the loops
        self.logger.log("INFO", "Loading loops...")
        for filename in os.listdir("./src/cogs/loops"):
            if filename.endswith(".py") and not filename.startswith("_"):
                await self.load_extension(f"src.cogs.loops.{filename[:-3]}")
        self.logger.clear()

        # Done!
        self.logger.log("INFO", f"Setup completed!")

# Define the client
bot = Bot()

# Run the bot
if __name__ == "__main__":
    try:
        bot.run(Config().discord_token)
    except KeyboardInterrupt:
        print(f"{Fore.MAGENTA}>{Fore.WHITE} Powering off the bot...")
        exit()