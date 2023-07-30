from discord.ext import commands
from src.util.logger import Logger
from src.helper.config import Config

class SyncGuildCommand(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.config = Config()
        self.logger = Logger(self.bot)
        return
    
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def syncguild(self, ctx: commands.Context) -> None:
        await ctx.message.delete()
        await self.bot.tree.sync(guild=ctx.guild)
        msg = await ctx.send(f"{self.config.green_tick_emoji_id} Successfully synced guild slash commands!")
        await self.logger.discord_log(f"✅ Successfully synced guild slash commands!")
        self.logger.log("INFO", f"✅ Successfully synced guild slash commands!")
        await msg.delete()
        return

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(SyncGuildCommand(bot))
    return Logger().log("INFO", "Syncguild command loaded!")