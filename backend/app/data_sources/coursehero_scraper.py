from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import time
import random

##YEDEK MIMARI
class CourseHeroScraper:
    BASE_URL = "https://www.coursehero.com/lit"

    def __init__(self, book_slug: str, book_part: int = 1, headless: bool = True):
        self.book_slug = book_slug
        self.book_part = book_part
        self.headless = headless

    # ---------------------------
    # URL BUILDER
    # ---------------------------
    def _build_chapter_url(self, chapter: int) -> str:
        return (
            f"{self.BASE_URL}/{self.book_slug}/"
            f"book-{self.book_part}-chapter-{chapter}-summary/"
        )

    # ---------------------------
    # HTML → SUMMARY PARSER
    # ---------------------------
    def _extract_summary_from_html(self, html: str) -> str | None:
        soup = BeautifulSoup(html, "html.parser")

        h2 = soup.find("h2", string=lambda x: x and x.strip() == "Summary")
        if not h2:
            return None

        paragraphs = []
        for el in h2.find_next_siblings():
            if el.name == "h2":  # Analysis / Themes'e gelince dur
                break
            if el.name == "p":
                text = el.get_text(" ", strip=True)
                if text:
                    paragraphs.append(text)

        if not paragraphs:
            return None

        return "\n\n".join(paragraphs)

    # ---------------------------
    # SINGLE CHAPTER FETCH
    # ---------------------------
    def fetch_chapter_summary(self, context, chapter: int) -> dict | None:
        page = context.new_page()
        url = self._build_chapter_url(chapter)

        try:
            page.goto(url, wait_until="domcontentloaded", timeout=30000)
            html = page.content()

            # gated check
            if "Sign up to unlock" in html or "Create a free account" in html:
                print(f"🚫 Chapter {chapter}: gated content")
                return None

            summary = self._extract_summary_from_html(html)
            if not summary:
                print(f"⚠️ Chapter {chapter}: summary bulunamadı")
                return None

            return {
                "chapter": chapter,
                "title": f"Book {self.book_part} | Chapter {chapter}",
                "summary": summary
            }

        finally:
            page.close()

    # ---------------------------
    # MULTI CHAPTER LOOP
    # ---------------------------
    def fetch_summaries_until(self, max_chapter: int) -> list:
        results = []

        with sync_playwright() as p:
            print(">>> Browser launching <<<")
            browser = p.chromium.launch(headless=self.headless)
            context = browser.new_context(
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                )
            )

            for chapter in range(1, max_chapter + 1):
                print(f"📘 Fetching chapter {chapter}...")
                data = self.fetch_chapter_summary(context, chapter)
                if data:
                    results.append(data)

                time.sleep(random.uniform(1.8, 3.5))

            browser.close()

        return results


# =========================================================
# MAIN / ENTRYPOINT
# =========================================================
if __name__ == "__main__":
    print(">>> MAIN START <<<")

    scraper = CourseHeroScraper(
        book_slug="1984",
        book_part=2,
        headless=False  # debug için False
    )

    chapters = scraper.fetch_summaries_until(6)

    print("\n>>> RESULTS <<<")
    for ch in chapters:
        print(f"\n===== {ch['title']} =====\n")
        print(ch["summary"])

    print("\n>>> MAIN END <<<")
