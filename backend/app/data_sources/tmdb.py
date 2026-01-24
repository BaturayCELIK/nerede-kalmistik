import os
import requests
from dotenv import load_dotenv

load_dotenv()


class TMDBClient:
    BASE_URL = "https://api.themoviedb.org/3"

    def __init__(self):
        self.api_key = os.getenv("TMDB_API_KEY")
        if not self.api_key:
            raise ValueError("TMDB_API_KEY bulunamadı")

    def search_tv(self, query: str):
        url = f"{self.BASE_URL}/search/tv"
        params = {
            "api_key": self.api_key,
            "query": query,
            "language": "tr-TR"
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()["results"]

    def get_tv_details(self, tv_id: int):
        url = f"{self.BASE_URL}/tv/{tv_id}"
        params = {
            "api_key": self.api_key,
            "language": "tr-TR"
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()

    def get_episode(self, tv_id: int, season: int, episode: int):
        url = f"{self.BASE_URL}/tv/{tv_id}/season/{season}/episode/{episode}"
        params = {
            "api_key": self.api_key,
            "language": "tr-TR"
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()

    def get_recap_until(self, title: str, target_season: int, target_episode: int):
        # 1. TV ID bul
        search_results = self.search_tv(title)
        tv_id = search_results[0]["id"]
        print(f"BULUNAN TV ID: {tv_id}")
        # 2. TV detayları
        tv_details = self.get_tv_details(tv_id)

        recap = []

        for season in tv_details["seasons"]:
            season_number = season["season_number"]

            if season_number == 0:
                continue
            if season_number > target_season:
                break

            max_episode = (
                target_episode
                if season_number == target_season
                else season["episode_count"]
            )

            for ep in range(1, max_episode + 1):
                data = self.get_episode(tv_id, season_number, ep)

                if not data.get("overview"):
                    continue

                recap.append({
                    "season": season_number,
                    "episode": ep,
                    "title": data["name"],
                    "overview": data["overview"]
                })

        return recap
def main():
    client = TMDBClient()

    TITLE = "Better Call Saul"   # burada istediğin diziyi değiştir
    TARGET_SEASON = 2
    TARGET_EPISODE = 10

    print("=== TMDB RECAP DATA TEST ===")
    print(f"Series: {TITLE}")
    print(f"Until: Season {TARGET_SEASON}, Episode {TARGET_EPISODE}")
    print("-----------------------------")

    recap_data = client.get_recap_until(
        title=TITLE,
        target_season=TARGET_SEASON,
        target_episode=TARGET_EPISODE
    )

    if not recap_data:
        print("❌ Hiç recap verisi alınamadı")
        return

    print(f"✅ Toplam bölüm sayısı: {len(recap_data)}\n")

    empty_count = 0

    for item in recap_data:
        print(f"S{item['season']}E{item['episode']} - {item['title']}")

        if not item["overview"].strip():
            print("⚠️  OVERVIEW BOŞ")
            empty_count += 1
        else:
            print(item["overview"])

        print("-" * 50)

    print("\n=== TEST SONUCU ===")
    print(f"Toplam bölüm: {len(recap_data)}")
    print(f"Boş overview sayısı: {empty_count}")


if __name__ == "__main__":
    main()
