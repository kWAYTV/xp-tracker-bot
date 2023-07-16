import discord
from datetime import datetime
from discord.ext import commands
from discord import app_commands
from src.util.utils import Utils
from src.util.logger import Logger
from src.helper.config import Config
from src.steam.checker import Checker
from src.helper.datetime import DateTime
from src.manager.xp_manager import XpManager

class ChangeUserGuild(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.utils = Utils()
        self.config = Config()
        self.database = XpManager()
        self.checker = Checker()
        self.datetime_helper = DateTime()

    # Remove user command  
    @app_commands.command(name="change_user_guild", description="Change the associated guild to the id's you've added to the tracker.")
    @app_commands.describe(
        id="The steamid64/vanity/profile url of the user you want to change the guild to.",
        guild_id="The ID of the guild you want to associate the user with.",
        hidden="If the command should be hidden from other users or not."
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def change_user_guild(self, interaction: discord.Interaction, id: str, guild_id: str, hidden: bool = True):
        await interaction.response.defer(ephemeral=hidden)

        # Clean the username
        username = await self.utils.clean_discord_username(f"{interaction.user.name}#{interaction.user.discriminator}")

        changing_message = await interaction.followup.send(f"{self.config.loading_green_emoji_id} Trying to change {id}'s associated guild.", ephemeral=hidden)

        if not guild_id:
            await interaction.response.send_message(f"Could not find a guild with ID {guild_id}.", ephemeral=True)
            return

        try:
            guild = await self.bot.fetch_guild(guild_id)
        except Exception as e:
            await changing_message.edit(content=f"Couldn't change the guild of the id `{id}`. Error: {e}")
            return

        success, steamid64, nickname, avatar = self.checker.get_persona(id)

        if not success:
            await changing_message.edit(content=f"The id `{id}` is not a valid ID.")
            await self.logger.discord_log(f"✅ {username} tried to change the guild of the id `{id}` but it's not a valid ID.")
            return

        if not self.database.check_adding_ownership(steamid64, interaction.user.id):
            await changing_message.edit(content=f"You don't have permission to change the guild of the id `{id}`. Ask whoever added it.")
            await self.logger.discord_log(f"✅ {username} tried to change the guild of the id `{id}` but they don't have permission.")
            return

        try:
            self.database.change_guild(steamid64, guild.id)
        except Exception as e:
            await changing_message.edit(content=f"Couldn't change the guild of the id `{id}`. Error: {e}")
            return

        embed = discord.Embed(title=f"{self.config.green_tick_emoji_id} Successfully changed `{nickname}`'s guild", url=f"https://steamcommunity.com/profiles/{steamid64}", color=0xba7272)

        embed.set_author(name=f"Tracker", icon_url=self.config.csgo_tracker_logo, url="https://kwayservices.top")
        embed.set_thumbnail(url=avatar)
        embed.add_field(name="Name", value=f"`{nickname}`", inline=True)
        embed.add_field(name="Guild Name", value=f"`{guild.name}`", inline=True)
        embed.add_field(name="Guild ID", value=f"`{guild.id}`", inline=True)

        embed.set_footer(text=f"CSGO Tracker • Requested by {username}", icon_url=self.config.csgo_tracker_logo)
        embed.timestamp = self.datetime_helper.get_current_timestamp()

        await changing_message.edit(content=f"{self.config.green_tick_emoji_id} Request completed.", embed=embed)
        await self.logger.discord_log(f"✅ {username} changed the guild of the id `{id}` to `{guild.name}`.")

    @change_user_guild.error
    async def change_user_guild_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.errors.MissingPermissions):
            await interaction.response.send_message("{self.config.red_cross_emoji_id} You don't have permissions to use this command.", ephemeral=True)
        else:
            await interaction.response.send_message(f"Error: {error}", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(ChangeUserGuild(bot))
    return Logger().log("INFO", "Change user guild command loaded!")