from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.routes import auth, pets, records, tags_metadata

app = FastAPI(
    title="PetWell API",
    description="""
    PetWell API - Your Pet's Health Management System
    
    ## Features
    * 👤 User authentication and management
    * 🐾 Pet profile management
    * ⚕️ Health records tracking
    * 📊 Weight monitoring
    * 💉 Vaccination records
    """,
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    openapi_tags=tags_metadata
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(pets.router, prefix=settings.API_V1_STR)
app.include_router(records.router, prefix=settings.API_V1_STR)

# Health check
@app.get("/health")
async def health_check():
    return {"status": "ok"} 