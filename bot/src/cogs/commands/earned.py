import discord
from discord.ext import commands
from discord import app_commands
from src.util.utils import Utils
from src.util.logger import Logger
from src.helper.config import Config
from src.steam.checker import Checker
from src.helper.datetime import DateTime
from src.manager.xp_manager import XpManager

class Earned(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.utils = Utils()
        self.config = Config()
        self.checker = Checker()
        self.xp_manager = XpManager()
        self.logger = Logger(self.bot)
        self.datetime_helper = DateTime()

    # Earned bot command  
    @app_commands.command(name="earned", description="Shows how many XP you've learned in last month or in total.")
    @app_commands.describe(
        id="The steamid64/vanity/profile url of the user you want to see the earned xp of.",
        hidden="If the command should be hidden from other users or not."
    )
    async def earned_command(self, interaction: discord.Interaction, id: str, hidden: bool = True):
        await interaction.response.defer(ephemeral=hidden)

        # Clean the username
        username = await self.utils.clean_discord_username(f"{interaction.user.name}#{interaction.user.discriminator}")

        # Tell the user that the bot is working on their order and log it to console and logs channel
        requested_message = await interaction.followup.send(f"{self.config.loading_green_emoji_id} Requesting database for {id}'s xp.")
        await self.logger.discord_log(f"⌛ Requesting database for {id}'s xp.")
        self.logger.log("INFO", f"⌛ Requesting database for {id}'s xp.")

        # Get user steamid4 to search for him in database later
        success, steamid64, name, avatar = self.checker.get_persona(id)

        # Check if the user's the owner of the id   
        if not self.xp_manager.check_adding_ownership(steamid64, interaction.user.id):
            await requested_message.edit(content=f"{self.config.red_cross_emoji_id} You don't have permissions to use this command on another people.")
            return await self.logger.discord_log(f"❌ {username} Tried to set `{id}`'s xp but he is not the owner of the id.")

        # Get their earned xp   
        earned_xp = self.xp_manager.get_earned_by_steamid64(steamid64)

        # If the user is not on the database, send an error message
        if earned_xp is None:
            await requested_message.edit(content=f"{self.config.red_cross_emoji_id} The user is not on the database!")
            await self.logger.discord_log(f"❌ The user is not on the database!")
            self.logger.log("ERROR", f"❌ The user is not on the database!")
            return

        # Create embed
        embed = discord.Embed(title="📄 Earned XP", description="Here you will have displayed your monthly and global xp earnings.", color=0x000000)
        embed.set_author(name=f"Tracker", icon_url=self.config.csgo_tracker_logo, url="https://kwayservices.top")

        # Add fields to embed
        embed.add_field(name="Monthly XP", value=f"`{earned_xp[0]}`", inline=True)
        embed.add_field(name="Global XP", value=f"`{earned_xp[1]}`", inline=True)

        # Add footer and thumbnail to embed
        embed.set_footer(text="CSGO Tracker • discord.gg/kws", icon_url=self.config.csgo_tracker_logo)
        embed.set_thumbnail(url=self.config.csgo_tracker_logo)
        embed.set_image(url=self.config.rainbow_line_gif)
        embed.timestamp = self.datetime_helper.get_current_timestamp()

        # Edit the message to show the embed
        await requested_message.edit(content=f"{self.config.green_tick_emoji_id} Database query completed!", embed=embed)

    @earned_command.error
    async def earned_command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.errors.MissingPermissions):
            await interaction.response.send_message(f"{self.config.red_cross_emoji_id} You don't have permissions to use this command.", ephemeral=True)
        else:
            await interaction.response.send_message(f"Error: {error}", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(Earned(bot))
    return Logger().log("INFO", "Earned command loaded!")