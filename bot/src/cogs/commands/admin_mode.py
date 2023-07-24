import discord
from discord.ext import commands
from discord import app_commands
from src.util.logger import Logger
from src.helper.config import Config
from src.helper.datetime import DateTime
from src.manager.admin_mode_manager import AdminModeManager

class AdminModeCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.config = Config()
        self.datetime_helper = DateTime()
        self.admin_mode_manager = AdminModeManager()

    # Admin mode bot command  
    @app_commands.command(name="admin_mode", description="Enable or disable the admin mode on this server.")
    @app_commands.describe(
        switch="If the admin mode should be enabled or disabled.",
        hidden="If the command should be hidden from other users or not."
    )
    async def admin_mode_command(self, interaction: discord.Interaction, switch: bool, hidden: bool = True):
        await interaction.response.defer(ephemeral=hidden)

        request_message = await interaction.followup.send(f"{self.config.loading_green_emoji_id} Trying to set admin mode to `{switch}`.", ephemeral=hidden)

        # Check if the user has permissions to use this command
        if not interaction.user.guild_permissions.administrator:
            return await request_message.edit(content=f"{self.config.red_cross_emoji_id} You don't have permissions to use this command.")
        
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

    @admin_mode_command.error
    async def admin_mode_command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.errors.MissingPermissions):
            await interaction.response.send_message(f"{self.config.red_cross_emoji_id} You don't have permissions to use this command.", ephemeral=True)
        else:
            await interaction.response.send_message(f"Error: {error}", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(AdminModeCommand(bot))
    return Logger().log("INFO", "Admin mode command loaded!")