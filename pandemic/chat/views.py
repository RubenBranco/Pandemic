import copy
from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets
from rest_framework.response import Response
from .models import Chat, Message
from .serializers import MessageSerializer, ChatSerializer
from .permissions import UserHasAccessToChat, UserHasAccessToMessage
from game.models import Session


class ChatViewSet(viewsets.ModelViewSet):
    queryset = Chat.objects.all()
    serializer_class = ChatSerializer
    permission_classes = [UserHasAccessToChat]


class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer
    permission_classes = [UserHasAccessToMessage]

    def get_queryset(self):
        queryset = Message.objects.filter(chat=self.kwargs['chat_pk']).order_by("date_time")
        last_message = self.request.query_params.get("last_comment", None)
        if last_message is not None:
            queryset = queryset.filter(id__gt=last_message)
        return queryset

    def create(self, request, chat_pk):
        serializer = MessageSerializer(data=request.data, many=False)
        if serializer.is_valid(raise_exception=True):
            message = serializer.save(chat=get_object_or_404(Chat, pk=chat_pk), sender=request.user)
        serializer = MessageSerializer(message)
        return Response(serializer.data)