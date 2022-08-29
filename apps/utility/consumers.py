
import json

from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync, sync_to_async

class NotificationConsumer(WebsocketConsumer):
    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['uuid']
        self.room_group_name = 'order_%s' % self.room_name
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    def receive(self, text_data):
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'order_status',
                'payload': text_data
            }
        )

    def send_notification(self, event):
        data = json.loads(event.get('value'))
        self.send(text_data=json.dumps({
            'payload': data
        }))