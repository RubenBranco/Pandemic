from rest_framework.permissions import BasePermission
from .models import Chat


class UserHasAccessToChat(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return user.is_staff

    def has_object_permission(self, request, view, chat):
        session = chat.session
        user = request.user
        return user == session.owner or session.users.filter(pk=user.pk)

class UserHasAccessToMessage(BasePermission):
    def has_permission(self, request, view):
        chat = Chat.objects.get(pk=int(request.resolver_match.kwargs.get('chat_pk')))
        session = chat.session
        user = request.user
        return user == session.owner or session.users.filter(pk=user.pk)

    def has_object_permission(self, request, view, message):
        session = message.chat.session
        user = request.user
        return user == session.owner or session.users.filter(pk=user.pk)

