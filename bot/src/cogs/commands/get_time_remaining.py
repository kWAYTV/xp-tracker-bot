import discord
from discord.ext import commands
from discord import app_commands
from src.util.logger import Logger
from src.helper.config import Config
from src.helper.datetime import DateTime

class GetTimeRemaining(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.config = Config()
        self.datetime_helper = DateTime()

    # Get time remaining bot command  
    @app_commands.command(name="get_time_remaining", description="Command to get the total time remaining until the next weekly xp reset.")
    async def get_time_remaining_command(self, interaction: discord.Interaction, hidden: bool = True):
        await interaction.response.defer(ephemeral=hidden)
        remaining_time = self.datetime_helper.time_until_next_wednesday()
        embed = discord.Embed(title="⌛ Time remaining", description="Below you have the total time remaining for the next weekly xp reset:", color=0xb34760)
        embed.add_field(name="Total", value=f"```{remaining_time}```", inline=True)
        embed.set_author(name=f"Tracker", icon_url=self.config.csgo_tracker_logo, url="https://kwayservices.top")
        embed.set_footer(text="CSGO Tracker • Timezone used: GMT+2 (Madrid, Spain) • kwayservices.top", icon_url=self.config.csgo_tracker_logo)
        embed.set_thumbnail(url=self.config.csgo_tracker_logo)
        embed.set_image(url=self.config.rainbow_line_gif)
        embed.timestamp = self.datetime_helper.get_current_timestamp()
        await interaction.followup.send(embed=embed)

    @get_time_remaining_command.error
    async def get_time_remaining_command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.errors.MissingPermissions):
            await interaction.response.send_message(f"{self.config.red_cross_emoji_id} You don't have permissions to use this command.", ephemeral=True)
        else:
            await interaction.response.send_message(f"Error: {error}", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(GetTimeRemaining(bot))
    return Logger().log("INFO", "Get time remaining command loaded!")