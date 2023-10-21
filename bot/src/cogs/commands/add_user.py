import discord
from discord.ext import commands
from discord import app_commands
from src.util.utils import Utils
from src.util.logger import Logger
from src.helper.config import Config
from src.steam.checker import Checker
from src.helper.datetime import DateTime
from src.handler.xp_handler import XpHandler
from src.manager.xp_manager import XpManager
from src.manager.guild_manager import GuildManager
from src.helper.trackeduser_class import TrackedUser
from src.manager.admin_mode_manager import AdminModeManager

class AddUser(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.config = Config()
        self.checker = Checker()
        self.database = XpManager()
        self.xp_handler = XpHandler()
        self.logger = Logger(self.bot)
        self.datetime_helper = DateTime()
        self.guild_manager = GuildManager()
        self.admin_mode_manager = AdminModeManager()

    # Add user command  
    @app_commands.command(name="add_user", description="Add a user to the xp tracker database.")
    @app_commands.describe(
        id="The steamid64/vanity/profile url of the user you want to start to track.",
        hidden="If the command should be hidden from other users or not."
    )
    async def add_track_user(self, interaction: discord.Interaction, id: str, hidden: bool = True):
        await interaction.response.defer(ephemeral=hidden)

        # Clean the username
        username = Utils.clean_discord_username(f"{interaction.user.name}#{interaction.user.discriminator}")

        # Send the loading message
        added_message = await interaction.followup.send(f"{self.config.loading_green_emoji_id} Trying to add id `{id}` to the tracker database.", ephemeral=hidden)

        admin_mode = self.admin_mode_manager.get_admin_mode(interaction.guild_id)

        # Check if the admin mode is set
        if admin_mode is None:
            await added_message.edit(content=f"{self.config.red_cross_emoji_id} Couldn't get the admin mode status for this server. Tell the owner to set it.")
            await self.logger.discord_log(f"✅ {username} tried to add an id to the tracker database, but couldn't get the admin mode status.")
            return

        # Check if the user has permissions to use this command
        if not interaction.user.guild_permissions.administrator and admin_mode:
            await added_message.edit(content=f"{self.config.red_cross_emoji_id} The admin mode is enabled. Only administrators can use this command.")
            await self.logger.discord_log(f"✅ {username} tried to add an id to the tracker database, but the admin mode is enabled.")
            return

        # Check if the id is valid and get the data
        success, steamid64, nickname, avatar = self.checker.get_persona(id)

        # If the id is not valid
        if not success:
            await added_message.edit(content=f"The id `{id}` is not a valid ID.")
            await self.logger.discord_log(f"✅ {username} tried to add an invalid id to the tracker database.")
            return

        # Check if the user is already being tracked
        if self.database.get_user_by_steam_id(steamid64) is not None:
            await added_message.edit(content=f"The id `{id}` is already being tracked. If you want to update the user's guild, whoever added it needs to use the `/change_user_guild` command.")
            await self.logger.discord_log(f"✅ {username} tried to add an already tracked id to the tracker database.")
            return
        
        # Check if the guild has a tracker channel set
        if not self.guild_manager.guild_exists(interaction.guild_id):
            await added_message.edit(content=f"{self.config.red_cross_emoji_id} This server doesn't have a tracker channel set. Tell an admin to set it.")
            await self.logger.discord_log(f"✅ {username} tried to add an id to the tracker database, but the guild doesn't have a tracker channel set.")
            return

        # Get the level and XP
        try:
            level, xp, remaining_xp, percentage = await self.xp_handler.get_user_level_and_xp(steamid64)
        except Exception as e:
            await added_message.edit(content=f"{self.config.red_cross_emoji_id} Couldn't get level and XP for `{id}`, couldn't add him to the tracker database. Error: {e}")
            await self.logger.discord_log(f"✅ {username} tried to add an id to the tracker database, but couldn't get the level and XP.")
            return

        # Add the user to the database
        added_user = TrackedUser(steamid64, interaction.user.id, interaction.guild.id, level, xp, 0, 0)
        try:
            self.database.add_user(added_user)
        except Exception as e:
            await added_message.edit(content=f"Couldn't add id {id} to the tracker database. Error: {e}")
            await self.logger.discord_log(f"✅ {username} tried to add an id to the tracker database, but couldn't add him to the database.")
            return

        # Send the embed
        embed = discord.Embed(title=f"{self.config.green_tick_emoji_id} Successfully added `{nickname}`", url=f"https://steamcommunity.com/profiles/{steamid64}", color=0x08dbf8c)

        embed.set_author(name=f"Tracker", icon_url=self.config.csgo_tracker_logo, url="https://kwayservices.top")
        embed.set_thumbnail(url=avatar)
        embed.add_field(name="SteamID64", value=f"`{steamid64}`", inline=True)
        embed.add_field(name="Current level", value=f"`{level}`", inline=True)
        embed.add_field(name="Current XP", value=f"`{xp}`", inline=True)

        embed.set_footer(text=f"CSGO Tracker • Requested by {username}", icon_url=self.config.csgo_tracker_logo)
        embed.set_image(url=self.config.rainbow_line_gif)
        embed.timestamp = self.datetime_helper.get_current_timestamp()

        # Edit the message with the embed and log it
        await added_message.edit(content=f"{self.config.green_tick_emoji_id} Request completed.", embed=embed)
        await self.logger.discord_log(f"✅ {username} added `{nickname}` to the tracker database.")

    # In case of an error
    @add_track_user.error
    async def add_track_user_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.errors.MissingPermissions):
            await interaction.response.send_message(f"{self.config.red_cross_emoji_id} You don't have permissions to use this command.", ephemeral=True)
        else:
            await interaction.response.send_message(f"Error: {error}", ephemeral=True)

async def setup(bot: commands.Bot):
    # Add the cog and log it
    await bot.add_cog(AddUser(bot))
    return Logger().log("INFO", "Add user command loaded!")