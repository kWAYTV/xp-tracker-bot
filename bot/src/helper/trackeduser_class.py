class TrackedUser:
    def __init__(self, steam_id, discord_id, current_level, current_xp, guild_id, total_earned = 0):
        self.steam_id = steam_id
        self.discord_id = discord_id
        self.current_level = current_level
        self.current_xp = current_xp
        self.guild_id = guild_id
        self.total_earned = total_earned

    def has_updated(self, level, xp):
        return level != self.current_level or xp != self.current_xp