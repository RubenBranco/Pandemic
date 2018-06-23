from django.views.decorators.csrf import csrf_exempt
from spyne.error import ResourceNotFoundError, ResourceAlreadyExistsError, InvalidCredentialsError
from spyne.server.django import DjangoApplication
from spyne.model.primitive import Unicode, Integer, Uuid, AnyDict
from spyne.model.complex import Iterable
from spyne.service import ServiceBase
from spyne.protocol.soap import Soap11
from spyne.application import Application
from spyne.decorator import rpc
from django.core.exceptions import ObjectDoesNotExist
from game.models import CityState, PlayerState, City, Session, SessionState
from game.views import update_player_state, update_city_state
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
import json
from rest_framework.request import Request
from django.http import HttpRequest, QueryDict

class InfoJogoService(ServiceBase):
    @rpc(Uuid, _returns=AnyDict)
    def info_jogo(ctx, session_hash):
        try:
            session = Session.objects.get(session_hash=session_hash)
            session_state = SessionState.objects.get(session=session)
            city_states = CityState.objects.all().filter(session=session_state)
            player_states = PlayerState.objects.all().filter(session=session_state)
            res = {'research_centers': {}, 'players': {}, 'cities': {}}

            for city_state in city_states:
                city = city_state.city
                if city_state.black_cubes > 0 or city_state.yellow_cubes > 0 or city_state.red_cubes > 0 or city_state.blue_cubes > 0:
                    res['cities'][city.name.replace(' ', '_')] = {}
                if city_state.black_cubes > 0:
                    res['cities'][city.name.replace(' ', '_')]['Black_Disease'] = city_state.black_cubes
                if city_state.yellow_cubes > 0:
                    res['cities'][city.name.replace(' ', '_')]['Yellow_Disease'] = city_state.yellow_cubes
                if city_state.red_cubes > 0:
                    res['cities'][city.name.replace(' ', '_')]['Red_Disease'] = city_state.red_cubes
                if city_state.blue_cubes > 0:
                    res['cities'][city.name.replace(' ', '_')]['Blue_Disease'] = city_state.blue_cubes
                if city_state.research_station:
                    res['research_centers'][city.name.replace(' ', '_')] = {}

            for player in player_states:
                player_city = player.city
                user = player.user
                res['players'][user.username] = {'position': player_city.name, 'neighbour_cities': {}}

                all_neighbours = player_city.connections.all()
                for city in all_neighbours:
                    res['players'][user.username]['neighbour_cities'][city.name.replace(' ', '_')] = {}
            print(res)
            return res
        except ObjectDoesNotExist:
            raise ResourceNotFoundError('Session')

class FazJogadaService(ServiceBase):
    @rpc(Uuid, Unicode, Unicode, Unicode, Unicode, Unicode, _returns=Unicode)
    def faz_jogada(ctx, id, username, password, jogada, cidade, cor):
        try:
            session = Session.objects.get(session_hash=id)
            session_state = SessionState.objects.get(session=session)
            city = City.objects.get(name=cidade)
            city_state = CityState.objects.get(session=session_state, city=city)
            res = ''
            user = authenticate(username=username, password=password)
            if user is not None:
                player_state = PlayerState.objects.get(session=session_state, user=user.id)
                http_request = HttpRequest()
                http_request.user = user
                http_request.method = "POST"
                if jogada == 'move':
                    http_request.POST = QueryDict.fromkeys(['city'], value=city.id)
                    request = Request(http_request)
                    request.user = user
                    response = update_player_state(request, player_state.id, session.session_hash)
                    res = "Aceite" if response.status_code == 200 else "Não aceite"
                elif jogada == 'treat':
                    key = []
                    value = 0
                    if cor == "Black":
                        key.append('black_cubes')
                        value = city_state.black_cubes - 1
                    elif cor == "Yellow":
                        key.append("yellow_cubes")
                        value = city_state.yellow_cubes - 1
                    elif cor == "Red":
                        key.append("red_cubes")
                        value = city_state.red_cubes - 1
                    else:
                        key.append("blue_cubes")
                        value = city_state.blue_cubes - 1
                    http_request.POST = QueryDict.fromkeys(key, value=value)
                    request = Request(http_request)
                    request.user = user
                    response = update_city_state(request, city_state.id, session.session_hash)
                    res = "Aceite" if response.status_code == 200 else "Não aceite"
                else:
                    http_request.POST = QueryDict.fromkeys(['research_station'], value=True)
                    request = Request(http_request)
                    request.user = user
                    response = update_city_state(request, city_state.id, session.session_hash)
                    res = "Aceite" if response.status_code == 200 else "Não aceite"
                return res
            else:
                raise InvalidCredentialsError('User')
        except ObjectDoesNotExist:
            raise ResourceNotFoundError('Session')

soap_app = Application([InfoJogoService, FazJogadaService],
    'pandemic.soap',
    in_protocol=Soap11(validator='lxml'),
    out_protocol=Soap11(),
)

pandemic_soap_service = csrf_exempt(DjangoApplication(soap_app))