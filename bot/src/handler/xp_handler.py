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
        self.checker = Checker()
        self.database = XpManager()
        self.logger = Logger(self.bot)
        self.datetime_helper = DateTime()
        self.session = requests.Session()
        self.guild_manager = GuildManager()
        self.session.headers.update({"User-Agent": "kWS-Auth"})

    # Function to get the user level and xp
    async def get_user_level_and_xp(self, id):

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
        embed = discord.Embed(title=f"`{name}`'s XP Change detected!", url=f"https://steamcommunity.com/profiles/{user.steam_id}", color=0x08dbf8c)

        embed.set_author(name=f"XP Tracker", icon_url=self.config.csgo_tracker_logo, url="https://kwayservices.top")
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

        if self.database.should_reset():
            actual_month = datetime.today().month
            self.database.reset_total_earned(actual_month)
            self.logger.log("INFO", "Resetting total earned xp for all users.")

        users = self.database.get_users()
        amount = len(users)
        self.logger.log("INFO", f"Checking xp for {amount} users.")
        for user in users:
            for i in range(3):
                try:
                    if not self.guild_manager.guild_exists(user.guild_id):
                        await self.logger.dm_user(user.discord_id, f"Removing {user.steam_id} ({user.discord_id}) from database because outdated guild id or channel id.")
                        self.logger.log("WARNING", f"Removing {user.steam_id} ({user.discord_id}) from database because outdated guild id or channel id.")
                        await self.logger.discord_log(f"Removing {user.steam_id} ({user.discord_id}) from database because outdated guild id or channel id.")
                        self.database.remove_user(user)
                        break
                    tracker_channel = await self.guild_manager.get_channel_by_guild(user.guild_id)
                    new_level, new_xp, remaining_xp, percentage = await self.get_user_level_and_xp(user.steam_id)
                    if new_level > user.current_level:  # Level up case
                        earned_xp = new_xp
                        if new_level >= 40:
                            await self.logger.dm_user(user.discord_id, "You have reached the maximum level (40). Claim your medal!")
                            self.logger.log("INFO", f"User {user.steam_id} ({user.discord_id}) has reached the maximum level (40).")
                            await self.logger.discord_log(f"User {user.steam_id} ({user.discord_id}) has reached the maximum level (40).")
                    else:
                        earned_xp = new_xp - user.current_xp
                    if user.has_updated(new_level, new_xp):
                        await self.send_update(tracker_channel, user, new_level, new_xp, remaining_xp, percentage, earned_xp)
                        total_monthly, total_global = user.total_earned + earned_xp, user.global_earned + earned_xp
                        self.database.update_user_level_and_xp(user.steam_id, new_level, new_xp, total_monthly, total_global)
                        self.logger.log("XP", f"Updating {user.steam_id} to level {new_level} and xp {new_xp}. Total earned: {total_monthly} Global earned: {total_global} Guild: {user.guild_id}")
                except Exception as e:
                    self.logger.log("ERROR", f"Error checking tracking: {e}")
                    continue
                break
            await asyncio.sleep(5)