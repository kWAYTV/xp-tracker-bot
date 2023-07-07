from discord.ext import commands
from src.util.logger import Logger
from src.helper.config import Config

class SyncCommand(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.config = Config()
        self.logger = Logger(self.bot)
        return
    
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def sync(self, ctx: commands.Context) -> None:
        await ctx.message.delete()
        await self.bot.tree.sync()
        msg = await ctx.send(f"{self.config.green_tick_emoji_id} Successfully synced slash commands!")
        await self.logger.discord_log(f"✅ Successfully synced slash commands!")
        self.logger.log("INFO", f"✅ Successfully synced slash commands!")
        await msg.delete()
        return

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(SyncCommand(bot))
    return Logger().log("INFO", "Sync command loaded!")