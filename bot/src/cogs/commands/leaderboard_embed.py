import discord
from discord.ext import commands
from discord import app_commands
from src.util.logger import Logger
from src.helper.config import Config
from src.helper.datetime import DateTime
from src.cogs.loops.update_leaderboard_loop import UpdateLeaderboardLoop

class LeaderboardEmbed(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.config = Config()
        self.datetime_helper = DateTime()
        self.update_leaderboard_loop = UpdateLeaderboardLoop(bot)

    # LeaderboardEmbed bot command
    @app_commands.command(name="leaderboard_embed", description="Creates and sets the leaderboard embed.")
    @app_commands.checks.has_permissions(administrator=True)
    async def leaderboard_embed_command(self, interaction: discord.Interaction):
        await interaction.response.defer()

        if not self.config.leaderboard_embed_switch:
            return await interaction.followup.send("{self.config.red_cross_emoji_id} Leaderboard embed is disabled in the config! Enable it and restart the bot.", ephemeral=True)
        
        embed = discord.Embed(title="🏆 XP Leaderboard.", color=0xb34760)
        embed.set_footer(text="CSGO Tracker • discord.gg/kws", icon_url=self.config.csgo_tracker_logo)
        embed.set_thumbnail(url=self.config.csgo_tracker_logo)
        embed.timestamp = self.datetime_helper.get_current_timestamp()

        leaderboard_embed_message = await interaction.followup.send(embed=embed)

        self.config.set_leaderboard_embed_channel_id(leaderboard_embed_message.channel.id)
        self.config.set_leaderboard_embed_message_id(leaderboard_embed_message.id)

        await interaction.followup.send("✅ Leaderboard embed created and values set in the config! Updating it soon...", ephemeral=True)
        await self.update_leaderboard_loop.force_update_leaderboard_embed()

    @leaderboard_embed_command.error
    async def leaderboard_embed_command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.errors.MissingPermissions):
            await interaction.response.send_message(f"{self.config.red_cross_emoji_id} You don't have permissions to use this command.", ephemeral=True)
        else:
            await interaction.response.send_message(f"Error: {error}", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(LeaderboardEmbed(bot), guild=discord.Object(id=Config().dev_guild_id))
    return Logger().log("INFO", "Leaderboard embed command loaded!")
