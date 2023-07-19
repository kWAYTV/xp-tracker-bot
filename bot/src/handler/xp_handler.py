import requests, discord, asyncio
from datetime import datetime
from discord.ext import commands
from src.util.logger import Logger
from src.helper.config import Config
from src.steam.checker import Checker
from src.helper.datetime import DateTime
from src.manager.xp_manager import XpManager
from src.manager.guild_manager import GuildManager

class XpHandler:
    def __init__(self, bot: commands.Bot = None):
        self.bot = bot
        self.config = Config()
        self.logger = Logger()
        self.checker = Checker()
        self.database = XpManager()
        self.datetime_helper = DateTime()
        self.session = requests.Session()
        self.guild_manager = GuildManager()
        self.session.headers.update({"User-Agent": "kWS-Auth"})

    # Function to get the user level and xp
    def get_user_level_and_xp(self, id):

        success, steamid64, nickname, avatar = self.checker.get_persona(id)

        if not success:
            return False, f"The id `{id}` is not a valid ID.", None, None

        url = f"https://checker.kwayservices.top/steam/get/levels?id={steamid64}"

        response = self.session.get(url)
        json = response.json()

        if not json["success"]:
            return False, f"The id `{id}` is not a valid ID."
        
        current_level = json["data"]["data"]["current_level"]
        current_xp = json["data"]["data"]["current_xp"]
        percentage = json["data"]["data"]["level_percentage"]
        remaining_xp = json["data"]["data"]["remaining_xp"]

        return current_level, current_xp, remaining_xp, percentage

    # Function to send an update to the tracker channel
    async def send_update(self, tracker_channel, user, level, xp, remaining_xp, percentage, earned_xp):

        name = str(user.steam_id)
        avatar = None

        # Get user info
        success, steamid64, name, avatar = self.checker.get_persona(user.steam_id)

        # Set bot icon as avatar if it's None
        if avatar is None:
            avatar = self.config.csgo_tracker_logo
        
        # If the xp changed, send an update
        if user.current_xp != xp:
            embed = discord.Embed(title=f"`{name}`'s XP Change detected!", url=f"https://steamcommunity.com/profiles/{user.steam_id}", color=0x08dbf8c)

            embed.set_author(name=f"Tracker", icon_url=self.config.csgo_tracker_logo, url="https://kwayservices.top")
            embed.add_field(name=f"{self.config.arrow_green_emoji_id} Level", value=f"`{level}` `({percentage})`", inline=True)
            embed.add_field(name=f"{self.config.arrow_blue_emoji_id} XP Earned ", value=f"`{earned_xp}`", inline=True)
            embed.add_field(name=f"{self.config.arrow_purple_emoji_id} XP Remaining", value=f"`{remaining_xp}`", inline=True)

            embed.set_thumbnail(url=avatar)
            embed.set_footer(text=f"CSGO Tracker", icon_url=self.config.csgo_tracker_logo)
            embed.timestamp = self.datetime_helper.get_current_timestamp()

            send_to = self.bot.get_channel(int(tracker_channel))
            await send_to.send(embed=embed)

    # Loop to track users xp and level from database
    async def check_tracking(self):
        users = self.database.get_users()

        if self.database.should_reset():
            actual_month = datetime.today().month
            self.database.reset_total_earned(actual_month)
            self.logger.log("INFO", "Resetting total earned xp for all users.")

        for user in users:
            for i in range(3):
                tracker_channel = self.guild_manager.get_channel_by_guild(user.guild_id)
                try:
                    new_level, new_xp, remaining_xp, percentage = self.get_user_level_and_xp(user.steam_id)
                    if new_level > user.current_level:  # Level up case
                        earned_xp = new_xp
                    else:
                        earned_xp = new_xp - user.current_xp
                except Exception as e:
                    self.logger.log("ERROR", f"Error checking tracking: {e}")
                    continue
                if user.has_updated(new_level, new_xp):
                    await self.send_update(tracker_channel, user, new_level, new_xp, remaining_xp, percentage, earned_xp)
                    total_earned = user.total_earned + earned_xp
                    self.database.update_user_level_and_xp(user.steam_id, new_level, new_xp, total_earned)
                break
            await asyncio.sleep(3)