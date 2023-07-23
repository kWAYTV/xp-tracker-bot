import discord
from discord.ext import commands
from discord import app_commands
from src.util.utils import Utils
from src.util.logger import Logger
from src.helper.config import Config
from src.steam.checker import Checker
from src.helper.datetime import DateTime
from src.manager.xp_manager import XpManager

class ChangeUserOwner(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.utils = Utils()
        self.config = Config()
        self.logger = Logger()
        self.checker = Checker()
        self.database = XpManager()
        self.datetime_helper = DateTime()

    # Remove user command  
    @app_commands.command(name="change_user_owner", description="Change the associated guild to the id's you've added to the tracker.")
    @app_commands.describe(
        id="The steamid64/vanity/profile url of the user you want to change the ownership to.",
        new_owner="The ID of the guild you want to associate the user with.",
        hidden="If the command should be hidden from other users or not."
    )
    async def change_user_owner(self, interaction: discord.Interaction, id: str, new_owner: discord.Member, hidden: bool = True):
        await interaction.response.defer(ephemeral=hidden)

        # Clean the username
        username = await self.utils.clean_discord_username(f"{interaction.user.name}#{interaction.user.discriminator}")
        
        # Send the loading message
        changing_message = await interaction.followup.send(f"{self.config.loading_green_emoji_id} Trying to change {id}'s associated owner id.", ephemeral=hidden)

        # Get user steamid4 to search for him in database later
        success, steamid64, nickname, avatar = self.checker.get_persona(id)

        # If the user is not on the database, send an error message
        if not success:
            await changing_message.edit(content=f"The id `{id}` is not a valid ID.")
            await self.logger.discord_log(f"✅ {username} tried to change the ownership id of the id `{id}` but it's not a valid ID.")
            return
        
        # Check if the user that's running the command is the owner of the id
        if not self.database.check_adding_ownership(steamid64, interaction.user.id):
            await changing_message.edit(content=f"You don't have permissions to change the ownership of the id `{id}`.")
            return

        # Actually change the ownership
        try:
            self.database.change_discord_id(steamid64, new_owner.id)
        except Exception as e:
            await changing_message.edit(content=f"Couldn't change the ownership of the id `{id}`. Error: {e}")
            return

        # Send the success message and log it
        await changing_message.edit(content=f"{self.config.green_tick_emoji_id} Successfully changed the ownership of the id `{id}` to `{new_owner.id}`.")
        await self.logger.discord_log(f"✅ {username} changed the ownership it of the id `{id}` to `{new_owner.id}`.")

    # Error handler for the remove_user command
    @change_user_owner.error
    async def change_user_owner_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.errors.MissingPermissions):
            await interaction.response.send_message(f"{self.config.red_cross_emoji_id} You don't have permissions to use this command.", ephemeral=True)
        else:
            await interaction.response.send_message(f"Error: {error}", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(ChangeUserOwner(bot))
    return Logger().log("INFO", "Change user owner command loaded!")