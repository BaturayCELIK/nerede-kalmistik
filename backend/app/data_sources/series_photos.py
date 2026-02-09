import os
import requests


class TMDBClient:
    BASE_URL = "https://api.themoviedb.org/3"
    IMAGE_BASE = "https://image.tmdb.org/t/p/w500"

    def __init__(self):
        self.key = os.getenv("TMDB_API_KEY")

        if not self.key:
            raise ValueError("TMDB_API_KEY bulunamadı")

        # v4 token (JWT genelde eyJ ile başlar)
        self.is_v4 = self.key.startswith("eyJ")

        if self.is_v4:
            self.headers = {
                "Authorization": f"Bearer {self.key}",
                "accept": "application/json"
            }
            self.params = {"language": "tr-TR"}
        else:
            self.headers = {}
            self.params = {
                "api_key": self.key,
                "language": "tr-TR"
            }

    # ------------------------
    # Core request helper
    # ------------------------
    def _get(self, path: str, params: dict | None = None):
        url = f"{self.BASE_URL}{path}"
        merged_params = self.params.copy()

        if params:
            merged_params.update(params)

        response = requests.get(
            url,
            headers=self.headers,
            params=merged_params,
            timeout=10
        )
        response.raise_for_status()
        return response.json()

    # ------------------------
    # TV endpoints
    # ------------------------
    def trending_tv(self, page: int = 1):
        return self._get("/trending/tv/week", {"page": page})

    def popular_tv(self, page: int = 1):
        return self._get("/tv/popular", {"page": page})

    def top_rated_tv(self, page: int = 1):
        return self._get("/tv/top_rated", {"page": page})

    def search_tv(self, query: str, page: int = 1):
        return self._get(
            "/search/tv",
            {
                "query": query,
                "page": page,
                "include_adult": False
            }
        )

    def tv_details(self, tv_id: int):
        return self._get(f"/tv/{tv_id}")

    def tv_images(self, tv_id: int):
        return self._get(f"/tv/{tv_id}/images")

    # ------------------------
    # Helpers
    # ------------------------
    def image_url(self, path: str | None):
        if not path:
            return None
        return f"{self.IMAGE_BASE}{path}"
