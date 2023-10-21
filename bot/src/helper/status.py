from itertools import cycle
from discord.ext import commands
from src.helper.datetime import DateTime
from src.manager.xp_manager import XpManager

class BotStatus:
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.database = XpManager()
        self.datetime_helper = DateTime()

        self.sentences = [
            lambda self: f"Holding {len(self.bot.guilds)} guilds & {sum(guild.member_count for guild in self.bot.guilds)} users.",
            lambda self: f"Tracking {self.database.get_users_count()} users.",
            lambda self: f"XP Reset: {self.datetime_helper.time_until_next_wednesday()} remaining. (GMT+2, Madrid, Spain)",
        ]

        self.status_generator = cycle(self.sentences)

    async def get_status_message(self) -> str:
        sentence_func = next(self.status_generator)
        return sentence_func(self)