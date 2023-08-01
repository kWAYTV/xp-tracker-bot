import discord
from discord.ext import commands
from src.util.logger import Logger
from src.helper.config import Config
from src.steam.checker import Checker
from src.helper.datetime import DateTime
from src.manager.xp_manager import XpManager

class LeaderboardHandler:
    def __init__(self, bot: commands.Bot = None):
        self.bot = bot
        self.logger = Logger()
        self.config = Config()
        self.checker = Checker()
        self.xp_manager = XpManager()
        self.datetime_helper = DateTime()

    async def update_leaderboard_embed(self):
        if not self.config.leaderboard_embed_switch: return

        # Fetch the message and channel
        try:
            leaderboard_channel = self.bot.get_channel(Config().leaderboard_embed_channel_id)
            leaderboard_message = await leaderboard_channel.fetch_message(Config().leaderboard_embed_message_id)
        except Exception as e:
            self.logger.log("ERROR", f"Failed to fetch leaderboard embed message, use the /leaderboard_embed command and wait for the leaderboard to update. Error: {e}")
            return

        # Get the leaderboard data and length
        data = self.xp_manager.get_users_sorted_by_total_earned()
        length = len(data)

        # Set the embed description
        if length > 0:
            description = "`User`/`Month earned`/`Global earned`\n\n"
            for index, user in enumerate(data[:10], start=1): # Only show the top 10, start index at 1
                steamid64, total_earned, global_earned = user[0], user[1], user[2]
                # Get user info
                success, steam64id, name, avatar = self.checker.get_persona(steamid64)
                description = description + f" > **{index}**. `{name}` • `{total_earned} XP` • `{global_earned} XP`\n"
        else:
            description = f"{self.config.discord_emoji_id} There's no people in the leaderboard."

        # Create the embed
        embed = discord.Embed(title="🏆 XP Leaderboard.", description=description, color=0xb34760)
        embed.set_author(name=f"Tracker", icon_url=self.config.csgo_tracker_logo, url="https://kwayservices.top")
        embed.set_footer(text=f"Top 10 • Last updated: {self.datetime_helper.get_current_timestamp().strftime('%H:%M:%S')}", icon_url=self.config.csgo_tracker_logo)
        embed.set_thumbnail(url=self.config.csgo_tracker_logo)

        # Edit the message
        await leaderboard_message.edit(embed=embed)