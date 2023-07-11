import discord
from datetime import datetime
from discord.ext import commands
from discord import app_commands
from src.util.utils import Utils
from src.util.logger import Logger
from src.helper.config import Config
from src.steam.checker import Checker
from src.manager.xp_manager import XpManager
from src.helper.trackeduser_class import TrackedUser

class RemoveUser(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.utils = Utils()
        self.config = Config()
        self.database = XpManager()
        self.checker = Checker()

    # Remove user command  
    @app_commands.command(name="remove_user", description="Remove an user from the xp tracker database.")
    @app_commands.describe(
        id="The steamid64/vanity/profile url of the user you want to stop to track.",
        hidden="If the command should be hidden from other users or not."
    )
    @commands.has_permissions(administrator=True)
    async def remove_track_user(self, interaction: discord.Interaction, id: str, hidden: bool = True):
        await interaction.response.defer(ephemeral=hidden)

        # Clean the username
        username = await self.utils.clean_discord_username(f"{interaction.user.name}#{interaction.user.discriminator}")

        added_message = await interaction.followup.send(f"{self.config.loading_green_emoji_id} Trying to remove id `{id}` from the tracker database.", ephemeral=hidden)

        success, steamid64, nickname, avatar = self.checker.get_persona(id)

        if not success:
            await added_message.edit(content=f"The id `{id}` is not a valid ID.")
            await self.logger.discord_log(f"✅ {username} tried to remove the id `{id}` from the tracker database but it's not a valid ID.")
            return

        if self.database.get_user_by_steam_id(steamid64) is None:
            await added_message.edit(content=f"The id `{id}` is not being tracked.")
            await self.logger.discord_log(f"✅ {username} tried to remove the id `{id}` from the tracker database but it's not being tracked.")
            return

        if not self.database.check_adding_ownership(steamid64, interaction.user.id):
            await added_message.edit(content=f"You don't have permission to remove the id `{id}` from the tracker database.")
            await self.logger.discord_log(f"✅ {username} tried to remove the id `{id}` from the tracker database but it doesn't have permission.")
            return
        
        removed_user = TrackedUser(steamid64, interaction.user.id, None, None, None)

        try:
            self.database.remove_user(removed_user)
        except Exception as e:
            await added_message.edit(content=f"Couldn't remove id {id} from the tracker database. Error: {e}")
            return

        embed = discord.Embed(title=f"{self.config.green_tick_emoji_id} Successfully removed `{nickname}`", url=f"https://steamcommunity.com/profiles/{steamid64}", color=0xba7272)

        embed.set_author(name=f"CSGO Tracker", icon_url=self.config.csgo_tracker_logo, url="https://kwayservices.top")
        embed.set_thumbnail(url=avatar)
        embed.add_field(name="SteamID64", value=f"`{steamid64}`", inline=True)

        embed.set_footer(text=f"CSGO Tracker • Requested by {username}", icon_url=self.config.csgo_tracker_logo)
        embed.timestamp = datetime.utcnow()

        await added_message.edit(content=f"{self.config.green_tick_emoji_id} Request completed.", embed=embed)
        await self.logger.discord_log(f"✅ {username} removed the id `{id}` from the tracker database.")

    @remove_track_user.error
    async def remove_track_user_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.errors.MissingPermissions):
            await interaction.response.send_message("❌ You don't have permissions to use this command.", ephemeral=True)
        else:
            await interaction.response.send_message(f"Error: {error}", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(RemoveUser(bot))
    return Logger().log("INFO", "Remove user command loaded!")