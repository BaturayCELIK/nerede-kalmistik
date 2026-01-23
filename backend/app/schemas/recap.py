from pydantic import BaseModel

class RecapRequest(BaseModel):
    title: str
    media_type: str  # book | tv
    progress: str    # Chapter 5 | S2E3

class RecapResponse(BaseModel):
    summary: str
