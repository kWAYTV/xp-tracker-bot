from ruamel.yaml import YAML

class Config:
    def __init__(self):
        self.yaml = YAML()
        self.yaml.preserve_quotes = True
        self.yaml.width = 120
        self.yaml.indent(mapping=2, sequence=4, offset=2)

        with open("config.yaml", "r") as file:
            self.config = self.yaml.load(file)

        self.csgo_tracker_logo = "https://i.imgur.com/SdE6a8S.png"
        self.queue_embed_switch = self.config["queue_embed_switch"]
        self.queue_embed_channel_id = int(self.config["queue_embed_channel_id"])
        self.queue_embed_message_id = int(self.config["queue_embed_message_id"])
        self.discord_token = self.config["discord_token"]
        self.bot_prefix = self.config["bot_prefix"]
        self.logs_channel = int(self.config["logs_channel"])
        self.loading_green_emoji_id = self.config["loading_green_emoji_id"]
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
        self.user_timeout = int(self.config["user_timeout"])
        self.faceit_api_key = self.config["faceit_api_key"]

    def set_queue_embed_channel_id(self, channel_id: int):
        self.config["queue_embed_channel_id"] = channel_id
        with open("config.yaml", "w") as file:
            self.yaml.dump(self.config, file)

    def set_queue_embed_message_id(self, message_id: int):
        self.config["queue_embed_message_id"] = message_id
        with open("config.yaml", "w") as file:
            self.yaml.dump(self.config, file)