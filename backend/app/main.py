from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.recap import router as recap_router
from app.api.series import router as series_router

app = FastAPI(
    title="Nerede Kalmıştık API",
    description="Spoiler-safe kitap ve dizi özet servisi",
    version="0.1.0"
)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(recap_router, prefix="/recap")
app.include_router(series_router)

@app.get("/health")
def health_check():
    return {"status": "ok"}
