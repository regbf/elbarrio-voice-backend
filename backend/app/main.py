from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.health import router as health_router
from app.routes.tools import router as tools_router
from app.routes.analytics import router as analytics_router

app = FastAPI(title="El Barrio Voice Pilot Backend")

# Configuração CORS (deve vir ANTES dos routers)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite todas as origens (para testes)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(health_router)
app.include_router(tools_router)
app.include_router(analytics_router)
