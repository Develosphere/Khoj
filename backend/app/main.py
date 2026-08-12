from fastapi import FastAPI
from app.core.config import settings

app = FastAPI()

@app.get("/health")
async def health_check():
    return {"status": "ok", "supabase_url": settings.SUPABASE_URL}
