from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import path, include
from spyne.protocol.soap import Soap11
from spyne.server.django import DjangoView

from . import views

urlpatterns = [
    path('info_jogo/', DjangoView.as_view(
        services=[views.InfoJogoService], tns='pandemic.soap',
        in_protocol=Soap11(validator='lxml'), out_protocol=Soap11()
    )),
    path('faz_jogada/', DjangoView.as_view(
        services=[views.FazJogadaService], tns='pandemic.soap',
        in_protocol=Soap11(validator='lxml'), out_protocol=Soap11()
    ))
]