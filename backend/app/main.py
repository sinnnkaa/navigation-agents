from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI

from app.api.v1.router import api_router
from app.ioc import build_container

app = FastAPI(title="Навигационная память — API")
setup_dishka(build_container(), app)
app.include_router(api_router)


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}
