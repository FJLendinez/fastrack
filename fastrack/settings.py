import os
from django.conf.global_settings import *

from typing import List
from starlette.config import Config
from pydantic import AnyHttpUrl
from starlette.datastructures import CommaSeparatedStrings

env = Config('.env')
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env.get('SECRET_KEY', str, 'Bruce Wayne is Batman!')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.get('DEBUG', bool, True)

# Application definition

INSTALLED_APPS = [
    'pixel.apps.PixelConfig'
]

os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env.get('POSTGRES_DB', str, 'fastrack'),
        'USER': env.get('POSTGRES_USER', str, 'fastrackuser'),
        'PASSWORD': env.get('POSTGRES_PASSWORD', str, 'fastrackpass'),
        'HOST': env.get('POSTGRES_HOST', str, 'localhost'),
        'PORT': env.get('POSTGRES_PORT', int, 5800),
    }
}

PROJECT_NAME = "fastrack"

BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

DOMAIN = env.get('PIXEL_DOMAIN', str, 'http://localhost:8000')

PRIVATE_ACCESS_KEYS = list(env.get('PRIVATE_ACCESS_KEYS', CommaSeparatedStrings, ""))
