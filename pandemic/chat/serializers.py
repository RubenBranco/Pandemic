from rest_framework.serializers import ModelSerializer, CharField, DateTimeField, IntegerField
from .models import Message, Chat

class MessageSerializer(ModelSerializer):
    sender = CharField(source='sender.username', required=False)
    date_time = DateTimeField(format="%x %X", required=False)
    
    class Meta:
        model = Message
        exclude = ('chat', )


class ChatSerializer(ModelSerializer):
    class Meta:
        model = Chat
        fields = '__all__'
        
