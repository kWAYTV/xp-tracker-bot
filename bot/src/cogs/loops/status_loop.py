import discord
from itertools import cycle
from src.util.logger import Logger
from discord.ext import commands, tasks

class StatusLoop(commands.Cog):

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.logger = Logger()
        self.change_status.start()

    @tasks.loop(seconds=30)
    async def change_status(self):
        # Dynamic activity
        guilds = len(self.bot.guilds)
        users = sum(guild.member_count for guild in self.bot.guilds)
        
        status = cycle([
            f"{guilds} guilds & {users} users",
            "those sweety medals", 
            "csgo rank", 
            "your xp", 
            f"{guilds} guilds & {users} users",
            "your back", 
            "crack accounts", 
            "for 2015 purples",
            f"{guilds} guilds & {users} users",
        ])
        
        await self.bot.change_presence(status=discord.Status.do_not_disturb, activity=discord.Activity(type=discord.ActivityType.watching, name=next(status)))

    @change_status.before_loop
    async def before_change_status(self) -> None:
        return await self.bot.wait_until_ready()

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(StatusLoop(bot))
    return Logger().log("INFO", "Status loop loaded!")
