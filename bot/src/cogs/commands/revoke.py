import discord
from discord.ext import commands
from discord import app_commands
from src.util.utils import Utils
from src.util.logger import Logger
from src.helper.config import Config
from src.helper.datetime import DateTime
from src.manager.timeout_manager import TimeoutManager

class Revoke(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.utils = Utils()
        self.config = Config()
        self.logger = Logger(self.bot)
        self.datetime_helper = DateTime()
        self.timeout_manager = TimeoutManager()

    # Revoke bot command  
    @app_commands.command(name="revoke", description="Revoke someone's timeout")
    @app_commands.describe(
        user="The user you want to revoke the timeout from.",
        notify_user="If you want to notify the user that their timeout has been revoked."
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def revoke_command(self, interaction: discord.Interaction, user: discord.Member, notify_user: bool = True):
        await interaction.response.defer(ephemeral=True)

        # Clean the username
        request_username = await self.utils.clean_discord_username(f"{interaction.user.name}#{interaction.user.discriminator}")

        # Send a loading message
        requested_message = await interaction.followup.send(f"{self.config.loading_green_emoji_id} Revoking timeout...")
        
        # Remove the user's timeout
        revoke = self.timeout_manager.remove_user(user.id)

        # If revoke is False, the user doesn't have a timeout
        if not revoke:
            await self.logger.discord_log(f"❌ {request_username} tried to revoke user ID: `{user.id}`'s timeout, but they don't have one.")
            self.logger.log("INFO", f"{self.config.red_cross_emoji_id} {request_username} tried to revoke user ID: {user.id}'s timeout, but they don't have one.")
            return await requested_message.edit(content=f"{self.config.loading_red_emoji_id} The user doesn't have a timeout.")

        # Create an embed and send it to the user.
        embed = discord.Embed(title=f"{self.config.green_tick_emoji_id} Timeout revoked", description=f"User ID: `{user.id}` has been revoked by {interaction.user.mention}.", color=0x00ff00)
        embed.set_footer(text=f"CSGO Tracker • Revoked by {request_username}", icon_url=self.config.csgo_tracker_logo)
        embed.timestamp = self.datetime_helper.get_current_timestamp()

        # Dm the user that their timeout has been revoked
        if notify_user:
            try:
                await user.send(embed=embed)
            except:
                pass

        await requested_message.edit(content=f"{self.config.green_tick_emoji_id} The timeout has been revoked.", embed=embed)
        await self.logger.discord_log(f"✅ {request_username} revoked user ID: `{user.id}`'s timeout.")
        self.logger.log("INFO", f"✅ {request_username} revoked user ID: {user.id}'s timeout.")

    @revoke_command.error
    async def revoke_command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.errors.MissingPermissions):
            await interaction.response.send_message(f"{self.config.red_cross_emoji_id} You don't have permissions to use this command.", ephemeral=True)
        else:
            await interaction.response.send_message(f"Error: {error}", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(Revoke(bot), guild=discord.Object(id=Config().dev_guild_id))
    return Logger().log("INFO", "Revoke command loaded!")