import discord, secrets
from discord import File
from datetime import datetime
from discord.ext import commands
from discord import app_commands
from src.util.utils import Utils
from src.util.logger import Logger
from src.steam.faceit import Faceit
from src.helper.config import Config
from src.handler.medal_handler import MedalHandler
from src.handler.queue_handler import QueueHandler
from src.manager.timeout_manager import TimeoutManager

class Order(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.utils = Utils()
        self.config = Config()
        self.faceit = Faceit()
        self.logger = Logger(self.bot)
        self.queue_handler = QueueHandler()
        self.medal_handler = MedalHandler()
        self.timeout_manager = TimeoutManager()

    # Spam bot command  
    @app_commands.command(name="check", description=f"Add some steam profile to the queue to be checked.")
    async def order_command(self, interaction: discord.Interaction, id: str, hidden: bool = True):
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

        # Tell the user that the bot is working on their order and log it to console and logs channel
        requested_message = await interaction.followup.send(f"{self.config.loading_green_emoji_id} Requested `{id}` to be checked.", ephemeral=hidden)
        await self.logger.discord_log(f"⌛ Requested `{id}` to be checked. Requested by `{username}`.")
        self.logger.log("INFO", f"⌛ Requested `{id}` to be checked.. Requested by {username}")

        # Create an embed to send to the user
        embed = discord.Embed(title=f"{self.config.loading_green_emoji_id} Successfully added!", description=f"Checking added to the queue.\nQueued steam ID: `{id}`.", color=0x00ff00)
        embed.set_thumbnail(url=self.config.csgo_tracker_logo)
        embed.set_footer(text=f"CSGO Tracker • Requested by {username}")
        embed.timestamp = datetime.utcnow()

        # Edit the message to send the embed and log it to console and logs channel
        await requested_message.edit(content=f"{self.config.loading_green_emoji_id} The order has been added to the queue.", embed=embed)
        await self.logger.discord_log(f"✅ Successfully added `{id}` to the queue. Requested by `{username}`.")
        self.logger.log("INFO", f"✅ Successfully added `{id}` to the queue. Requested by `{username}`")

        # Generate a random queue ID
        queue_id = f"KWS{secrets.token_hex(6)}"

        self.queue_handler.push_order({'steamid64': id, 'queue_id': queue_id,'requested_by': int(interaction.user.id)})
        await self.queue_handler.force_check_start()

        # Get the results of the check
        success, result = self.queue_handler.get_check_results(id)

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
            faceit_success, faceit_stats_text = await self.faceit.get_combined_stats(steamid64)

            # Get the medals image
            image_path = await self.medal_handler.get_image_path(f"{queue_id}")
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
            embed.add_field(name=f"{self.config.arrow_pink_emoji_id} CSGO Level", value=f"`{csgo_level}`", inline=True)
            embed.add_field(name=f"{self.config.arrow_purple_emoji_id} Lvl Percentage", value=f"`{level_percentage}`", inline=True)
            embed.add_field(name=f"{self.config.arrow_yellow_emoji_id} Remaining XP", value=f"`{remaining_xp}`", inline=True)
            if country_code is not None:
                embed.add_field(name=f"{self.config.spinbot_emoji_id} Country Code", value=f"`{country_code}`", inline=True)
            embed.add_field(name=f"{self.config.shield_emoji_id} Medals", value=f"`{len(medals)}`", inline=True)
            if faceit_success:
                embed.add_field(name=f"{self.config.faceit_emoji_id} Faceit Stats", value=f"{faceit_stats_text}", inline=False)
            else:
                embed.add_field(name=f"{self.config.faceit_emoji_id} Faceit Stats", value=f"```Couldn't fetch faceit stats for this profile```", inline=False)
            embed.add_field(name=f"{self.config.arrow_white_emoji_id} Friendly Commends", value=f"`{friendly_commends}`", inline=True)
            embed.add_field(name=f"{self.config.arrow_green_emoji_id} Leader Commends", value=f"`{leader_commends}`", inline=True)
            embed.add_field(name=f"{self.config.arrow_red_emoji_id} Teacher Commends", value=f"`{teacher_commends}`", inline=True)
            embed.set_thumbnail(url=avatar)
            embed.set_image(url=f"attachment://{image_file.filename}")
            embed.set_footer(text=f"CSGO Tracker • Requested by {username}", icon_url=self.config.csgo_tracker_logo)
            embed.timestamp = datetime.utcnow()
        elif not faceit_success:
            # If there was an error, send a message with the error
            await interaction.followup.send(f"{self.config.loading_red_emoji_id} There was an error checking the faceit stats. Contact the developer if the profile has faceit profile and this is happening.", ephemeral=hidden)
        else:
            # If there was an error, send a message with the error
            await interaction.followup.send(f"{self.config.loading_red_emoji_id} There was an error checking the steam ID. Contact the developer if the id format is profile link or steamid64 (correct).", ephemeral=hidden)

        # Edit the message to send the embed and log it to console and logs channel
        await requested_message.edit(content=f"{self.config.green_tick_emoji_id} The check has been successfully completed.", embed=embed, attachments=[image_file])
        #await interaction.followup.send(file=image_file, ephemeral=hidden)
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
                await self.logger.discord_log(f"❌ The user {username} `already` in the timeout list.")
                self.logger.log("INFO", f"❌ The user {username} already in the timeout list.")
                return await interaction.followup.send(f"{self.config.loading_red_emoji_id} The user {username} `already` in the timeout list.", ephemeral=hidden)

            
            # Log that the user has been added to the timeout list
            await self.logger.discord_log(f"⏳ {username} has been added to the timeout list for {self.config.user_timeout} seconds.")
            self.logger.log("INFO", f"⏳ {username} has been added to the timeout list for {self.config.user_timeout} seconds.")

    @order_command.error
    async def order_command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.errors.MissingPermissions):
            return await interaction.response.send_message("❌ You don't have permissions to use this command.", ephemeral=True)
        else:
            return await interaction.response.send_message(f"❌ Error: {error}", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(Order(bot))
    return Logger().log("INFO", "Order command loaded!")