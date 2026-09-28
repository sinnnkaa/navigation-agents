from fastapi import APIRouter

from app.api.v1 import assistance, events, hazards, realtime, snapshot

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(events.router, tags=["events"])
api_router.include_router(assistance.router, tags=["assistance"])
api_router.include_router(hazards.router, tags=["hazards"])
api_router.include_router(snapshot.router, tags=["snapshot"])
api_router.include_router(realtime.router, tags=["realtime"])
