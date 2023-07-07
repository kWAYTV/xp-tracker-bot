import os
from src.util.logger import Logger
from src.helper.config import Config

defaultConfig = """
# CSGO Tacker Discord Bot

# Discord bot prefix
bot_prefix: .
# Discord bot token
discord_token: 
# Discord green tick emoji id
green_tick_emoji_id: 
# Discord green loading emoji id
loading_green_emoji_id: 
# Discord red loading emoji id
loading_red_emoji_id: 
# Discord panel logo emoji:
panel_logo_emoji_id: 
# Arrow blue emoji id
arrow_blue_emoji_id: 
# Arrow purple emoji id
arrow_purple_emoji_id: 
# Arrow pink emoji id
arrow_pink_emoji_id: 
# Arrow yellow emoji id
arrow_yellow_emoji_id: 
# Arrow green emoji id
arrow_green_emoji_id: 
# Arrow red emoji id
arrow_red_emoji_id: 
# Arrow white emoji id
arrow_white_emoji_id: 
# Spinbot emoji id
spinbot_emoji_id: 
# Shield emoji id
shield_emoji_id: 
# Discord emoji id
discord_emoji_id: 
# Faceit emoji id
faceit_emoji_id: 
# Discord logs channel id
logs_channel: 
# Discord queue embed switch
queue_embed_switch: true
# Discord queue embed channel id
queue_embed_channel_id: 
# Discord queue embed message id
queue_embed_message_id: 
# Discord user timeout after order (in seconds)
user_timeout: 300
# Faceit api key
faceit_api_key: 
"""

class FileManager():

    def __init__(self):
        self.logger = Logger()
        self.config = Config()

    # Function to check if the input files are valid
    def check_input(self):

        # if there is no config file, create one.
        if not os.path.isfile("config.yaml"):
            self.logger.log("INFO", "Config file not found, creating one...")
            open("config.yaml", "w+").write(defaultConfig)
            self.logger.log("INFO", "Successfully created config.yml, please fill it out and try again.")
            exit()

        # If the folder "/src/database" doesn't exist, create it.
        if not os.path.exists("src/database"):
            os.makedirs("src/database")