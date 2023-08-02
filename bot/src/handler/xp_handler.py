import requests, discord, asyncio
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

    # Function to create level progress bar
    @staticmethod
    def create_progress_bar(remaining_xp, total_xp=5000, bar_length=20):
        progress = (total_xp - remaining_xp) / total_xp
        filled_length = int(bar_length * progress)
        bar = '▓' * filled_length + '░' * (bar_length - filled_length)
        return bar

    # Function to get the time remaining for level 40
    def get_time_remaining_for_40(self, current_level, current_level_xp, average_xp_per_game=117):
        remaining_levels = 40 - current_level
        total_xp_required_for_remaining_levels = remaining_levels * 5000
        remaining_xp_for_current_level = 5000 - current_level_xp
        total_xp_required = total_xp_required_for_remaining_levels + remaining_xp_for_current_level
        total_games_required = total_xp_required / average_xp_per_game
        remaining_time_in_minutes = total_games_required * 420 / 60

        days, remainder_minutes = divmod(remaining_time_in_minutes, 1440) # 1440 minutes in a day
        hours, minutes = divmod(remainder_minutes, 60) # 60 minutes in an hour

        time_string = ""
        if days > 0:
            time_string += f"{int(days)} day(s) "
        if hours > 0:
            time_string += f"{int(hours)} hour(s) "
        if minutes > 0:
            time_string += f"{int(minutes)} minute(s)"

        return time_string.strip(), f"{total_games_required:.2f}"

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
    async def send_update(self, tracker_channel, user, new_level, remaining_xp, percentage, earned_xp, total_monthly):

        try:

            name = str(user.steam_id)
            avatar = None

            # Get user info
            success, steamid64, name, avatar = self.checker.get_persona(user.steam_id)
            xp_bar = self.create_progress_bar(remaining_xp)
            time_for_40, games_required = self.get_time_remaining_for_40(new_level, remaining_xp)

            # Set bot icon as avatar if it's None
            if avatar is None:
                avatar = self.config.csgo_tracker_logo
            
            # If the xp changed, send an update
            embed = discord.Embed(title=f"`{name}`'s XP Change detected!", url=f"https://steamcommunity.com/profiles/{user.steam_id}", color=0x08dbf8c)
            embed.set_author(name=f"XP Tracker", icon_url=self.config.csgo_tracker_logo, url="https://kwayservices.top")

            # Set fields
            embed.add_field(name=f"{self.config.arrow_green_emoji_id} Level", value=f"`{new_level}` `({percentage})`", inline=True)
            embed.add_field(name=f"{self.config.arrow_blue_emoji_id} XP Earned ", value=f"`{earned_xp}`", inline=True)
            embed.add_field(name=f"{self.config.arrow_purple_emoji_id} XP Remaining", value=f"`{remaining_xp}`", inline=True)

            # Add progress bar & time for 40
            embed.add_field(name=f"{self.config.arrow_pink_emoji_id} Games remaining", value=f"`{games_required} games`", inline=True)
            embed.add_field(name=f"{self.config.arrow_white_emoji_id} Time remaining", value=f"`{time_for_40}`", inline=True)
            embed.add_field(name=f"{self.config.arrow_yellow_emoji_id} Monthly XP", value=f"`{total_monthly}`", inline=True)
            embed.add_field(name=f"{self.config.green_tick_emoji_id} XP Progress", value=f"`{xp_bar} ({percentage})`", inline=True)

            # Set the last data
            embed.set_thumbnail(url=avatar)
            embed.set_image(url=self.config.rainbow_line_gif)
            embed.set_footer(text=f"CSGO Tracker • Warning! The weekly xp bonus is not considered.", icon_url=self.config.csgo_tracker_logo)
            embed.timestamp = self.datetime_helper.get_current_timestamp()

            # Send the embed
            send_to = self.bot.get_channel(int(tracker_channel))
            await send_to.send(embed=embed)

        except Exception as e:
            self.logger.log("ERROR", f"While sending update: {e}")
            await self.logger.discord_log(f"While sending update: {e}")

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

            # Send an update if the user has updated
            if user.has_updated(new_level, new_xp):
                await self.send_update(tracker_channel, user, new_level, remaining_xp, percentage, earned_xp, total_monthly)
                self.logger.log("XP", f"Changed: {user.steam_id} • Level: {new_level} • XP: {new_xp} • Total: {total_monthly} • Global: {total_global} • User: {user.discord_id} • Guild: {user.guild_id}")

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
        
        # Check the users
        for user in users:
            await self.track_user(user)
            await asyncio.sleep(3)