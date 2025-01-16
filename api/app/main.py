from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from datetime import datetime
from app.core.config import settings
from app.routes import auth, pets, records, reports, tags_metadata
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi.openapi.docs import get_swagger_ui_html
from app.utils.init_data import init_default_templates

class CustomJSONResponse(JSONResponse):
    def render(self, content) -> bytes:
        if isinstance(content, dict):
            for key, value in content.items():
                if isinstance(value, datetime):
                    content[key] = value.astimezone(settings.TIMEZONE).isoformat()
        return super().render(jsonable_encoder(content))

app = FastAPI(
    title="PetWell API",
    description="""
    Pet health management system with comprehensive record keeping and analysis.
    """,
    version=settings.VERSION,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    openapi_tags=tags_metadata,
    default_response_class=CustomJSONResponse
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
app.include_router(reports.router, prefix=settings.API_V1_STR)

# Health check
@app.get("/health")
async def health_check():
    return {"status": "ok", "version": settings.VERSION}

@app.on_event("startup")
async def startup_event():
    init_default_templates()
    print(f"""
🚀 PetWell API is running:
   - API Documentation: http://127.0.0.1:8000/api/docs
   - ReDoc Documentation: http://127.0.0.1:8000/api/redoc
   - Health Check: http://127.0.0.1:8000/health
   - Version: {settings.VERSION}
    """)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 