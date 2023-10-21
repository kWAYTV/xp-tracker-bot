import discord
from discord.ext import commands
from discord import app_commands
from src.util.utils import Utils
from src.util.logger import Logger
from src.helper.config import Config
from src.manager.guild_manager import GuildManager
from src.manager.timeout_manager import TimeoutManager

class SetXpChannel(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.config = Config()
        self.logger = Logger(self.bot)
        self.guild_manager = GuildManager()
        self.timeout_manager = TimeoutManager()

    # Add user command  
    @app_commands.command(name="set_tracker_channel", description="Set the specified channel as the xp tracker channel for this guild.")
    @app_commands.describe(
        channel="The channel you want the xp tracker messages to be sent to in this guild.",
        hidden="If the command should be hidden from other users or not."
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def set_tracker_channel(self, interaction: discord.Interaction, channel: discord.TextChannel, hidden: bool = True):
        await interaction.response.defer(ephemeral=hidden)

        # Clean the username
        username = Utils.clean_discord_username(f"{interaction.user.name}#{interaction.user.discriminator}")

        # Check if the user is in timeout
        is_in_timeout, time_remaining = self.timeout_manager.is_user_in_timeout(interaction.user.id)
        if is_in_timeout:
            minutes, seconds = divmod(time_remaining, 60)
            await self.logger.discord_log(f"⏳ {username} tried to use the set_tracker_channel command but is in timeout for {int(minutes)} minutes and {int(seconds)} seconds.")
            self.logger.log("INFO", f"⏳ {username} tried to use the set_tracker_channel command but is in timeout for {int(minutes)} minutes and {int(seconds)} seconds.")
            return await interaction.followup.send(f"{self.config.loading_red_emoji_id} You can only use this command every {self.config.user_timeout} seconds! Please wait {int(minutes)} minutes and {int(seconds)} seconds.", ephemeral=hidden)

        requested_message = await interaction.followup.send(f"{self.config.loading_green_emoji_id} Trying to set channel id `{channel.id}` as the guild's xp tracker channel.", ephemeral=hidden)

        if self.guild_manager.get_guild(interaction.guild.id) is not None:
            self.guild_manager.update_guild(interaction.guild.id, channel.id)
            await requested_message.edit(content=f"{self.config.green_tick_emoji_id} Successfully updated channel id `{channel.id}` as the guild's xp tracker channel.")
            return await self.logger.discord_log(f"✅ {username} updated channel id `{channel.id}` as the guild's xp tracker channel.")

        try:
            self.guild_manager.add_guild(interaction.guild.id, channel.id)
        except Exception as e:
            await requested_message.edit(content=f"{self.config.loading_green_emoji_id} An error occurred while trying to add the guild to the database. Error: {e}")
            return await self.logger.discord_log(f"❌ An error occurred while trying to add the guild to the database. Error: {e}")
        
        await requested_message.edit(content=f"{self.config.green_tick_emoji_id} Successfully set channel id `{channel.id}` as the guild's xp tracker channel.")
        return await self.logger.discord_log(f"✅ {username} set channel id `{channel.id}` as the guild's xp tracker channel.")

    @set_tracker_channel.error
    async def set_tracker_channel_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.errors.MissingPermissions):
            return await interaction.response.send_message(f"{self.config.red_cross_emoji_id} You don't have permissions to use this command.", ephemeral=True)
        else:
            return await interaction.response.send_message(f"Error: {error}", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(SetXpChannel(bot))
    return Logger().log("INFO", "Set tracker channel command loaded!")