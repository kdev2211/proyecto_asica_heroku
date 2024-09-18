import json
from channels.generic.websocket import AsyncWebsocketConsumer
import logging

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        if self.scope['user'].is_authenticated:
            self.group_name = f"notificaciones_{self.scope['user'].id}"
        else:
            self.group_name = "notificaciones_generales"  # Grupo general para usuarios no específicos

        # Unirse al grupo
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Salir del grupo
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def notificacion_message(self, event):
        message = event['message']

        # Enviar mensaje al WebSocket
        await self.send(text_data=json.dumps({
            'titulo': message['titulo'],
            'mensaje': message['mensaje'],
            'fecha': message['fecha'],
            'icono': message['icono']
        }))

    # Este método se puede añadir si quieres manejar mensajes personalizados o comandos en el futuro
    async def receive(self, text_data):
        data = json.loads(text_data)
        # Aquí puedes manejar los datos recibidos desde el cliente si es necesario
        # Por ejemplo, si quieres procesar comandos personalizados, puedes hacerlo aquí
        logging.info(f"Mensaje recibido del WebSocket: {data}")