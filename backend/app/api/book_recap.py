from app.services.book_recap_service import BookRecapService
from app.data_sources.coursehero_json_scraper import CourseHeroScraper


def main():
    BOOK_TITLE = "Crime and Punishment"
    TARGET_CHAPTER = 2
    PART = None  # None → default part = 1

    # Scraper artık chapter'ı burada alıyor
    scraper = CourseHeroScraper(
        book_title=BOOK_TITLE,
        chapter=TARGET_CHAPTER,
        part=PART,
        headless=False
    )

    service = BookRecapService(scraper)

    recap = service.generate_full_recap(
        book_title=BOOK_TITLE,
        chapter=TARGET_CHAPTER
    )

    print("\n===== FINAL RECAP =====\n")
    print(recap)


if __name__ == "__main__":
    main()
