import discord
from typing import Literal
from discord.ext import commands
from discord import app_commands
from src.util.utils import Utils
from src.util.logger import Logger
from src.helper.config import Config
from src.steam.checker import Checker
from src.helper.datetime import DateTime
from src.manager.xp_manager import XpManager

class ResetXP(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.config = Config()
        self.checker = Checker()
        self.xp_manager = XpManager()
        self.logger = Logger(self.bot)
        self.datetime_helper = DateTime()

    # Earned bot command  
    @app_commands.command(name="reset_xp", description="Let's you reset your own xp.")
    @app_commands.describe(
        mode="If you want to reset the monthly xp, global xp or both.",
        id="The steamid64/vanity/profile url of the user you want to reset the xp of.",
    )
    async def earned_command(self, interaction: discord.Interaction, mode: Literal["Monthly", "Global", "Both"], id: str, hidden: bool = True):
        await interaction.response.defer(ephemeral=hidden)

        # Clean the username
        username = Utils.clean_discord_username(f"{interaction.user.name}#{interaction.user.discriminator}")

        # Tell the user that the bot is working on their order and log it to console and logs channel
        requested_message = await interaction.followup.send(f"{self.config.loading_green_emoji_id} Requesting database for `{id}`'s xp.")
        await self.logger.discord_log(f"⌛ Requesting database for `{id}`'s xp.")
        self.logger.log("INFO", f"⌛ Requesting database for {id}'s xp.")

        # Get user steamid4 to search for him in database later
        success, steamid64, name, avatar = self.checker.get_persona(id)

        # Fetch the user from the database
        fetched_user = self.xp_manager.get_user_by_steam_id(steamid64)

        if fetched_user is None:
            await requested_message.edit(content=f"{self.config.red_cross_emoji_id} The user `{id}` is not in the database.")
            return await self.logger.discord_log(f"❌ The user `{id}` is not in the database.")
        
        # Check if the user's the owner of the id   
        if not self.xp_manager.check_adding_ownership(steamid64, interaction.user.id):
            await requested_message.edit(content=f"{self.config.red_cross_emoji_id} You don't have permissions to use this command on another people.")
            return await self.logger.discord_log(f"❌ {username} Tried to set `{id}`'s xp but he is not the owner of the id.")

        try:
            if mode == "Monthly":
                self.xp_manager.reset_monthly_xp(steamid64)
                return await requested_message.edit(content=f"{self.config.green_tick_emoji_id} Successfully reset `{id}`'s monthly xp.")
            
            if mode == "Global":
                self.xp_manager.reset_global_xp(steamid64)
                return await requested_message.edit(content=f"{self.config.green_tick_emoji_id} Successfully reset `{id}`'s global xp.")
            
            if mode == "Both":
                self.xp_manager.reset_monthly_xp(steamid64)
                self.xp_manager.reset_global_xp(steamid64)
                return await requested_message.edit(content=f"{self.config.green_tick_emoji_id} Successfully reset `{id}`'s monthly and global xp.")
        except Exception as e:
            await requested_message.edit(content=f"{self.config.red_cross_emoji_id} Couldn't reset `{id}`'s xp. Error: {e}")
            return await self.logger.discord_log(f"❌ Couldn't reset `{id}`'s xp. Error: {e}")

    @earned_command.error
    async def hearned_command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.errors.MissingPermissions):
            await interaction.response.send_message(f"{self.config.red_cross_emoji_id} You don't have permissions to use this command.", ephemeral=True)
        else:
            await interaction.response.send_message(f"Error: {error}", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(ResetXP(bot))
    return Logger().log("INFO", "Earned command loaded!")