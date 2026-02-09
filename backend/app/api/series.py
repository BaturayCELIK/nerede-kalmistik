"""
Series API Router
Provides endpoints for browsing and searching TV series with image caching
"""

from fastapi import APIRouter, Query, HTTPException
from typing import Optional
from functools import lru_cache
from app.data_sources.series_photos import TMDBClient

router = APIRouter(tags=["series"])

# Initialize TMDB client (reused for caching)
@lru_cache(maxsize=1)
def _get_tmdb_client():
    return TMDBClient()


@router.get("/series/popular")
async def get_popular_series(page: int = Query(1, ge=1)):
    """
    Get popular TV series from TMDB with cached images.
    
    Query Parameters:
    - page: Page number (1-indexed)
    
    Returns:
    List of popular series with poster and backdrop images
    """
    try:
        client = _get_tmdb_client()
        data = client.popular_tv(page=page)
        
        series_list = []
        for show in data.get("results", []):
            series_list.append({
                "id": show["id"],
                "title": show.get("name", ""),
                "description": show.get("overview", ""),
                "poster_path": show.get("poster_path"),
                "poster": client.image_url(show.get("poster_path")),
                "backdrop_path": show.get("backdrop_path"),
                "backdrop": client.image_url(show.get("backdrop_path")),
                "rating": show.get("vote_average", 0),
                "genres": [],  # Will be filled for detailed view
                "seasons": 0,  # Will be filled for detailed view
                "episodes": 0,  # Will be filled for detailed view
            })
        
        return {
            "results": series_list,
            "page": data.get("page"),
            "total_pages": data.get("total_pages"),
            "total_results": data.get("total_results"),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching popular series: {str(e)}")


@router.get("/series/trending")
async def get_trending_series(page: int = Query(1, ge=1)):
    """
    Get trending TV series from TMDB.
    
    Query Parameters:
    - page: Page number (1-indexed)
    
    Returns:
    List of trending series with poster and backdrop images
    """
    try:
        client = _get_tmdb_client()
        data = client.trending_tv(page=page)
        
        series_list = []
        for show in data.get("results", []):
            series_list.append({
                "id": show["id"],
                "title": show.get("name", ""),
                "description": show.get("overview", ""),
                "poster": client.image_url(show.get("poster_path")),
                "backdrop": client.image_url(show.get("backdrop_path")),
                "rating": show.get("vote_average", 0),
            })
        
        return {
            "results": series_list,
            "page": data.get("page"),
            "total_pages": data.get("total_pages"),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching trending series: {str(e)}")


@router.get("/series/top-rated")
async def get_top_rated_series(page: int = Query(1, ge=1)):
    """
    Get top-rated TV series from TMDB.
    
    Query Parameters:
    - page: Page number (1-indexed)
    
    Returns:
    List of top-rated series with poster and backdrop images
    """
    try:
        client = _get_tmdb_client()
        data = client.top_rated_tv(page=page)
        
        series_list = []
        for show in data.get("results", []):
            series_list.append({
                "id": show["id"],
                "title": show.get("name", ""),
                "description": show.get("overview", ""),
                "poster": client.image_url(show.get("poster_path")),
                "backdrop": client.image_url(show.get("backdrop_path")),
                "rating": show.get("vote_average", 0),
            })
        
        return {
            "results": series_list,
            "page": data.get("page"),
            "total_pages": data.get("total_pages"),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching top-rated series: {str(e)}")


@router.get("/series/search")
async def search_series(q: str = Query(..., min_length=1), page: int = Query(1, ge=1)):
    """
    Search for TV series by title.
    
    Query Parameters:
    - q: Search query (required)
    - page: Page number (1-indexed)
    
    Returns:
    List of matching series with poster and backdrop images
    """
    try:
        if not q or not q.strip():
            raise HTTPException(status_code=400, detail="Search query cannot be empty")
        
        client = _get_tmdb_client()
        data = client.search_tv(query=q, page=page)
        
        series_list = []
        for show in data.get("results", []):
            series_list.append({
                "id": show["id"],
                "title": show.get("name", ""),
                "description": show.get("overview", ""),
                "poster": client.image_url(show.get("poster_path")),
                "backdrop": client.image_url(show.get("backdrop_path")),
                "rating": show.get("vote_average", 0),
            })
        
        return {
            "results": series_list,
            "page": data.get("page"),
            "total_pages": data.get("total_pages"),
            "total_results": data.get("total_results"),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching series: {str(e)}")


@router.get("/series/{series_id}")
async def get_series_details(series_id: int):
    """
    Get detailed information about a specific TV series including seasons and genres.
    
    Path Parameters:
    - series_id: The TMDB ID of the series
    
    Returns:
    Detailed series information with poster, backdrop, seasons count, and genres
    """
    try:
        client = _get_tmdb_client()
        data = client.tv_details(series_id)
        
        # Extract genre names
        genres = [genre["name"] for genre in data.get("genres", [])]
        
        # Count total episodes
        total_episodes = 0
        seasons_info = data.get("seasons", [])
        for season in seasons_info:
            if season["season_number"] > 0:  # Skip season 0 (specials)
                total_episodes += season.get("episode_count", 0)
        
        return {
            "id": data["id"],
            "title": data.get("name", ""),
            "description": data.get("overview", ""),
            "poster": client.image_url(data.get("poster_path")),
            "backdrop": client.image_url(data.get("backdrop_path")),
            "rating": data.get("vote_average", 0),
            "genres": genres,
            "seasons": len([s for s in seasons_info if s["season_number"] > 0]),
            "episodes": total_episodes,
            "first_air_date": data.get("first_air_date"),
            "last_air_date": data.get("last_air_date"),
            "networks": [net.get("name") for net in data.get("networks", [])],
            "seasons_info": [
                {
                    "season": s["season_number"],
                    "episodes": s.get("episode_count", 0)
                }
                for s in seasons_info
                if s["season_number"] > 0
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Series not found or error fetching details: {str(e)}")


@router.get("/series/{series_id}/season/{season_number}")
async def get_season_details(series_id: int, season_number: int):
    """
    Get details about a specific season including episode count.
    
    Path Parameters:
    - series_id: The TMDB ID of the series
    - season_number: The season number
    
    Returns:
    Season information including episode count
    """
    try:
        client = _get_tmdb_client()
        data = client.tv_details(series_id)
        
        # Find the specific season
        seasons_info = data.get("seasons", [])
        season_data = next(
            (s for s in seasons_info if s["season_number"] == season_number),
            None
        )
        
        if not season_data:
            raise HTTPException(status_code=404, detail=f"Season {season_number} not found")
        
        return {
            "season": season_number,
            "episodes": season_data.get("episode_count", 0),
            "air_date": season_data.get("air_date"),
            "poster": client.image_url(season_data.get("poster_path")),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching season details: {str(e)}")
