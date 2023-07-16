import discord
from datetime import datetime
from discord.ext import commands
from discord import app_commands
from src.util.utils import Utils
from src.util.logger import Logger
from src.helper.config import Config
from src.steam.checker import Checker
from src.helper.datetime import DateTime
from src.handler.xp_handler import XpHandler
from src.manager.xp_manager import XpManager
from src.helper.trackeduser_class import TrackedUser

class AddUser(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.utils = Utils()
        self.config = Config()
        self.logger = Logger(self.bot)
        self.database = XpManager()
        self.xp_handler = XpHandler()
        self.checker = Checker()
        self.datetime_helper = DateTime()

    # Add user command  
    @app_commands.command(name="add_user", description="Add an user to the xp tracker database.")
    @app_commands.describe(
        id="The steamid64/vanity/profile url of the user you want to start to track.",
        hidden="If the command should be hidden from other users or not."
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def add_track_user(self, interaction: discord.Interaction, id: str, hidden: bool = True):
        await interaction.response.defer(ephemeral=hidden)

        # Clean the username
        username = await self.utils.clean_discord_username(f"{interaction.user.name}#{interaction.user.discriminator}")

        added_message = await interaction.followup.send(f"{self.config.loading_green_emoji_id} Trying to add id `{id}` to the tracker database.", ephemeral=hidden)

        success, steamid64, nickname, avatar = self.checker.get_persona(id)

        if not success:
            await added_message.edit(content=f"The id `{id}` is not a valid ID.")
            await self.logger.discord_log(f"✅ {username} tried to add an invalid id to the tracker database.")
            return

        if self.database.get_user_by_steam_id(steamid64) is not None:
            await added_message.edit(content=f"The id `{id}` is already being tracked. If you want to update the user's guild, whoever added it needs to use the `/change_user_guild` command.")
            await self.logger.discord_log(f"✅ {username} tried to add an already tracked id to the tracker database.")
            return

        try:
            level, xp, remaining_xp, percentage = self.xp_handler.get_user_level_and_xp(steamid64)
        except Exception as e:
            await added_message.edit(content=f"{self.config.red_cross_emoji_id} Couldn't get level and XP for `{id}`, couldn't add him to the tracker database. Error: {e}")
            await self.logger.discord_log(f"✅ {username} tried to add an id to the tracker database, but couldn't get the level and XP.")
            return

        added_user = TrackedUser(steamid64, interaction.user.id, level, xp, interaction.guild.id)
        try:
            self.database.add_user(added_user)
        except Exception as e:
            await added_message.edit(content=f"Couldn't add id {id} to the tracker database. Error: {e}")
            await self.logger.discord_log(f"✅ {username} tried to add an id to the tracker database, but couldn't add him to the database.")
            return

        embed = discord.Embed(title=f"{self.config.green_tick_emoji_id} Successfully added `{nickname}`", url=f"https://steamcommunity.com/profiles/{steamid64}", color=0x08dbf8c)

        embed.set_author(name=f"Tracker", icon_url=self.config.csgo_tracker_logo, url="https://kwayservices.top")
        embed.set_thumbnail(url=avatar)
        embed.add_field(name="SteamID64", value=f"`{steamid64}`", inline=True)
        embed.add_field(name="Current level", value=f"`{level}`", inline=True)
        embed.add_field(name="Current XP", value=f"`{xp}`", inline=True)

        embed.set_footer(text=f"CSGO Tracker • Requested by {username}", icon_url=self.config.csgo_tracker_logo)
        embed.timestamp = self.datetime_helper.get_current_timestamp()

        await added_message.edit(content=f"{self.config.green_tick_emoji_id} Request completed.", embed=embed)
        await self.logger.discord_log(f"✅ {username} added `{nickname}` to the tracker database.")

    @add_track_user.error
    async def add_track_user_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.errors.MissingPermissions):
            await interaction.response.send_message("{self.config.red_cross_emoji_id} You don't have permissions to use this command.", ephemeral=True)
        else:
            await interaction.response.send_message(f"Error: {error}", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(AddUser(bot))
    return Logger().log("INFO", "Add user command loaded!")