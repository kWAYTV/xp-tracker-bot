import sqlite3
from src.helper.config import Config

class AdminModeManager:
    def __init__(self):
        self.config = Config()
        self.connection = sqlite3.connect('src/database/admin_mode.sqlite')

        # Create table if it doesn't exist
        self.create_table()

    def __del__(self):
        if self.connection:
            self.connection.close()

    def create_table(self):
        with self.connection:
            self.connection.execute('''
                CREATE TABLE IF NOT EXISTS admin_mode (
                    guild_id TEXT NOT NULL PRIMARY KEY,
                    status INTEGER NOT NULL DEFAULT 1
                )
            ''')

    def add_admin_mode(self, guild_id, status):
        with self.connection:
            cursor = self.connection.cursor()
            cursor.execute('''
                INSERT INTO admin_mode (guild_id, status) VALUES (?, ?)
            ''', (guild_id, int(status)))
            self.connection.commit()

    def set_admin_mode(self, guild_id, status):
        with self.connection:
            cursor = self.connection.cursor()
            cursor.execute('''
                UPDATE admin_mode SET status = ? WHERE guild_id = ?
            ''', (int(status), guild_id))
            self.connection.commit()

    def get_admin_mode(self, guild_id):
        with self.connection:
            cursor = self.connection.cursor()
            cursor.execute('''
                SELECT status FROM admin_mode WHERE guild_id = ?
            ''', (guild_id,))
            result = cursor.fetchone()
            return bool(result[0]) if result else None

    def delete_admin_mode(self, guild_id):
        with self.connection:
            cursor = self.connection.cursor()
            cursor.execute('''
                DELETE FROM admin_mode WHERE guild_id = ?
            ''', (guild_id,))
            self.connection.commit()
