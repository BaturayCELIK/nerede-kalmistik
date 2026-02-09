"""
Recap API Router
Provides endpoints for generating AI-powered recaps for series and books
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.services.recap_service import RecapService
from app.services.book_recap_service import BookRecapService
from app.data_sources.coursehero_json_scraper import CourseHeroScraper

router = APIRouter(tags=["recap"])


class SeriesRecapRequest(BaseModel):
    title: str
    season: int
    episode: int


class BookRecapRequest(BaseModel):
    title: str
    chapter: int
    part: Optional[int] = None


class RecapResponse(BaseModel):
    characterContext: list[str]
    storyRecap: str
    generatedAt: str


@router.post("/series", response_model=RecapResponse)
async def get_series_recap(request: SeriesRecapRequest):
    """
    Generate an AI recap for a TV series up to a specific season and episode.
    
    Request Body:
    - title: TV series title (e.g., "Breaking Bad")
    - season: Target season number
    - episode: Target episode number
    
    Returns:
    Recap with character context and story summary
    """
    try:
        service = RecapService()
        recap_text = service.generate_full_recap(
            title=request.title,
            season=request.season,
            episode=request.episode
        )
        
        # Parse the recap into sections (character context + story recap)
        sections = recap_text.split("SECTION 2 —")
        
        character_context = []
        story_recap = ""
        
        if len(sections) >= 1:
            # Extract character context bullets
            context_text = sections[0].replace("SECTION 1 —", "").replace("CHARACTER CONTEXT", "").strip()
            character_context = [
                line.strip()
                for line in context_text.split("\n")
                if line.strip().startswith("•") or (line.strip() and not line.strip().startswith("-"))
            ]
        
        if len(sections) == 2:
            story_recap = sections[1].replace("STORY RECAP", "").strip()
        
        return RecapResponse(
            characterContext=character_context or ["Unable to parse character context"],
            storyRecap=story_recap or recap_text,
            generatedAt=""
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=f"Series not found: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating recap: {str(e)}")


@router.post("/book", response_model=RecapResponse)
async def get_book_recap(request: BookRecapRequest):
    """
    Generate an AI recap for a book up to a specific chapter.
    
    Request Body:
    - title: Book title (e.g., "Crime and Punishment")
    - chapter: Target chapter number
    - part: Optional part number (for multi-part books)
    
    Returns:
    Recap with character context and story summary
    """
    try:
        # Initialize scraper
        scraper = CourseHeroScraper(
            book_title=request.title,
            chapter=request.chapter,
            part=request.part or 1,
            headless=True
        )
        
        # Generate recap
        service = BookRecapService(scraper)
        recap_text = service.generate_full_recap(
            book_title=request.title,
            chapter=request.chapter
        )
        
        # Parse the recap into sections
        sections = recap_text.split("SECTION 2 —")
        
        character_context = []
        story_recap = ""
        
        if len(sections) >= 1:
            context_text = sections[0].replace("SECTION 1 —", "").replace("CHARACTER CONTEXT", "").strip()
            character_context = [
                line.strip()
                for line in context_text.split("\n")
                if line.strip().startswith("•") or (line.strip() and not line.strip().startswith("-"))
            ]
        
        if len(sections) == 2:
            story_recap = sections[1].replace("STORY RECAP", "").strip()
        
        return RecapResponse(
            characterContext=character_context or ["Unable to parse character context"],
            storyRecap=story_recap or recap_text,
            generatedAt=""
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating book recap: {str(e)}")


# Test endpoint (for development)
def main():
    """Test function for local development"""
    print("=== RECAP PIPELINE TEST ===")

    # Fixed test data
    TITLE = "Dexter"
    TARGET_SEASON = 6
    TARGET_EPISODE = 2

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

