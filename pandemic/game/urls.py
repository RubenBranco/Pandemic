from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import path, include
# from admin.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('session/<session_hash>', views.session, name="game_session"),
    path('create/', views.create, name="game_create"),
    path('', views.frontpage, name="game_frontpage"),
]