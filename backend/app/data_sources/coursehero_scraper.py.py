from playwright.sync_api import sync_playwright
import time
import random

class CourseHeroScraper:
    BASE_URL = "https://www.coursehero.com/lit"

    def __init__(self, book_slug: str, book_part: int = 1):
        """
        book_slug: 1984, animal-farm, etc.
        book_part: Book 1, Book 2...
        """
        self.book_slug = book_slug
        self.book_part = book_part

    def _build_chapter_url(self, chapter: int) -> str:
        return (
            f"{self.BASE_URL}/{self.book_slug}/"
            f"book-{self.book_part}-chapter-{chapter}-summary/"
        )

    def _extract_summary_from_page(self, page) -> str:
        page.wait_for_selector("h2:has-text('Summary')", timeout=15000)

        summary = page.evaluate("""
            () => {
                const h2 = [...document.querySelectorAll("h2")]
                    .find(el => el.innerText.trim() === "Summary");

                if (!h2) return null;

                let text = [];
                let el = h2.nextElementSibling;

                while (el && el.tagName === "P") {
                    text.push(el.innerText.trim());
                    el = el.nextElementSibling;
                }

                return text.join("\\n\\n");
            }
        """)

        if not summary:
            raise RuntimeError("Summary not found")

        return summary

    def fetch_chapter_summary(self, page, chapter: int) -> dict | None:
        url = self._build_chapter_url(chapter)
        page.goto(url, wait_until="domcontentloaded", timeout=30000)

        summary = self._extract_summary_from_page(page)

        if not summary:
            print(f"⚠️ Summary not found for chapter {chapter}")
            return None

        return {
            "chapter": chapter,
            "title": f"Book {self.book_part} | Chapter {chapter}",
            "summary": summary
        }


    def fetch_summaries_until(self, chapter: int) -> list:
        results = []

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                )
            )
            page = context.new_page()

            for ch in range(1, chapter + 1):
                print(f"📘 Fetching chapter {ch}...")
                data = self.fetch_chapter_summary(page, ch)

                if data:
                    results.append(data)

                time.sleep(random.uniform(1.5, 3.5))

            browser.close()

        return results

def main():
    scraper = CourseHeroScraper(
        book_slug="1984",
        book_part=1
    )

    chapters = scraper.fetch_summaries_until(chapter=4)

    for ch in chapters:
        print(f"\n===== {ch['title']} =====\n")
        print(ch["summary"])


if __name__ == "__main__":
    main()
