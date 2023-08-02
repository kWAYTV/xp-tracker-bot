import discord
from discord.ext import commands
from discord import app_commands
from src.util.utils import Utils
from src.util.logger import Logger
from src.helper.config import Config
from src.helper.datetime import DateTime
from src.manager.admin_mode_manager import AdminModeManager

class AdminModeCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.utils = Utils()
        self.config = Config()
        self.logger = Logger(bot)
        self.datetime_helper = DateTime()
        self.admin_mode_manager = AdminModeManager()

    # Admin mode bot command  
    @app_commands.command(name="admin_mode", description="Enable or disable the admin mode on this server.")
    @app_commands.describe(
        switch="If the admin mode should be enabled or disabled.",
        hidden="If the command should be hidden from other users or not."
    )
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.guild_only()
    async def admin_mode_command(self, interaction: discord.Interaction, switch: bool, hidden: bool = True):
        await interaction.response.defer(ephemeral=hidden)

        # Clean the username
        username = await self.utils.clean_discord_username(f"{interaction.user.name}#{interaction.user.discriminator}")

        request_message = await interaction.followup.send(f"{self.config.loading_green_emoji_id} Trying to set admin mode to `{switch}`.", ephemeral=hidden)

        self.logger.log("INFO", f"✅ Admin mode has been requested to be set to `{switch}` on the guild {interaction.guild_id} ({interaction.guild.name}).")
        await self.logger.discord_log(f"✅ {username} requested to set the admin mode to `{switch}` on the guild {interaction.guild_id} ({interaction.guild.name}).")
        
        # Check if the admin mode is already added, if not, add it.
        if self.admin_mode_manager.get_admin_mode(interaction.guild_id) is None:
            self.admin_mode_manager.add_admin_mode(interaction.guild_id, switch)
            return await request_message.edit(content=f"{self.config.green_tick_emoji_id} Admin mode has been set to `{switch}`.")

        # Change the admin mode in case it's already added
        try:
            self.admin_mode_manager.set_admin_mode(interaction.guild_id, switch)
        except Exception as e:
            return await request_message.edit(content=f"{self.config.red_cross_emoji_id} Failed to set admin mode. Error: {e}")
        
        # Send a message to the user
        await request_message.edit(content=f"{self.config.green_tick_emoji_id} Admin mode has been set to `{switch}`.")

        self.logger.log("INFO", f"Admin mode has been set to `{switch}` on the guild {interaction.guild_id} ({interaction.guild.name}) by {username}.")
        return await self.logger.discord_log(f"Admin mode has been set to `{switch}` on the guild {interaction.guild_id} ({interaction.guild.name}) by {username}.")

    @admin_mode_command.error
    async def admin_mode_command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.errors.MissingPermissions):
            return await interaction.response.send_message(f"{self.config.red_cross_emoji_id} You don't have permissions to use this command.", ephemeral=True)
        else:
            return await interaction.response.send_message(f"Error: {error}", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(AdminModeCommand(bot))
    return Logger().log("INFO", "Admin mode command loaded!")