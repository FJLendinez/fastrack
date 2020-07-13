from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from fastapi.middleware.wsgi import WSGIMiddleware

from fastrack.urls import api_router

from django.apps import apps
from fastrack import settings as fastrack_settings
from django.conf import settings

settings.configure(fastrack_settings)
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

