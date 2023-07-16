import requests, struct
from Cryptodome.Hash import MD5
from src.util.logger import Logger
from src.helper.config import Config
from concurrent.futures import ThreadPoolExecutor

class Checker():

    def __init__(self):
        self.logger = Logger()
        self.config = Config()
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "kWS-Auth"})

    def is_api_online(self):
        try:
            response = self.session.get("https://checker.kwayservices.top")
            if response.status_code == 200:
                return True
            else:
                return False
        except:
            return False

    def friend_code_to_steam64(self, friend_code):
        alphabet = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
        code = "AAAA" + friend_code.replace("-", "")

        result = 0

        for i in range(13):
            index = alphabet.find(code[i])
            if index == -1: return -1
            result = result | (index << 5 * i)

        result, = struct.unpack('<Q', struct.pack('>Q', result))
        account_id = 0

        for i in range(8):
            result = result >> 1
            id_nib = result & 0xF
            result = result >> 4
            account_id = (account_id << 4) | id_nib

        return account_id + 76561197960265728

    def steam64_to_friend_code(self, steam64):
        alphabet = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"

        h = b'CSGO' + struct.pack('>L', int(steam64) - 76561197960265728)
        h, = struct.unpack('<L', MD5.new(h[::-1]).digest()[:4])
        result = 0

        for i in range(8):
            id_nib = (int(steam64) >> (i * 4)) & 0xF
            hash_nib = (h >> i) & 0x1
            a = (result << 4) | id_nib

            result = ((result >> 28) << 32) | a
            result = ((result >> 31) << 32) | ((a << 1) | hash_nib)

        result, = struct.unpack('<Q', struct.pack('>Q', result))
        code = ''

        for i in range(13):
            if i in (4, 9):
                code += '-'

            code += alphabet[result & 31]
            result = result >> 5

        return code[5:]

    # Function to get player steamid64, name and avatar
    def get_persona(self, id: str):

        sid_url = f"https://checker.kwayservices.top/steam/get/steamid?id={id}"

        sid_response = self.session.get(sid_url)
        sid_response_json = sid_response.json()

        if not sid_response_json["success"]:
            return False, sid_response_json, None, None

        steamid64 = sid_response_json["data"].get("id", None)
        nickname = sid_response_json["data"].get("nickname", None)
        avatar = sid_response_json["data"].get("avatar", None)

        return True, steamid64, nickname, avatar

    # Function to get player info
    def get_player_info(self, id: int, queue_id: str):

        try:

            success, steamid64, nickname, avatar = self.get_persona(id)

            info_url = f"https://checker.kwayservices.top/steam/get/medals?id={steamid64}&queueid={queue_id}"

            info_response = self.session.get(info_url)
            info_response_json = info_response.json()

            if not info_response_json["success"]:
                return False, info_response_json

            player_data = info_response_json["data"]["playerData"].get("data", {})
            profile_url = player_data.get("profile_url", None)
            country_code = player_data.get("country_code", None)

            medal_data = info_response_json["data"]["medalData"].get("data", {})
            steam_level = medal_data.get("steam_level", None)
            csgo_level = medal_data.get("csgo_level", None)
            level_percentage = medal_data.get("level_percentage", None)
            remaining_xp = medal_data.get("remaining_xp", None)
            commends = medal_data.get("commends", {})
            friendly_commends = commends.get("friendly", None)
            leader_commends = commends.get("leader", None)
            teacher_commends = commends.get("teacher", None)
            medals = medal_data.get("medals", None)

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