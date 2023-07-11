import discord, secrets
from discord import File
from datetime import datetime
from discord.ext import commands
from discord import app_commands
from src.util.utils import Utils
from src.util.logger import Logger
from src.steam.faceit import Faceit
from src.helper.config import Config
from src.steam.checker import Checker
from src.handler.medal_handler import MedalHandler
from src.handler.queue_handler import QueueHandler
from src.manager.timeout_manager import TimeoutManager

class Check(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.utils = Utils()
        self.config = Config()
        self.checker = Checker()
        self.faceit = Faceit()
        self.logger = Logger(self.bot)
        self.queue_handler = QueueHandler()
        self.medal_handler = MedalHandler()
        self.timeout_manager = TimeoutManager()

    # Check bot command  
    @app_commands.command(name="check", description=f"Add some steam profile to the queue to be checked.")
    @app_commands.describe(
        id="The steam id (profile link, custom id, steamid64) to be checked.",
        hidden="If the command should be hidden from other users or not."
    )
    async def check_command(self, interaction: discord.Interaction, id: str, hidden: bool = True):
        await interaction.response.defer(ephemeral=hidden)

        # Clean the username
        username = await self.utils.clean_discord_username(f"{interaction.user.name}#{interaction.user.discriminator}")

        # Check if the user is in timeout
        is_in_timeout, time_remaining = self.timeout_manager.is_user_in_timeout(interaction.user.id)
        if is_in_timeout:
            minutes, seconds = divmod(time_remaining, 60)
            await self.logger.discord_log(f"⏳ {username} tried to use the spam command but is in timeout for {int(minutes)} minutes and {int(seconds)} seconds.")
            self.logger.log("INFO", f"⏳ {username} tried to use the spam command but is in timeout for {int(minutes)} minutes and {int(seconds)} seconds.")
            return await interaction.followup.send(f"{self.config.loading_red_emoji_id} You can only use this command every {self.config.user_timeout} seconds! Please wait {int(minutes)} minutes and {int(seconds)} seconds.", ephemeral=hidden)

        # Check if the api it's online
        if not self.checker.is_api_online():
            await self.logger.discord_log(f"⚠️ {username} tried to use the spam command but the API is offline.")
            self.logger.log("INFO", f"⚠️ {username} tried to use the spam command but the API is offline.")
            return await interaction.followup.send(f"{self.config.loading_red_emoji_id} The API is offline, please try again later.", ephemeral=hidden)
        
        # Tell the user that the bot is working on their order and log it to console and logs channel
        requested_message = await interaction.followup.send(f"{self.config.loading_green_emoji_id} Requested `{id}` to be checked.", ephemeral=hidden)
        await self.logger.discord_log(f"⌛ Requested `{id}` to be checked. Requested by `{username}`.")
        self.logger.log("INFO", f"⌛ Requested `{id}` to be checked.. Requested by {username}")

        # Create an embed to send to the user
        embed = discord.Embed(title=f"{self.config.green_tick_emoji_id} Successfully added!", description=f"Checking added to the queue.\nID: `{id}`.", color=0x00ff00)
        embed.set_thumbnail(url=self.config.csgo_tracker_logo)
        embed.set_footer(text=f"CSGO Tracker • Requested by {username}")
        embed.timestamp = datetime.utcnow()

        # Edit the message to send the embed and log it to console and logs channel
        await requested_message.edit(content=f"{self.config.green_tick_emoji_id} The order has been added to the queue.", embed=embed)
        await self.logger.discord_log(f"✅ Successfully added `{id}` to the queue. Requested by `{username}`.")
        self.logger.log("INFO", f"✅ Successfully added `{id}` to the queue. Requested by `{username}`")

        # Generate a random queue ID
        queue_id = f"KWS{secrets.token_hex(6)}"

        # Get user info
        success, steamid64, name, avatar = self.checker.get_persona(id)

        self.queue_handler.push_order({'steamid64': steamid64, 'queue_id': queue_id,'requested_by': int(interaction.user.id)})
        await self.queue_handler.force_check_start()

        # Get the results of the check
        success, result = await self.queue_handler.get_check_results(steamid64)
        image_path = None

        # Check if the check was successful
        if success:

            steamid64 = result['steamid64']
            nickname = result['nickname']
            avatar = result['avatar']
            profile_url = result['profile_url']
            country_code = result['country_code']
            steam_level = result['steam_level']
            csgo_level = result['csgo_level']
            level_percentage = result['level_percentage']
            remaining_xp = result['remaining_xp']
            friendly_commends = result['friendly_commends']
            leader_commends = result['leader_commends']
            teacher_commends = result['teacher_commends']
            medals = result['medals']

            # Get faceit stats
            faceit_success, faceit_stats_text, faceit_profile_url = await self.faceit.get_combined_stats(steamid64)

            # Get friend code
            friend_code = self.checker.steam64_to_friend_code(steam64 = steamid64)

            # Get the medals image
            image_path = await self.medal_handler.get_image_path(f"{queue_id}")
            if image_path is not None:
                image_file = File(image_path, filename="medals.png")

            # Build the embed with the results
            embed = discord.Embed(
                title=f"{self.config.green_tick_emoji_id} {nickname}",
                description=f"\n*{steamid64}*",  # Include the results in the description
                color=0xbfa5d1,
                url=profile_url
            )

            # Add the results to the embed
            embed.set_author(name=f"CSGO Tracker", icon_url=self.config.csgo_tracker_logo, url="https://kwayservices.top")
            embed.add_field(name=f"{self.config.arrow_blue_emoji_id} Steam Level", value=f"`{steam_level}`", inline=True)
            embed.add_field(name=f"{self.config.arrow_pink_emoji_id} CSGO Level", value=f"`{csgo_level} ({level_percentage})`", inline=True)
            embed.add_field(name=f"{self.config.arrow_yellow_emoji_id} Remaining XP", value=f"`{remaining_xp}`", inline=True)
            embed.add_field(name=f"{self.config.arrow_purple_emoji_id} Friend Code", value=f"`{friend_code}`", inline=True)

            if country_code is not None:
                embed.add_field(name=f"{self.config.spinbot_emoji_id} Country Code", value=f"`{country_code}`", inline=True)
            embed.add_field(name=f"{self.config.shield_emoji_id} Medals", value=f"`{len(medals)}`", inline=True)

            if faceit_success:
                embed.add_field(name=f"", value=f"{self.config.faceit_emoji_id} [FACEIT]({faceit_profile_url}){faceit_stats_text}", inline=False)
            else:
                embed.add_field(name=f"{self.config.faceit_emoji_id} Faceit Stats", value=f"```Couldn't fetch faceit stats for this profile```", inline=False)

            embed.add_field(name=f"{self.config.arrow_white_emoji_id} Friendly Commends", value=f"`{friendly_commends}`", inline=True)
            embed.add_field(name=f"{self.config.arrow_green_emoji_id} Leader Commends", value=f"`{leader_commends}`", inline=True)
            embed.add_field(name=f"{self.config.arrow_red_emoji_id} Teacher Commends", value=f"`{teacher_commends}`", inline=True)
            embed.set_thumbnail(url=avatar)

            # Add the medals image if it exists
            if image_path is not None:
                embed.set_image(url=f"attachment://{image_file.filename}")

            embed.set_footer(text=f"CSGO Tracker • Requested by {username}", icon_url=self.config.csgo_tracker_logo)
            embed.timestamp = datetime.utcnow()
        else:
            # If there was an error, send a message with the error
            await interaction.followup.send(f"{self.config.loading_red_emoji_id} There was an error checking the steam ID. Contact the developer if the id format is profile link or steamid64 (correct).", ephemeral=hidden)

        # Edit the message to send the embed and log it to console and logs channel
        if image_path is not None: 
            await requested_message.edit(content=f"{self.config.green_tick_emoji_id} The check has been successfully completed.", embed=embed, attachments=[image_file])
        else:
            await requested_message.edit(content=f"{self.config.green_tick_emoji_id} The check has been successfully completed.", embed=embed)
        await self.logger.discord_log(f"✅ Successfully checked `{id}`. Requested by `{username}`.")
        self.logger.log("INFO", f"✅ Successfully checked `{id}`. Requested by `{username}`.")

        # Delete the image
        await self.medal_handler.delete_image(f"{queue_id}")

        # Check if the user has any of the roles from the admin roles list or has admin permission
        if interaction.user.guild_permissions.administrator:
            await self.logger.discord_log(f"⚠️  {username} has bypassed the timeout because they have admin permissions.")
            self.logger.log("INFO", f"⚠️  {username} has bypassed the timeout because they have admin permissions.")
        else:
            # Add user to timeout list after they have successfully used the command
            adding = self.timeout_manager.add_user(interaction.user.id)

            # Check if the user is already in the timeout list
            if not adding:
                await self.logger.discord_log(f"❌ The user {username} is `already` in the timeout list.")
                self.logger.log("INFO", f"❌ The user {username} is already in the timeout list.")
                return await interaction.followup.send(f"{self.config.loading_red_emoji_id} The user {username} `already` in the timeout list.", ephemeral=hidden)

            # Log that the user has been added to the timeout list
            await self.logger.discord_log(f"⏳ {username} has been added to the timeout list for {self.config.user_timeout} seconds.")
            self.logger.log("INFO", f"⏳ {username} has been added to the timeout list for {self.config.user_timeout} seconds.")

    @check_command.error
    async def check_command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.errors.MissingPermissions):
            return await interaction.response.send_message("❌ You don't have permissions to use this command.", ephemeral=True)
        else:
            return await interaction.response.send_message(f"❌ Error: {error}", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(Check(bot))
    return Logger().log("INFO", "Check command loaded!")