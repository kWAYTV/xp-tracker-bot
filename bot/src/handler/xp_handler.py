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

        try:

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

            # Set fields
            embed.add_field(name=f"{self.config.arrow_green_emoji_id} Level", value=f"`{level}` `({percentage})`", inline=True)
            embed.add_field(name=f"{self.config.arrow_blue_emoji_id} XP Earned ", value=f"`{earned_xp}`", inline=True)
            embed.add_field(name=f"{self.config.arrow_purple_emoji_id} XP Remaining", value=f"`{remaining_xp}`", inline=True)

            # Set the last data
            embed.set_thumbnail(url=avatar)
            embed.set_footer(text=f"CSGO Tracker", icon_url=self.config.csgo_tracker_logo)
            embed.timestamp = self.datetime_helper.get_current_timestamp()

            # Send the embed
            send_to = self.bot.get_channel(int(tracker_channel))
            await send_to.send(embed=embed)

        except Exception as e:
            self.logger.log("ERROR", f"Error while sending update: {e}")
            await self.logger.discord_log(f"Error while sending update: {e}")

    # Function to track the given user
    async def track_user(self, user):
        try:
        
            # Check if guild exists
            if not self.guild_manager.guild_exists(user.guild_id):
                try:
                    self.database.remove_user(user)
                    await self.logger.dm_user(user.discord_id, f"Removed {user.steam_id} ({user.discord_id}) from database because outdated guild id or channel id.")
                    self.logger.log("WARNING", f"Removed {user.steam_id} ({user.discord_id}) from database because outdated guild id or channel id.")
                    return await self.logger.discord_log(f"Removed {user.steam_id} ({user.discord_id}) from database because outdated guild id or channel id.")
                except Exception as e:
                    self.logger.log("ERROR", f"Error while removing user {user.steam_id} ({user.discord_id}) from database (outdated guild): {e}")
                    return await self.logger.discord_log(f"Error while removing user {user.steam_id} ({user.discord_id}) from database (outdated guild): {e}")

            # Get the tracker channel and the user xp data
            tracker_channel = await self.guild_manager.get_channel_by_guild(user.guild_id)
            new_level, new_xp, remaining_xp, percentage = await self.get_user_level_and_xp(user.steam_id)

            # Level up checks
            if new_level > user.current_level:  # Level up case
                earned_xp = new_xp
                # If user has reached the maximum level, notify him
                if new_level >= 40:
                    try:
                        await self.logger.dm_user(user.discord_id, "You have reached the maximum level (40). Claim your medal!")
                        self.logger.log("INFO", f"User {user.steam_id} ({user.discord_id}) has reached the maximum level (40).")
                        await self.logger.discord_log(f"User {user.steam_id} ({user.discord_id}) has reached the maximum level (40).")
                    except:
                        self.logger.log("INFO", f"User {user.steam_id} ({user.discord_id}) has reached the maximum level (40) but couldn't be notified.")
                        await self.logger.discord_log(f"User {user.steam_id} ({user.discord_id}) has reached the maximum level (40) but couldn't be notified.")
            else:
                earned_xp = new_xp - user.current_xp

            # Update the user data
            total_monthly, total_global = user.total_earned + earned_xp, user.global_earned + earned_xp
            self.database.update_user_level_and_xp(user.steam_id, new_level, new_xp, total_monthly, total_global)
            self.logger.log("XP", f"Changed: {user.steam_id} • Level: {new_level} • XP: {new_xp} • Total: {total_monthly} • Global: {total_global} • User: {user.discord_id} • Guild: {user.guild_id}")

            # Send an update if the user has updated
            if user.has_updated(new_level, new_xp):
                await self.send_update(tracker_channel, user, new_level, new_xp, remaining_xp, percentage, earned_xp)

        except Exception as e:
            self.logger.log("ERROR", f"Error checking {user.steam_id} ({user.discord_id}) tracking: {e}")

    # Loop to track users xp and level from database
    async def check_tracking(self):

        # Check if it's day 1 and the month earnings should be reset
        if self.database.should_reset():
            self.database.reset_total_earned()
            self.logger.log("INFO", "Resetting total earned xp for all users.")

        # Get all users and check them
        users = self.database.get_users()
        self.logger.log("INFO", f"Checking xp for {len(users)} users.")
        for user in users:
            for _ in range(2):
                await self.track_user(user)
                break
            await asyncio.sleep(4)