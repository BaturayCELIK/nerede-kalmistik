from app.services.llm.gemini import GeminiClient
from app.data_sources.tmdb import TMDBClient

class RecapService:

    def __init__(self):
        self.tmdb = TMDBClient()
        self.llm = GeminiClient()

    def _build_raw_text(self, episodes: list) -> str:
        parts = []
        for ep in episodes:
            parts.append(
                f"Season {ep['season']}, Episode {ep['episode']} "
                f"({ep['title']}): {ep['overview']}"
            )
        return "\n".join(parts)

    def generate_full_recap(self, title: str, season: int, episode: int) -> str:
        # 1. TMDb'den raw recap datası
        episodes = self.tmdb.get_recap_until(title, season, episode)

        # 2. Raw recap text oluştur
        raw_text = self._build_raw_text(episodes)

        # 3. Prompt hazırla
        prompt = f"""
Below are episode summaries up to Season {season} Episode {episode}.

TASK:
- Rewrite them into a single, coherent recap
- Explain events step by step
- Do NOT include spoilers beyond this point
- Output must be in Turkish
EPISODE SUMMARIES:
{raw_text}
"""

        # 4. LLM'e gönder
        return self.llm.generate_recap(prompt)
