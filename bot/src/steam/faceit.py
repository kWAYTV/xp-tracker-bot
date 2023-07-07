import requests, pyfaceit
from src.util.logger import Logger
from src.helper.config import Config

class Faceit:
    def __init__(self):
        self.logger = Logger()
        self.config = Config()
        self.session = requests.Session()
        self.session.headers.update({
            'accept': 'application/json',
            'Authorization': f'Bearer {self.config.faceit_api_key}'
        })

    async def get_pyfaceit_stats(self, nickname: str):
        faceit_instance = pyfaceit.Pyfaceit(nickname)
        stats = faceit_instance.player_stats()
        stats_data = {
            'kd_ratio': stats['lifetime']['K/D Ratio'],
            'avrg_headshots': stats['lifetime']['Average Headshots %'],
            'win_rate': stats['lifetime']['Win Rate %'],
            'longest_win_streak': stats['lifetime']['Longest Win Streak'],
            'current_win_streak': stats['lifetime']['Current Win Streak'],
            'avrg_kd_ratio': stats['lifetime']['Average K/D Ratio'],
            'total_matches': stats['lifetime']['Matches'],
            'total_wins': stats['lifetime']['Wins'],
        }
        return stats_data

    async def get_faceit_stats(self, steamid64: str):

        try:
            url = 'https://open.faceit.com/data/v4/players'
            params = {
                'game': 'csgo',
                'game_player_id': steamid64
            }
            response = self.session.get(url, params=params)
            stats = response.json()

            stats_data = {
                'nickname': stats['nickname'],
                'country': stats['country'],
                'faceit_level': stats['games']['csgo']['skill_level'],
                'faceit_elo': stats['games']['csgo']['faceit_elo'],
                'membership_type': stats['memberships'][0],
            }
            
            return True, stats_data
        
        except Exception as e:
            self.logger.log("WARNING", f"Error while getting faceit stats: {e}")
            return False, f"Error while getting faceit stats: {e}"

    async def get_combined_stats(self, steamid64: str):
        success, faceit_stats = await self.get_faceit_stats(steamid64)
        if not success:
            return False, faceit_stats
        pyfaceit_stats = await self.get_pyfaceit_stats(faceit_stats['nickname'])

        combined_stats = [
            f"Nickname: {faceit_stats['nickname']}",
            f"Country: {faceit_stats['country']}",
            f"Faceit Level: {faceit_stats['faceit_level']}",
            f"Faceit Elo: {faceit_stats['faceit_elo']}",
            f"Membership Type: {faceit_stats['membership_type']}",
            f"K/D Ratio: {pyfaceit_stats['kd_ratio']}",
            f"Average Headshots %: {pyfaceit_stats['avrg_headshots']}",
            f"Win Rate %: {pyfaceit_stats['win_rate']}",
            f"Longest Win Streak: {pyfaceit_stats['longest_win_streak']}",
            f"Current Win Streak: {pyfaceit_stats['current_win_streak']}",
            f"Average K/D Ratio: {pyfaceit_stats['avrg_kd_ratio']}",
            f"Total Matches: {pyfaceit_stats['total_matches']}",
            f"Total Wins: {pyfaceit_stats['total_wins']}"
        ]

        combined_stats_str = '\n'.join(combined_stats)
        code_block = f"```{combined_stats_str}```"

        return code_block
