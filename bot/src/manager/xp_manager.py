import sqlite3
from datetime import datetime
from src.util.logger import Logger
from src.helper.trackeduser_class import TrackedUser

class XpManager:
    def __init__(self):
        self.logger = Logger()
        self.connection = sqlite3.connect('src/database/tracked_users.sqlite')

        # Create table if it doesn't exist
        self.create_table()

        # Check if reset_month has been set, otherwise set it to the current month
        self.check_reset_month()

    def __del__(self):
        self.connection.close()

    # Function to create the table if it doesn't exist
    def create_table(self):
        with self.connection:
            self.connection.execute('''
                CREATE TABLE IF NOT EXISTS tracking (
                    steam_id BIGINT PRIMARY KEY NOT NULL,
                    discord_id BIGINT NOT NULL,
                    current_level BIGINT NOT NULL,
                    current_xp BIGINT NOT NULL,
                    guild_id BIGINT NOT NULL,
                    total_earned BIGINT DEFAULT 0 NOT NULL
                );
            ''')
            # Create a new table to store the reset month
            self.connection.execute('''
                CREATE TABLE IF NOT EXISTS reset_month_table (
                    id INTEGER PRIMARY KEY,
                    reset_month INT DEFAULT NULL
                );
            ''')

    # Function to add a user to the database
    def add_user(self, user: TrackedUser):
        try:
            with self.connection:
                self.connection.execute("INSERT INTO tracking VALUES (?, ?, ?, ?, ?, ?)", (user.steam_id, user.discord_id, user.current_level, user.current_xp, user.guild_id, user.total_earned))
            return True
        except sqlite3.Error as e:
            self.logger.log("ERROR", f"Error adding user to tracker database: {e}")
            return False

    # Function to get a user from the database by steam id
    def get_user_by_steam_id(self, steam_id):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM tracking WHERE steam_id = ?", (steam_id,))
        row = cursor.fetchone()
        if row is not None:
            return TrackedUser(*row)
        return None

    # Function to get all users from the database
    def get_users(self):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM tracking")
        rows = cursor.fetchall()
        return [TrackedUser(*row) for row in rows]

    # Function to update the data of a user
    def update_user_level_and_xp(self, steam_id, level, xp, total_earned):
        try:
            with self.connection:
                self.connection.execute("UPDATE tracking SET current_level = ?, current_xp = ?, total_earned = ? WHERE steam_id = ?", (level, xp, total_earned, steam_id))
            return True
        except sqlite3.Error as e:
            self.logger.log("ERROR", f"Error updating user level & xp: {e}")
            return False

    # Function to remove a user from the database
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
    
    # Function to change users guild    
    def change_guild(self, steam_id, guild_id):
        try:
            with self.connection:
                self.connection.execute("UPDATE tracking SET guild_id = ? WHERE steam_id = ?", (guild_id, steam_id))
            return True
        except sqlite3.Error as e:
            self.logger.log("ERROR", f"Error changing user guild: {e}")
            return False

    # Function to get all users from the database sorted by total earned
    def get_users_sorted_by_total_earned(self):
        cursor = self.connection.cursor()
        cursor.execute("SELECT steam_id, total_earned FROM tracking ORDER BY total_earned DESC")
        rows = cursor.fetchall()
        return rows  # this will be a list of tuples, where each tuple is (discord_id, total_earned)
    
    # Function to check if reset_month has been set, otherwise set it to the current month
    def check_reset_month(self):
        reset_month = self.connection.execute("SELECT reset_month FROM reset_month_table WHERE id = 1").fetchone()
        reset_month = reset_month[0] if reset_month is not None else None
        if reset_month is None:
            actual_month = datetime.today().month
            try:
                with self.connection:
                    self.connection.execute("INSERT OR REPLACE INTO reset_month_table(id, reset_month) VALUES (1, ?)", (actual_month,))
                return True
            except sqlite3.Error as e:
                self.logger.log("ERROR", f"Error setting reset month: {e}")
                return False
        return True

    # Function to check if we need to reset total_earned
    def should_reset(self):
        today = datetime.today()
        reset_month = self.connection.execute("SELECT reset_month FROM reset_month_table WHERE id = 1").fetchone()
        reset_month = reset_month[0] if reset_month is not None else None
        return today.day == 1 and today.month != reset_month

    # Function to set every user's total earned to 0
    def reset_total_earned(self):
        actual_month = datetime.today().month
        try:
            with self.connection:
                self.connection.execute("UPDATE tracking SET total_earned = 0")
                self.connection.execute("INSERT OR REPLACE INTO reset_month_table(id, reset_month) VALUES (1, ?)", (actual_month,))
            return True
        except sqlite3.Error as e:
            self.logger.log("ERROR", f"Error resetting total earned: {e}")
            return False