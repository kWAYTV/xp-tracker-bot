import discord
from discord.ext import commands
from discord import app_commands
from src.util.logger import Logger
from src.helper.config import Config
from src.helper.datetime import DateTime

commands_text = f"""
**🌎 Main Commands**
  > - */help* - Show this help message.
  > - */ping* - Test the bot latency and response.
  > - */get_total_users* - Get the total users the bot's tracking.
  > - */get_time_remaining* - Get the total time remaining until the next weekly xp reset.

**👤 Profile Checker Commands**
  > - */check* - Add some steam profile to the queue to be profile-checked.

**🚀 XP Tracker Commands**
  > - */add_user* - Add some user to the xp-tracker database.
  > - */remove_user* - Remove some user from the xp-tracke database, being you who added the user.
  > - */reset_xp* - Let's you reset monthly or total xp, being you who added the user.
  > - */earned* - Show how much xp you've earned in the last month or in total.

*(Please don't add other people's accounts without their permission, they will be removed.)*

**⛔ Admin Commands**
  > - *.sync* - Sync the Discord bot commands.
  > - */setup* - Shows the steps to setup the bot on your server.
  > - */admin_mode* - Set the admin mode for the server.
  > - */set_tracker_channel* - Set the channel where the bot will send the xp-tracker messages on this server.
  > - */change_user_guild* - Change the user's guild, being you who added the user.
  > - */change_user_owner* - Change the id's ownership, being you who added the user.
"""

class Help(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.config = Config()
        self.datetime_helper = DateTime()

    # Help bot command  
    @app_commands.command(name="help", description="Shows the commands to use the bot.")
    @app_commands.describe(
        hidden="If the command should be hidden from other users or not."
    )
    async def help_command(self, interaction: discord.Interaction, hidden: bool = False):
        await interaction.response.defer(ephemeral=hidden)

        embed = discord.Embed(title="📄 Bot Commands", description=commands_text, color=0xb34760)
        embed.set_author(name=f"Tracker", icon_url=self.config.csgo_tracker_logo, url="https://kwayservices.top")
        embed.set_footer(text="CSGO Tracker • kwayservices.top", icon_url=self.config.csgo_tracker_logo)
        embed.set_thumbnail(url=self.config.csgo_tracker_logo)
        embed.set_image(url=self.config.rainbow_line_gif)
        embed.timestamp = self.datetime_helper.get_current_timestamp()
        await interaction.followup.send(embed=embed)

    @help_command.error
    async def help_command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.errors.MissingPermissions):
            await interaction.response.send_message(f"{self.config.red_cross_emoji_id} You don't have permissions to use this command.", ephemeral=True)
        else:
            await interaction.response.send_message(f"Error: {error}", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(Help(bot))
    return Logger().log("INFO", "Help command loaded!")