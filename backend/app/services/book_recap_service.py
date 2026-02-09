from app.services.llm.gemini import GeminiClient


class BookRecapService:
    """
    Responsibility:
    - Takes chapter-level summaries
    - Builds a structured prompt
    - Produces a final recap via LLM

    It does NOT:
    - Resolve book titles
    - Scrape websites
    """

    def __init__(self, chapter_source, llm: GeminiClient | None = None):
        """
        chapter_source must implement:
            fetch_summaries_until(max_chapter: int) -> list[dict]
        """
        self.chapter_source = chapter_source
        self.llm = llm or GeminiClient()

    # --------------------------------------------------
    # RAW TEXT BUILDER
    # --------------------------------------------------
    def _build_raw_text(self, chapters: list[dict]) -> str:
        parts: list[str] = []

        for ch in chapters:
            parts.append(
                f"Chapter {ch['chapter']} ({ch['title']}): {ch['summary']}"
            )

        return "\n".join(parts)

    # --------------------------------------------------
    # PUBLIC API
    # --------------------------------------------------
    def generate_full_recap(
        self,
        *,
        book_title: str,
        chapter: int
    ) -> str:
        """
        Generates a spoiler-safe recap up to the given chapter.
        """

        # 1. Fetch chapter summaries
        chapters = self.chapter_source.fetch_summaries_until(
            max_chapter=chapter
        )

        if not chapters:
            raise RuntimeError("No chapter summaries found")

        # 2. Build raw context
        raw_text = self._build_raw_text(chapters)

        # 3. Build prompt
        prompt = self._build_prompt(
            book_title=book_title,
            chapter=chapter,
            raw_text=raw_text
        )

        # 4. Generate recap
        return self.llm.generate_recap(prompt)

    # --------------------------------------------------
    # PROMPT BUILDER
    # --------------------------------------------------
    def _build_prompt(
        self,
        *,
        book_title: str,
        chapter: int,
        raw_text: str
    ) -> str:
        return f"""
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
- Before describing events, briefly experience the atmosphere and environment of the book.
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
""".strip()
