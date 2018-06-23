from rest_framework.permissions import BasePermission
from .models import Session

class UserHasAccessToSession(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        pk = view.kwargs.get('pk')
        if pk is not None:
            session = Session.objects.get(pk=view.kwargs.get("pk"))
            return user.is_staff or session.owner == user or session.users.filter(pk=user.pk)
        return True

    def has_object_permission(self, request, view, session):
        user = request.user
        if view.action != 'partial_update':
            return user == session.owner or session.users.filter(pk=user.pk)
        return user == session.owner 

class UserHasAccessToSessionParticipants(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        session = Session.objects.get(pk=request.resolver_match.kwargs.get("session_hash_pk"))
        return session.owner == user or session.users.filter(pk=user.pk)
    
    def has_object_permission(self, request, view, state):
        user = request.user
        session = state.session
        return user == session.owner or session.users.filter(pk=user.pk)

class UserHasAccessToState(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        session = Session.objects.get(pk=request.resolver_match.kwargs.get("session_hash_pk"))
        return user == session.owner or session.users.filter(pk=user.pk)

    def has_object_permission(self, request, view, state):
        user = request.user
        session = state.session.session
        if view.action == 'partial_update':
            return user == state.user
        return user == session.owner or session.users.filter(pk=user.pk)
    
class UserHasAccessToSessionState(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        session = Session.objects.get(pk=request.resolver_match.kwargs.get("session_hash_pk"))
        return session.owner == user or session.users.filter(pk=user.pk)
    
    def has_object_permission(self, request, view, state):
        user = request.user
        session = state.session
        return user == session.owner or session.users.filter(pk=user.pk)

class UserHasAccessToCityState(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        session = Session.objects.get(pk=request.resolver_match.kwargs.get("session_hash_pk"))
        return user == session.owner or session.users.filter(pk=user.pk)

    def has_object_permission(self, request, view, state):
        user = request.user
        session = state.session.session
        return user == session.owner or session.users.filter(pk=user.pk)

class UserHasAccessToCardState(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        session = Session.objects.get(pk=request.resolver_match.kwargs.get("session_hash_pk"))
        return user == session.owner or session.users.filter(pk=user.pk)

    def has_object_permission(self, request, view, state):
        user = request.user
        session = state.session.session
        return user == session.owner or session.users.filter(pk=user.pk)