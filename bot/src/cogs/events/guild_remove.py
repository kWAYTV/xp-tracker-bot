from discord.ext import commands
from src.util.logger import Logger
from src.manager.guild_manager import GuildManager

class GuildRemove(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.logger = Logger(bot)
        self.guild_manager = GuildManager()

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        
        # Check if the guild exists in the database and remove it if it does
        if self.guild_manager.guild_exists(guild.id):
            try:
                self.guild_manager.remove_guild(guild.id)
                self.logger.log("INFO", f"The guild {guild.name} ({guild.id}) has been removed from the bot.")
                await self.logger.discord_log(f"The guild {guild.name} ({guild.id}) has been removed from the bot.")
            except Exception as e:
                await self.logger.log("ERROR", f"An error occurred while trying to remove the guild {guild.name} ({guild.id}) from the database. Error: {e}")
                await self.logger.discord_log(f"An error occurred while trying to remove the guild {guild.name} ({guild.id}) from the database. Error: {e}")
                return

        # Clean possible remaining trash guilds
        self.guild_manager.clean_guilds(self.bot)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(GuildRemove(bot))
    return Logger().log("INFO", "On guild leave event registered!")