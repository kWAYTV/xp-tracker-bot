import discord
from ruamel.yaml import YAML

class Config:
    def __init__(self):
        self.yaml = YAML()
        self.yaml.preserve_quotes = True
        self.yaml.width = 120
        self.yaml.indent(mapping=2, sequence=4, offset=2)

        with open("config.yaml", "r") as file:
            self.config = self.yaml.load(file)

        # Bot logo
        self.csgo_tracker_logo = "https://i.imgur.com/SdE6a8S.png"

        # Rainbow line gif
        self.rainbow_line_gif = "https://i.imgur.com/mnydyND.gif"

        # Discord
        self.discord_token = self.config["discord_token"]
        self.bot_prefix = self.config["bot_prefix"]
        self.logs_channel = int(self.config["logs_channel"])
        self.dev_guild_id = discord.Object(int(self.config["dev_guild_id"]))
        self.user_timeout = int(self.config["user_timeout"])
        self.queue_embed_switch = self.config["queue_embed_switch"]
        self.queue_embed_channel_id = int(self.config["queue_embed_channel_id"])
        self.queue_embed_message_id = int(self.config["queue_embed_message_id"])
        self.leaderboard_embed_switch = self.config["leaderboard_embed_switch"]
        self.leaderboard_embed_channel_id = int(self.config["leaderboard_embed_channel_id"])
        self.leaderboard_embed_message_id = int(self.config["leaderboard_embed_message_id"])
        self.update_embeds_delay = int(self.config["update_embeds_delay"])
        self.medals_output_dir = self.config["medals_output_dir"]

        # Emoji IDs
        self.loading_green_emoji_id = self.config["loading_green_emoji_id"]
        self.red_cross_emoji_id = self.config["red_cross_emoji_id"]
        self.loading_red_emoji_id = self.config["loading_red_emoji_id"]
        self.green_tick_emoji_id = self.config["green_tick_emoji_id"]
        self.panel_logo_emoji_id = self.config["panel_logo_emoji_id"]
        self.arrow_blue_emoji_id = self.config["arrow_blue_emoji_id"]
        self.arrow_purple_emoji_id = self.config["arrow_purple_emoji_id"]
        self.arrow_pink_emoji_id = self.config["arrow_pink_emoji_id"]
        self.arrow_yellow_emoji_id = self.config["arrow_yellow_emoji_id"]
        self.arrow_green_emoji_id = self.config["arrow_green_emoji_id"]
        self.arrow_red_emoji_id = self.config["arrow_red_emoji_id"]
        self.arrow_white_emoji_id = self.config["arrow_white_emoji_id"]
        self.spinbot_emoji_id = self.config["spinbot_emoji_id"]
        self.shield_emoji_id = self.config["shield_emoji_id"]
        self.discord_emoji_id = self.config["discord_emoji_id"]
        self.faceit_emoji_id = self.config["faceit_emoji_id"]

        # Faceit
        self.faceit_api_key = self.config["faceit_api_key"]

        # XP Tracker
        self.checker_interval = int(self.config["checker_interval"])
        self.discord_tracker_channel_id = int(self.config["discord_tracker_channel_id"])
        self.steam_username = self.config["steam_username"]
        self.steam_password = self.config["steam_password"]
        self.steam_api_key = self.config["steam_api_key"]

    # Function to set queue embed channel ID on the config file
    def set_queue_embed_channel_id(self, channel_id: int):
        self.config["queue_embed_channel_id"] = channel_id
        with open("config.yaml", "w") as file:
            self.yaml.dump(self.config, file)

    # Function to set queue embed message ID on the config file
    def set_queue_embed_message_id(self, message_id: int):
        self.config["queue_embed_message_id"] = message_id
        with open("config.yaml", "w") as file:
            self.yaml.dump(self.config, file)

    # Function to set leaderboard embed channel ID on the config file
    def set_leaderboard_embed_channel_id(self, channel_id: int):
        self.config["leaderboard_embed_channel_id"] = channel_id
        with open("config.yaml", "w") as file:
            self.yaml.dump(self.config, file)

    # Function to set leaderboard embed message ID on the config file
    def set_leaderboard_embed_message_id(self, message_id: int):
        self.config["leaderboard_embed_message_id"] = message_id
        with open("config.yaml", "w") as file:
            self.yaml.dump(self.config, file)