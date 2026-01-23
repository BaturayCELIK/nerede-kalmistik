from app.services.recap_service import RecapService


def main():
    print("=== RECAP PIPELINE TEST ===")

    # Sabit test verisi
    TITLE = "Breaking Bad"
    TARGET_SEASON = 1
    TARGET_EPISODE = 3

    service = RecapService()

    print(f"Dizi: {TITLE}")
    print(f"Hedef: Season {TARGET_SEASON} Episode {TARGET_EPISODE}")
    print("\nRecap üretiliyor...\n")

    final_recap = service.generate_full_recap(
        title=TITLE,
        season=TARGET_SEASON,
        episode=TARGET_EPISODE
    )

    print("===== FINAL RECAP =====\n")
    print(final_recap)


if __name__ == "__main__":
    main()
