from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from fastapi.middleware.wsgi import WSGIMiddleware

from fastrack.urls import api_router

from django.apps import apps
from fastrack import settings as fastrack_settings
from django.conf import settings

try:
    settings.configure(fastrack_settings)
except RuntimeError:
    pass

apps.populate(settings.INSTALLED_APPS)


app = FastAPI(title=settings.PROJECT_NAME)

# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(api_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, log_level="info")
