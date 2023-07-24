import sqlite3
from src.helper.config import Config

class GuildManager:
    def __init__(self):
        self.config = Config()
        self.connection = sqlite3.connect('src/database/tracker_channels.sqlite')

        # Create table if it doesn't exist
        self.create_table()

    def __del__(self):
        if self.connection:
            self.connection.close()

    def create_table(self):
        with self.connection:
            self.connection.execute('''
                CREATE TABLE IF NOT EXISTS tracking (
                    guild_id BIGINT PRIMARY KEY NOT NULL,
                    channel_id BIGINT NOT NULL
                );
            ''')

    def get_guild(self, guild_id):
        with self.connection:
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
                self.connection.commit()
            return True
        except sqlite3.Error:
            return False

    def remove_guild(self, guild_id):
        try:
            with self.connection:
                self.connection.execute('''
                    DELETE FROM tracking WHERE guild_id = ?
                ''', (guild_id,))
                self.connection.commit()
            return True
        except sqlite3.Error:
            return False

    def update_guild(self, guild_id, channel_id):
        try:
            with self.connection:
                self.connection.execute('''
                    UPDATE tracking SET channel_id = ? WHERE guild_id = ?
                ''', (channel_id, guild_id))
                self.connection.commit()
            return True
        except sqlite3.Error:
            return False

    def guild_exists(self, guild_id):
        with self.connection:
            cursor = self.connection.cursor()
            cursor.execute('''
                SELECT * FROM tracking WHERE guild_id = ?
            ''', (guild_id,))
            return cursor.fetchone() is not None

    async def get_channel_by_guild(self, guild_id):
        with self.connection:
            cursor = self.connection.cursor()
            cursor.execute('''
                SELECT channel_id FROM tracking WHERE guild_id = ?
            ''', (guild_id,))
            result = cursor.fetchone()
            return int(result[0])
        
    def clean_guilds(self, bot):
        bot_guild_ids = [guild.id for guild in bot.guilds]
        with self.connection:
            cursor = self.connection.cursor()
            cursor.execute('''
                SELECT guild_id FROM tracking
            ''')
            db_guild_ids = [row[0] for row in cursor.fetchall()]
            for db_guild_id in db_guild_ids:
                if db_guild_id not in bot_guild_ids:
                    self.remove_guild(db_guild_id)
