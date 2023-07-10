import time, sqlite3
from src.util.logger import Logger
from src.helper.config import Config

class TimeoutManager:
    def __init__(self):
        self.config = Config()
        self.logger = Logger()
        self.connection = sqlite3.connect('src/database/timeout.sqlite')
        self.create_table()

    def __del__(self):
        self.connection.close()

    def create_table(self):
        with self.connection:
            self.connection.execute('''
                CREATE TABLE IF NOT EXISTS timeout_db (
                    user_id TEXT PRIMARY KEY,
                    timeout REAL
                );
            ''')

    def add_user(self, user_id):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM timeout_db WHERE user_id = ?", (user_id,))
        user = cursor.fetchone()
        if user:
            return False  # User already exists
        try:
            with self.connection:
                self.connection.execute("INSERT INTO timeout_db(user_id, timeout) VALUES(?, ?)", (user_id, time.time()))
            return True  # User added successfully
        except sqlite3.Error as e:
            self.logger.log("ERROR", f"Error adding user: {e}")
            return False  # Error occurred during insertion

    def remove_user(self, user_id):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM timeout_db WHERE user_id = ?", (user_id,))
        user = cursor.fetchone()
        if not user:
            return False  # User does not exist
        try:
            with self.connection:
                self.connection.execute("DELETE FROM timeout_db WHERE user_id = ?", (user_id,))
            return True  # User removed successfully
        except sqlite3.Error as e:
            self.logger.log("ERROR", f"Error removing user: {e}")
            return False  # Error occurred during deletion

    def is_user_in_timeout(self, user_id):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM timeout_db WHERE user_id = ?", (user_id,))
        user = cursor.fetchone()
        if user is None:
            return False, None

        elapsed_time = time.time() - user[1]  # Access the second element of the tuple
        if elapsed_time < self.config.user_timeout:
            return True, self.config.user_timeout - elapsed_time
        else:
            self.remove_user(user_id)
            return False, None
