class TrackedUser:
    def __init__(self, steam_id, discord_id, guild_id, current_level, current_xp, total_earned: int = 0, global_earned: int = 0):
        self.steam_id = steam_id
        self.discord_id = discord_id
        self.guild_id = guild_id
        self.current_level = current_level
        self.current_xp = current_xp
        self.total_earned = total_earned
        self.global_earned = global_earned

    def has_updated(self, new_level, new_xp):
        return self.current_level != new_level or self.current_xp != new_xp