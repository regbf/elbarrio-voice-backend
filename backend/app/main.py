from fastapi import FastAPI
from app.routes.health import router as health_router
from app.routes.tools import router as tools_router
from app.routes.analytics import router as analytics_router

app = FastAPI(title="El Barrio Voice Pilot Backend")

app.include_router(health_router)
app.include_router(tools_router)
app.include_router(analytics_router)