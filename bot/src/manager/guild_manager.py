import sqlite3
from src.helper.config import Config

class GuildManager:
    def __init__(self):
        self.config = Config()
        self.connection = sqlite3.connect('src/database/tracker_channels.sqlite')
        self.create_table()

    def __del__(self):
        self.connection.close()

    def connect_database(self, db_path):
        return sqlite3.connect(db_path)

    def create_table(self):
        with self.connection:
            self.connection.execute('''
                CREATE TABLE IF NOT EXISTS tracking (
                    guild_id BIGINT PRIMARY KEY NOT NULL,
                    channel_id BIGINT NOT NULL
                );
            ''')

    def get_guild(self, guild_id):
        cursor = self.connection.cursor()
        cursor.execute('''
            SELECT * FROM tracking WHERE guild_id = ?
        ''', (guild_id,))
        return cursor.fetchone()
    
    def add_guild(self, guild_id, channel_id):
        try:
            with self.connection:
                self.connection.execute('''
                    INSERT INTO tracking VALUES (?, ?)
                ''', (guild_id, channel_id))
            return True
        except sqlite3.Error:
            return False

    def remove_guild(self, guild_id):
        try:
            with self.connection:
                self.connection.execute('''
                    DELETE FROM tracking WHERE guild_id = ?
                ''', (guild_id,))
            return True
        except sqlite3.Error:
            return False

    def update_guild(self, guild_id, channel_id):
        try:
            with self.connection:
                self.connection.execute('''
                    UPDATE tracking SET channel_id = ? WHERE guild_id = ?
                ''', (channel_id, guild_id))
            return True
        except sqlite3.Error:
            return False

    def get_channel_by_guild(self, guild_id):
        cursor = self.connection.cursor()
        cursor.execute('''
            SELECT channel_id FROM tracking WHERE guild_id = ?
        ''', (guild_id,))
        result = cursor.fetchone()
        if result is not None:
            return int(result[0])  # result is a tuple, we need the first element
        else:
            return self.config.discord_tracker_channel_id