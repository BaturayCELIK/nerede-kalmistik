import os
from dotenv import load_dotenv

load_dotenv()

TMDB_API_KEY = os.getenv("TMDB_API_KEY")
TMDB_BASE_URL = os.getenv("TMDB_BASE_URL")

if not TMDB_API_KEY:
    raise RuntimeError("TMDB_API_KEY is not set")
