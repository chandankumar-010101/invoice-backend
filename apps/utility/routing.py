from django.conf.urls import url


from .consumers import NotificationConsumer


websocket_urlpatterns = [
    url(r'^notification/(?P<uuid>[a-f0-9-]+)$', NotificationConsumer),

]