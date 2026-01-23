from fastapi import FastAPI
from app.api.recap import router as recap_router

app = FastAPI(
    title="Nerede Kalmıştık API",
    description="Spoiler-safe kitap ve dizi özet servisi",
    version="0.1.0"
)


app.include_router(recap_router, prefix="/recap")

@app.get("/health")
def health_check():
    return {"status": "ok"}
