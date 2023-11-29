import discord
from discord.ext import commands
from discord import app_commands
from src.util.logger import Logger
from src.helper.config import Config
from src.helper.datetime import DateTime
from src.manager.xp_manager import XpManager

class GetTotalUsers(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.config = Config()
        self.xp_manager = XpManager()
        self.datetime_helper = DateTime()

    # Get total users bot command  
    @app_commands.command(name="get_total_users", description="Command to get the total users the bot's tracking.")
    async def get_user_count_command(self, interaction: discord.Interaction, hidden: bool = True):
        await interaction.response.defer(ephemeral=hidden)
        total_users = self.xp_manager.get_users_count()
        total_guild_users = self.xp_manager.get_users_count_by_guild_id(interaction.guild.id)
        embed = discord.Embed(title="🧮 Total users being tracked", description="Below you have the total users count:", color=0xb34760)
        embed.add_field(name="Total", value=f"**{total_users}** users.", inline=True)
        embed.add_field(name="This server", value=f"**{total_guild_users} users.**", inline=True)
        embed.set_author(name=f"Tracker", icon_url=self.config.csgo_tracker_logo, url="https://kwayservices.top")
        embed.set_footer(text="CSGO Tracker • kwayservices.top", icon_url=self.config.csgo_tracker_logo)
        embed.set_thumbnail(url=self.config.csgo_tracker_logo)
        embed.set_image(url=self.config.rainbow_line_gif)
        embed.timestamp = self.datetime_helper.get_current_timestamp()
        await interaction.followup.send(embed=embed)

    @get_user_count_command.error
    async def get_user_count_command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.errors.MissingPermissions):
            await interaction.response.send_message(f"{self.config.red_cross_emoji_id} You don't have permissions to use this command.", ephemeral=True)
        else:
            await interaction.response.send_message(f"Error: {error}", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(GetTotalUsers(bot))
    return Logger().log("INFO", "Get total users command loaded!")