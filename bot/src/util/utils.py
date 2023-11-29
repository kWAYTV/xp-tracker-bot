class Utils:

    def __init__(self):
        pass

    @staticmethod
    def clean_discord_username(username: str) -> str:
        username_split = username.split("#")
        if username_split[1] == "0":
            return f"@{username_split[0]}"
        else:
            return username
