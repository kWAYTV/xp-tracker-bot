class TrackedUser:
    def __init__(self, steam_id, discord_id, current_level, current_xp, guild_id):
        self.steam_id, self.discord_id, self.current_level, self.current_xp, self.guild_id = steam_id, discord_id, current_level, current_xp, guild_id

    def has_updated(self, level, xp):
        return level != self.current_level or xp != self.current_xp