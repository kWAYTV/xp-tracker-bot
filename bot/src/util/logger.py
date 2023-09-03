import discord, asyncio
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

    # Function to log messages to the console
    def log(self, type, message):
        color = self.log_types[type]
        now = datetime.now()
        current_time = now.strftime("%d/%m/%Y • %H:%M:%S")
        print(f"{Style.DIM}{current_time} • {Style.RESET_ALL}{Style.BRIGHT}{color}[{Style.RESET_ALL}{type}{Style.BRIGHT}{color}] {Style.RESET_ALL}{Style.BRIGHT}{Fore.WHITE}{message}")

    # Function to send logs to the discord channel
    async def discord_log(self, description: str):
        channel = self.bot.get_channel(self.config.logs_channel)
        if channel:
            embed = discord.Embed(title="CSGO Tracker", description=f"```{description}```")
            embed.set_thumbnail(url=self.config.csgo_tracker_logo)
            embed.set_image(url=self.config.rainbow_line_gif)
            embed.set_footer(text=f"CSGO Tracker • kwayservices.top", icon_url=self.config.csgo_tracker_logo)
            embed.timestamp = self.datetime_helper.get_current_timestamp()
            await channel.send(embed=embed)
        else:
            self.log("ERROR", f"Could not find the logs channel with id {self.config.logs_channel}")

    # Function to dm user by id
    async def dm_user(self, userid: int, message: str):
        dm_user = await self.bot.fetch_user(userid)
        if dm_user:
            await dm_user.send(message)
        else:
            self.log("ERROR", f"Could not find the user with id {userid}")
            await self.discord_log(f"Could not find the user with id {userid}")

    # Function to dm guild owner by guild id    
    async def dm_guild_owner(self, guildid: int, message: str):
        guild = self.bot.get_guild(guildid)
        if guild:
            owner = guild.owner
            if owner:
                await owner.send(message)
            else:
                self.log("ERROR", f"Could not find the owner of the guild with id {guildid}")
                await self.discord_log(f"Could not find the owner of the guild with id {guildid}")
        else:
            self.log("ERROR", f"Could not find the guild with id {guildid}")
            await self.discord_log(f"Could not find the guild with id {guildid}")

    # Function to dm every guild owner
    async def dm_guild_owners(self, message: str):
        guilds = self.bot.guilds
        self.log("INFO", f"Sending message to {len(guilds)} guild owners...")
        for guild in guilds:
            owner = guild.owner
            if owner:
                await owner.send(message)
                await asyncio.sleep(4)  # Use 'await' to pause execution
            else:
                self.log("ERROR", f"Could not find the owner of the guild with id {guild.id}")
                await self.discord_log(f"Could not find the owner of the guild with id {guild.id}")