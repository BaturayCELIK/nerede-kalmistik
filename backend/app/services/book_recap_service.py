from app.services.llm.gemini import GeminiClient
from app.data_sources.books import BookSummaryClient


class BookRecapService:

    def __init__(self):
        self.book_source = BookSummaryClient()
        self.llm = GeminiClient()

    def _build_raw_text(self, chapters: list) -> str:
        """
        chapters örnek yapı:
        [
          {
            "chapter": 1,
            "title": "Book 1 | Chapter 1",
            "summary": "...."
          },
          ...
        ]
        """
        parts = []
        for ch in chapters:
            parts.append(
                f"Chapter {ch['chapter']} ({ch['title']}): {ch['summary']}"
            )
        return "\n".join(parts)

    def generate_full_recap(
        self,
        book_title: str,
        chapter: int
    ) -> str:
        # 1. Kitap summary datasını al
        chapters = self.book_source.get_summaries_until(
            book_title=book_title,
            chapter=chapter
        )

        # 2. Raw text oluştur
        raw_text = self._build_raw_text(chapters)

        # 3. Prompt hazırla
        prompt = f"""
Below are chapter summaries for the book "{book_title}" up to Chapter {chapter}.
Your task is to create a detailed recap of the story so far and PRODUCE EXACTLY TWO SECTIONS as per the instructions below.

SECTION 1 — CHARACTER CONTEXT
Rules:
- Introduce ONLY the main characters.
- Maximum 1 sentence per character.
- Describe ONLY:
  - who the character is
  - their current role or position in the story
- Do NOT describe events.
- Do NOT mention specific actions or chapters.
- Do NOT include cause–effect explanations.
- Use bullet points.
- Keep this section SHORT and STATIC.

SECTION 2 — STORY RECAP
Rules:
- Write the recap as a continuous story, divided into natural paragraphs.
- Each paragraph must focus on ONLY ONE character or character group.
- Do NOT jump between characters within the same paragraph.
- Early chapters must be summarized briefly.
- Events closer to Chapter {chapter} must be described in more detail.
- Skip minor side events unless they directly affect the current situation.
- Emphasize:
  - turning points
  - unresolved conflicts
  - the character’s current mental or situational state
- Do NOT include headings or labels.
- End the recap with the most recent unresolved tension, realization, or dilemma.

────────────────────────────
OUTPUT RULES
────────────────────────────
- Output language: Turkish.
- Start directly with SECTION 1.
- Do NOT add any commentary or explanations.

CHAPTER SUMMARIES:
{raw_text}
"""

        # 4. Gemini'ye gönder
        return self.llm.generate_recap(prompt)
