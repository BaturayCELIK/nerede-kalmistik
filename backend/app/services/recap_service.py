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
Below are episode summaries for {title} up to Season {season} Episode {episode}.
Your task is to create a detailed recap of the story so far and PRODUCE EXACTLY TWO SECTIONS as per the instructions below.     

SECTION 1 — CHARACTER CONTEXT
Rules:
- Introduce ONLY the main characters.
- Maximum 1 sentence per character.
- Describe ONLY:
  - who the character is
  - their current role or position in the story
- Do NOT describe events.
- Do NOT mention specific actions or episodes.
- Do NOT include cause–effect explanations.
- Use bullet points.
- Keep this section SHORT and STATIC.

SECTION 2 — STORY RECAP

Rules:
- Write the recap as a continuous story, divided into natural paragraphs.
- Each paragraph must focus on ONLY ONE character or character group.
- Do NOT jump between characters within the same paragraph.
- Early-season events must be summarized briefly.
- Events closer to Season {season} Episode {episode} must be described in more detail.
- Skip minor side events unless they directly affect the current situation.
- Emphasize:
  - turning points
  - conflicts that are still unresolved
  - the character’s current position at the stopping point
- Do NOT include headings or labels.
- End the recap with the most recent unresolved tension or decision.


────────────────────────────
OUTPUT RULES
────────────────────────────
- Output language: Turkish.
- Start directly with SECTION 1.
- Do NOT add any commentary or explanations.


EPISODE SUMMARIES:
{raw_text}
"""

        # 4. LLM'e gönder
        return self.llm.generate_recap(prompt)
