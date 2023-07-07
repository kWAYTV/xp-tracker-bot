import requests
from src.util.logger import Logger
from src.helper.config import Config
from concurrent.futures import ThreadPoolExecutor

class Checker():

    def __init__(self):
        self.logger = Logger()
        self.config = Config()

    # Function to get player info
    def get_player_info(self, id: int, queue_id: str):

        try:
            sid_url = f"https://checker.kwayservices.top/sid/get?id={id}"

            sid_response = requests.get(sid_url)
            sid_response_json = sid_response.json()

            if not sid_response_json["success"]:
                return False, sid_response_json

            steamid64 = sid_response_json["data"].get("id", "None")
            nickname = sid_response_json["data"].get("name", "None")
            avatar = sid_response_json["data"].get("avatar", "None")

            info_url = f"https://checker.kwayservices.top/steam/getmedals?id={steamid64}&queue_id={queue_id}"

            info_response = requests.get(info_url)
            info_response_json = info_response.json()

            if not info_response_json["success"]:
                return False, info_response_json

            profile_url = info_response_json["response"]["player_data"].get("profile_url", "None")
            country_code = info_response_json["response"]["player_data"].get("country_code", "None")

            medal_data = info_response_json["response"].get("medal_data", {})
            steam_level = medal_data.get("steam_level", "None")
            csgo_level = medal_data.get("csgo_level", "None")
            level_percentage = medal_data.get("level_percentage", "None")
            remaining_xp = medal_data.get("remaining_xp", "None")
            commends = medal_data.get("commends", {})
            friendly_commends = commends.get("friendly", "None")
            leader_commends = commends.get("leader", "None")
            teacher_commends = commends.get("teacher", "None")
            medals = medal_data.get("medals", "None")

            json = {
                "steamid64": steamid64,
                "nickname": nickname,
                "avatar": avatar,
                "profile_url": profile_url,
                "country_code": country_code,
                "steam_level": steam_level,
                "csgo_level": csgo_level,
                "level_percentage": level_percentage,
                "remaining_xp": remaining_xp,
                "friendly_commends": friendly_commends,
                "leader_commends": leader_commends,
                "teacher_commends": teacher_commends,
                "medals": medals
            }

            return True, json

        except Exception as e:
            self.logger.log("ERROR", "Error getting player info: " + str(e))
            return False, "Error getting player info: " + str(e)

    # Function to request player info
    def request_player_info(self, id: str, queue_id: str):
        info = self.get_player_info(id, queue_id)
        with ThreadPoolExecutor(max_workers=int(1)) as executor:
                for _ in range(int(1)):
                    executor.submit(lambda: self.get_player_info(id, queue_id))