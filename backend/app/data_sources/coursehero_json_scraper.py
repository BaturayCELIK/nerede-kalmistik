from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import re
import time
import random


class CourseHeroScraper:
    BASE_URL = "https://www.coursehero.com/lit"

    def __init__(
        self,
        book_title: str,
        target_part: int,
        target_chapter: int,
        headless: bool = True
    ):
        self.book_title = book_title
        self.book_slug = self._normalize_title(book_title)
        self.target_part = target_part
        self.target_chapter = target_chapter
        self.headless = headless

    # --------------------------------------------------
    # SLUG
    # --------------------------------------------------
    def _normalize_title(self, title: str) -> str:
        return title.strip().replace(" ", "-")

    # --------------------------------------------------
    # LINK FILTER (SPOILER SAFE)
    # --------------------------------------------------
    def _is_valid_summary_link(self, href: str, text: str) -> bool:
        combined = f"{href} {text}".lower()

        if "summary" not in combined:
            return False

        banned = [
            "epilogue",
            "monologue",
            "analysis",
            "themes",
            "symbol",
            "character"
        ]
        if any(b in combined for b in banned):
            return False

        if "chapter" not in combined and "chapters" not in combined:
            return False

        return True

    # --------------------------------------------------
    # PARSE PART + CHAPTER RANGE (DOĞRU VE GÜVENLİ)
    # --------------------------------------------------
    def _parse_part_and_range(self, href: str, text: str) -> tuple[int, int, int]:
        lower_text = text.lower()
        lower_href = href.lower()

        # PART → URL'DEN
        part_match = re.search(r"part-(\d+)", lower_href)
        if not part_match:
            raise ValueError(f"Part not found in URL: {href}")
        part = int(part_match.group(1))

        # CHAPTER → TEXT'TEN
        chapter_match = re.search(
            r"chapters?\s*(\d+)(?:\D+(\d+))?",
            lower_text
        )

        if not chapter_match:
            raise ValueError(f"Chapter parse failed: {text}")

        start = int(chapter_match.group(1))
        end = int(chapter_match.group(2)) if chapter_match.group(2) else start

        return part, start, end


    # --------------------------------------------------
    # DISCOVERY
    # --------------------------------------------------
    def _discover_all_summaries(self, context) -> list[dict]:
        page = context.new_page()
        url = f"{self.BASE_URL}/{self.book_slug}/"

        page.goto(url, wait_until="domcontentloaded", timeout=20000)
        soup = BeautifulSoup(page.content(), "html.parser")

        summaries = []

        for a in soup.find_all("a", href=True):
            href = a["href"]
            text = a.get_text(strip=True)

            if not self._is_valid_summary_link(href, text):
                continue

            part, start, end = self._parse_part_and_range(href,text)

            # 🔥 ASIL OLAY BURASI
            if part > self.target_part:
                continue   # HİÇ KEŞFETME

            if href.startswith("/"):
                href = f"https://www.coursehero.com{href}"

            summaries.append({
                "part": part,
                "start": start,
                "end": end,
                "url": href
            })

        page.close()

        if not summaries:
            raise RuntimeError("No valid summaries discovered")

        return summaries


    # --------------------------------------------------
    # UNTIL LOGIC (ASIL İŞ KURALI)
    # --------------------------------------------------
    def _select_until(self, summaries: list[dict]) -> list[dict]:
        selected = []

        for s in summaries:
            part = s["part"]
            start = s["start"]
            end = s["end"]

            # Önceki partlar → full
            if part < self.target_part:
                selected.append(s)

            # Target part → SADECE chapter X'i kapsayan
            elif part == self.target_part:
                if start <= self.target_chapter <= end:
                    selected.append(s)

        if not selected:
            raise RuntimeError("UNTIL selection produced empty result")

        selected.sort(key=lambda x: (x["part"], x["start"]))
        return selected


    # --------------------------------------------------
    # HTML → SUMMARY
    # --------------------------------------------------
    def _extract_summary(self, html: str) -> str | None:
        soup = BeautifulSoup(html, "html.parser")

        h2 = soup.find("h2", string=lambda x: x and x.strip() == "Summary")
        if not h2:
            return None

        paragraphs = []
        for el in h2.find_next_siblings():
            if el.name == "h2":
                break
            if el.name == "p":
                text = el.get_text(" ", strip=True)
                if text:
                    paragraphs.append(text)

        return "\n\n".join(paragraphs) if paragraphs else None

    # --------------------------------------------------
    # PUBLIC API
    # --------------------------------------------------
    def fetch_summaries_until(self) -> list[dict]:
        results = []

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=self.headless)
            context = browser.new_context(
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                )
            )
            input("Devam etmek için Enter'a bas...")
            all_summaries = self._discover_all_summaries(context)
            print(all_summaries)
            input("Devam etmek için Enter'a bas...")
            required = self._select_until(all_summaries)

            for s in required:
                page = context.new_page()
                page.goto(s["url"], wait_until="domcontentloaded", timeout=30000)
                html = page.content()
                page.close()

                summary = self._extract_summary(html)
                if summary:
                    results.append({
                        "part": s["part"],
                        "chapters": f"{s['start']}-{s['end']}",
                        "summary": summary
                    })

                time.sleep(random.uniform(1.5, 3.0))

            browser.close()

        return results


def main():
    scraper = CourseHeroScraper(
        book_title="Crime and Punishment",
        target_part=2,
        target_chapter=3,
        headless=False
    )

    summaries = scraper.fetch_summaries_until()

    print("\n===== FINAL SCRAPE RESULT =====\n")

    for s in summaries:
        print(f"Part {s['part']} | Chapters {s['chapters']}")
        print(s["summary"])
        print("\n" + "=" * 60 + "\n")


if __name__ == "__main__":
    main()
