import sqlite3
from src.util.logger import Logger
from src.helper.trackeduser_class import TrackedUser

class XpManager:
    def __init__(self):
        self.logger = Logger()
        self.connection = sqlite3.connect('src/database/tracked_users.sqlite')
        self.create_table()

    def __del__(self):
        self.connection.close()

    def create_table(self):
        with self.connection:
            self.connection.execute('''
                CREATE TABLE IF NOT EXISTS tracking (
                    steam_id BIGINT PRIMARY KEY NOT NULL,
                    discord_id BIGINT NOT NULL,
                    current_level BIGINT NOT NULL,
                    current_xp BIGINT NOT NULL,
                    guild_id BIGINT NOT NULL
                );
            ''')

    def add_user(self, user: TrackedUser):
        try:
            with self.connection:
                self.connection.execute("INSERT INTO tracking VALUES(?, ?, ?, ?, ?)", (user.steam_id, user.discord_id, user.current_level, user.current_xp, user.guild_id))
            return True
        except sqlite3.Error as e:
            self.logger.log("ERROR", f"Error adding user: {e}")
            return False

    def get_user_by_steam_id(self, steam_id):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM tracking WHERE steam_id = ?", (steam_id,))
        row = cursor.fetchone()
        if row is not None:
            return TrackedUser(*row)
        return None

    def get_users(self):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM tracking")
        rows = cursor.fetchall()
        return [TrackedUser(*row) for row in rows]

    def update_user_level_and_xp(self, steam_id, level, xp):
        try:
            with self.connection:
                self.connection.execute("UPDATE tracking SET current_level = ?, current_xp = ? WHERE steam_id = ?", (level, xp, steam_id))
            return True
        except sqlite3.Error as e:
            self.logger.log("ERROR", f"Error updating user: {e}")
            return False

    def remove_user(self, user: TrackedUser):
        try:
            with self.connection:
                self.connection.execute("DELETE FROM tracking WHERE steam_id = ? AND discord_id = ?", (user.steam_id, user.discord_id))
            return True
        except sqlite3.Error as e:
            self.logger.log("ERROR", f"Error deleting user: {e}")
            return False
        
    # Function to check if the given user id it's the same who added the user to the database
    def check_adding_ownership(self, steam_id, discord_id):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM tracking WHERE steam_id = ? AND discord_id = ?", (steam_id, discord_id))
        row = cursor.fetchone()
        if row is not None:
            return True
        return False