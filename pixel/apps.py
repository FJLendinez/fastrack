from django.apps import AppConfig


class PixelConfig(AppConfig):
    name = 'pixel'

    def ready(self):
        from fastrack.urls import api_router
        from pixel.views import router

        api_router.include_router(router, tags=[self.name])