import discord
from os import system, name
from datetime import datetime
from discord.ext import commands
from colorama import Fore, Style
from src.helper.config import Config
from src.helper.datetime import DateTime

class Logger:

    def __init__(self, bot: commands.Bot = None):
        self.bot = bot
        self.config = Config()
        self.datetime_helper = DateTime()
        # Set the colors for the logs
        self.log_types = {
            "INFO": Fore.CYAN,
            "SUCCESS": Fore.GREEN,
            "OK": Fore.GREEN,
            "XP": Fore.GREEN,
            "WARNING": Fore.YELLOW,
            "SLEEP": Fore.YELLOW,
            "ERROR": Fore.RED,
            "BAD": Fore.RED,
            "INPUT": Fore.BLUE,
            "RATELIMIT": Fore.YELLOW,
        }

    # Clear console function
    def clear(self):
        system("cls" if name in ("nt", "dos") else "clear")

    # Function to send logs to the discord channel
    async def discord_log(self, description: str):
        channel = self.bot.get_channel(self.config.logs_channel)
        embed = discord.Embed(title="CSGO Tracker", description=f"```{description}```")
        embed.set_thumbnail(url=self.config.csgo_tracker_logo)
        embed.set_footer(text=f"CSGO Tracker • discord.gg/kws", icon_url=self.config.csgo_tracker_logo)
        embed.timestamp = self.datetime_helper.get_current_timestamp()
        await channel.send(embed=embed)

    # Function to log messages to the console
    def log(self, type, message):
        color = self.log_types[type]
        now = datetime.now()
        current_time = now.strftime("%d/%m/%Y • %H:%M:%S")
        print(f"{Style.DIM}{current_time} • {Style.RESET_ALL}{Style.BRIGHT}{color}[{Style.RESET_ALL}{type}{Style.BRIGHT}{color}] {Style.RESET_ALL}{Style.BRIGHT}{Fore.WHITE}{message}")