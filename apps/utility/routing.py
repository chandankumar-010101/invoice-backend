from django.urls import path


from .consumers import NotificationConsumer


websocket_urlpatterns = [

    path('notification/<str:uuid>', NotificationConsumer.as_asgi()),


]