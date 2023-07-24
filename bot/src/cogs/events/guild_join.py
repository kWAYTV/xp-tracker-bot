from discord.ext import commands
from src.util.logger import Logger

class GuildJoin(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.logger = Logger(self.bot)

    @commands.Cog.listener()
    async def on_guild_join(self, guild):

        # Copy the global commands to the guild
        self.bot.tree.copy_global_to(guild=guild)
        await self.bot.tree.sync(guild=guild)

        # Log the event
        self.logger.log("INFO", f"✅ Bot joined Guild: {guild.name}. Syncing commands...")
        await self.logger.discord_log(f"✅ Bot joined Guild: {guild.name}. Syncing commands...")

        # Send a DM to the guild owner
        await guild.owner.send(f"Hello {guild.owner.name}, your guild {guild.name} has successfully synced commands with the bot! To start, use the command `/setup` on your server.")

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(GuildJoin(bot))
    return Logger().log("INFO", "On guild join event registered!")
