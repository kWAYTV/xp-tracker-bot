import requests, discord, asyncio, time
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
    def create_per_level_progress_bar(remaining_xp, total_xp=5000, bar_length=12):
        progress = (total_xp - remaining_xp) / total_xp
        filled_length = int(bar_length * progress)
        bar = '▰' * filled_length + '▱' * (bar_length - filled_length)
        return bar
    
    # Function to create max level progress bar
    @staticmethod
    def create_progress_bar_to_40(current_level, current_level_xp, max_level=40, total_xp_per_level=5000, bar_length=12):
        total_required_xp = max_level * total_xp_per_level
        total_current_xp = (current_level * total_xp_per_level) + current_level_xp
        progress = total_current_xp / total_required_xp
        filled_length = int(bar_length * progress)
        bar = '▰' * filled_length + '▱' * (bar_length - filled_length)
        percentage = progress * 100
        return bar, f"{percentage:.2f} %"

    # Function to calculate games to level up
    def calculate_games_to_level_up(self, current_xp, required_xp, average_xp_per_game):
        # Calculating the total XP needed to reach the next level
        xp_needed = required_xp - current_xp

        # Calculating the number of games needed to level up
        games_needed = xp_needed / average_xp_per_game

        return games_needed

    # Function to calculate the expected time to level up
    def calculate_expected_time_to_level_up(self, games_needed, average_game_duration_minutes):
        # Calculating the expected time in minutes
        expected_time_minutes = games_needed * average_game_duration_minutes

        # Calculating the expected time in hours
        expected_time_hours = expected_time_minutes / 60

        # Leave only 2 decimal places and return the result
        return round(expected_time_hours, 2)

    # Function to format the remaining time
    def format_remaining_time(self, total_hours):
        # Convert to days, hours, and minutes
        days, remainder_hours = divmod(total_hours, 24)
        hours, remainder_minutes = divmod(remainder_hours * 60, 60)

        days = round(days)  # Round to the nearest integer
        hours = round(hours)  # Round to the nearest integer
        remainder_minutes = round(remainder_minutes)  # Round to the nearest integer

        # Format the result
        result = ''
        if days:
            result += f'{days} day(s) '
        if hours or days: # include hours if there are days even if hours is 0
            result += f'{hours} hour(s) '
        result += f'{remainder_minutes} minute(s)'

        # Strip any trailing space and return the result
        return result.strip()

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

            # Create the current level progress bar
            xp_bar = self.create_per_level_progress_bar(remaining_xp)

            # Create the max level progress bar
            max_level_xp_bar, max_percentage = self.create_progress_bar_to_40(user.current_level, user.current_xp)

            # Calculate the remaining games & time for the next level
            games_needed_next_level = self.calculate_games_to_level_up(user.current_xp, 5000, 117)
            # Round the games needed to the nearest integer
            games_needed_next_level = round(games_needed_next_level)
            expected_time_hours_next_level = self.calculate_expected_time_to_level_up(games_needed_next_level, 7)

            # Convert the hours to Ex: 1 day(s), 2 hour(s), 3 minute(s) 
            expected_time = self.format_remaining_time(expected_time_hours_next_level)

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
            embed.add_field(name=f"{self.config.arrow_yellow_emoji_id} Monthly XP", value=f"`{total_monthly}`", inline=True)
            embed.add_field(name=f"{self.config.arrow_pink_emoji_id} Games needed", value=f"`{games_needed_next_level} games`", inline=True)
            embed.add_field(name=f"{self.config.arrow_white_emoji_id} Next level in", value=f"`{expected_time}`", inline=True)
            embed.add_field(name=f"{self.config.loading_green_emoji_id} Current level progress", value=f"`{xp_bar} ({percentage})`", inline=True)
            embed.add_field(name=f"{self.config.loading_green_emoji_id} Max level progress", value=f"`{max_level_xp_bar} ({max_percentage})`", inline=True)

            # Set the last data
            embed.set_thumbnail(url=avatar)
            embed.set_image(url=self.config.rainbow_line_gif)
            embed.set_footer(text=f"CSGO Tracker • Warning! The weekly xp bonus is not considered.", icon_url=self.config.csgo_tracker_logo)
            embed.timestamp = self.datetime_helper.get_current_timestamp()

            # Send the embed
            try:
                send_to = self.bot.get_channel(int(tracker_channel))
                await send_to.send(embed=embed)
            except Exception as e:
                self.logger.log("ERROR", f"Couldn't send update to guild {user.guild_id} channel {tracker_channel}: {e}. Removing it from database!")
                await self.logger.discord_log(f"Couldn't send update to guild {user.guild_id} channel {tracker_channel}: {e}. Removing it from database!")
                await self.logger.dm_guild_owner(user.guild_id, f"Couldn't send update to guild {user.guild_id} channel {tracker_channel}: {e}. Removing it from database! Please, re-set your server's tracking channel.")
                self.guild_manager.remove_guild(user.guild_id)
                return

        except Exception as e:
            self.logger.log("ERROR", f"While sending update: {e}")
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
        if not len(users) >= 1:
            return await asyncio.sleep(3)

        self.logger.log("INFO", f"Checking xp for {len(users)} users.")
        
        # Check the users
        for user in users:
            await self.track_user(user)
            await asyncio.sleep(3)