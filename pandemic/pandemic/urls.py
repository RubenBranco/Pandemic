"""pandemic URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views
from rest_framework_nested import routers
from accounts import views as acc_views
from soap import urls as soap_urls
from game import urls as game_urls
from chat import views as chat_views
from game import views as game_views
from rest_framework.documentation import include_docs_urls

api = routers.SimpleRouter()
api.register(r'chat', chat_views.ChatViewSet, base_name='chat')
api.register(r'cities', game_views.CityViewSet, base_name='city')
api.register(r'pawn', game_views.PawnViewSet, base_name='pawn')
api.register(r'card', game_views.CardViewSet, base_name='card')
chat_router = routers.NestedSimpleRouter(api, r'chat', lookup='chat')
chat_router.register(r'messages', chat_views.MessageViewSet, base_name='chat-message')
api.register(r'session', game_views.SessionViewSet, base_name='session')
session_router = routers.NestedSimpleRouter(api, r'session', lookup='session_hash')
session_router.register(r'session_state', game_views.SessionStateViewSet, base_name='session-state')
session_router.register(r'users', game_views.UserViewSet, base_name='session-users')
session_router.register(r'owner', game_views.OwnerViewSet, base_name='session-owner')
session_router.register(r'player_state', game_views.PlayerStateViewSet, base_name='player-state')
session_router.register(r'city_state', game_views.CityStateViewSet, base_name='city-state')
session_router.register(r'card_state', game_views.CardStateViewSet, base_name='card-state')
session_router.register(r'cure_state', game_views.CureStateViewSet, base_name='cure-state')
session_router.register(r'disease_state', game_views.DiseaseStateViewSet, base_name='disease-state')

api.register('districts', acc_views.DistrictViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    # USER RELATED
    path('login/', auth_views.LoginView.as_view(redirect_authenticated_user=True), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page="/"), name='logout'),
    path('reset-password/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('reset-sent/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset-password-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('register/', acc_views.register, name='register'),
    path('activate/<uidb64>/<token>/', acc_views.registration_activate, name='registration_activate'),
    path('user/<username>/', acc_views.profile, name='profile'),
    path('edit-profile/', acc_views.edit_profile, name='edit_profile'),
    path('change-password/', acc_views.change_password, name='change_password'),
    # END OF USER RELATED
    path('how-to/', views.howto, name="howtoplay"),
    path('about-us/', views.aboutus, name="aboutus"),
    # REST API
    path('api/', include(api.urls)),
    path('api/', include(chat_router.urls)),
    path('api/', include(session_router.urls)),
    path('api-docs/', include_docs_urls(title="Pandemic REST API")),
    # GAME
    path("game/", include(game_urls)),
    # SOAP
    path("soap/", include(soap_urls)),
    # Root
    path('', views.frontpage, name='frontpage'),
]
