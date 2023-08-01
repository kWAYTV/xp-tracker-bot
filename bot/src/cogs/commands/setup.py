import discord
from discord.ext import commands
from discord import app_commands
from src.util.logger import Logger
from src.helper.config import Config
from src.helper.datetime import DateTime

setup_text = f"""
  > - 1. Set the admin mode for the server with `/admin_mode` command. This would allow only administrators to add/remove people to the xp tracker.
  > - 2. Set the server's tracker channel with `/set_tracker_channel` command. The xp messages wouuld be sent there.
  > - 3. You can already start to add people to the tracker with `/add_user` command.

  For more information about the commands, use `/help`. We recommend you to keep your xp tracker channel private.
"""

class SetupCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.config = Config()
        self.datetime_helper = DateTime()

    # Help bot command  
    @app_commands.command(name="setup", description="Shows you the steps to setup the bot.")
    async def setup_command(self, interaction: discord.Interaction, hidden: bool = True):
        await interaction.response.defer(ephemeral=hidden)

        embed = discord.Embed(title="🤖 Bot Setup", description=setup_text, color=0xb34760)
        embed.set_author(name=f"Tracker", icon_url=self.config.csgo_tracker_logo, url="https://kwayservices.top")
        embed.set_footer(text="CSGO Tracker • discord.gg/kws", icon_url=self.config.csgo_tracker_logo)
        embed.set_thumbnail(url=self.config.csgo_tracker_logo)
        embed.set_image(url=self.config.rainbow_line_gif)
        embed.timestamp = self.datetime_helper.get_current_timestamp()
        await interaction.followup.send(embed=embed)

    @setup_command.error
    async def setup_command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.errors.MissingPermissions):
            await interaction.response.send_message(f"{self.config.red_cross_emoji_id} You don't have permissions to use this command.", ephemeral=True)
        else:
            await interaction.response.send_message(f"Error: {error}", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(SetupCommand(bot))
    return Logger().log("INFO", "Setup command loaded!")