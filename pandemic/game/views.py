from django.shortcuts import render, redirect, get_object_or_404
import django.contrib.auth.hashers as hashers
from .models import Session, City, Card, CardState, PlayerState, SessionState, CityState, CureState, Pawn, Color, DiseaseState
from django.contrib.auth.decorators import login_required
from .forms import *
from chat.models import Chat
from django.db.models import Q
from django.contrib.auth.models import User
from .permissions import UserHasAccessToSession, UserHasAccessToState, UserHasAccessToSessionParticipants, UserHasAccessToCityState, UserHasAccessToCardState, UserHasAccessToSessionState
from rest_framework import viewsets, status
from rest_framework.response import Response
from .serializers import SessionSerializer, SessionStateSerializer, UserSerializer, CitySerializer, PlayerStateSerializer, CityStateSerializer, CardStateSerializer, CureStateSerializer, DiseaseStateSerializer, PawnSerializer, CardSerializer
from datetime import datetime
from .tasks import schedule_session_start


def frontpage(request):
    qs = Session.objects.all()
    return render(request, 'game/frontpage.html', {'qs': qs})


@login_required
def create(request):
    if request.method == "POST":
        create_session_form = SessionCreationForm(request.POST)
        if create_session_form.is_valid():
            session = create_session_form.save(commit=False)
            if request.POST["password"] != '':
                session.password = hashers.make_password(
                    request.POST["password"], hasher=hashers.PBKDF2PasswordHasher())
                session.locked = True
            session.owner = User.objects.get(username=request.user.username)
            session.save()
            if session.eta_to_start:
                eta_datetime = datetime.now().replace(hour=session.eta_to_start.hour, minute=session.eta_to_start.minute,
                                                      second=session.eta_to_start.second, microsecond=session.eta_to_start.microsecond)
                schedule_session_start.apply_async(
                    (session.session_hash,), eta=eta_datetime)
            chat = Chat.objects.create(session=session)
            chat.save()
            return redirect('game_session', session_hash=session.session_hash)
    return render(request, "game/create.html", {'form': (SessionCreationForm() if request.method == "GET" else create_session_form)})


@login_required
def session(request, session_hash):
    session = get_object_or_404(Session, session_hash=session_hash)
    chat = Chat.objects.get(session=session)
    if request.method == "POST":
        password_form = SessionPasswordForm(request.POST)
        if password_form.is_valid():
            password = password_form.cleaned_data.get("password")
            validate = hashers.check_password(password, session.password)
            if not validate:
                password_form.add_error('password', "Invalid password")
                return render(request, "game/session_password.html", {"form": password_form})
            else:
                session.users.add(request.user)
                session.save()
                return render(request, "game/lobby.html", {"session": session, "chat_id": chat.id})
    else:
        if not session.has_started:
            if session.max_players > len(session.users.all()) + 1 or (request.user.username == session.owner.username or session.users.filter(username=request.user.username)):
                if session.password == '' or request.user.username == session.owner.username:
                    if request.user.username != session.owner.username:
                        session.users.add(request.user)
                        session.save()
                    return render(request, "game/lobby.html", {"session": session, "chat_id": chat.id})
                else:
                    return render(request, "game/session_password.html", {"form": SessionPasswordForm()})
            else:
                return render(request, "game/frontpage.html", {"full": True, "qs": Session.objects.all()})
        else:
            if request.user.username == session.owner.username or session.users.filter(username=request.user.username):
                return render(request, "game/game.html", {"session": session, "chat_id": chat.id})

# Session setup


def setup_session(session):
    owner = session.owner
    users = session.users
    num_players = len(users.all()) + 1
    start_city = City.objects.get(name="Atlanta")

    session_state = SessionState.objects.create(
        session=session, current_player=owner)

    setup_player_state(session_state, users, owner, start_city)
    setup_city_state(session_state, start_city)
    setup_card_state(session_state, int(session.difficulty),
                     num_players, owner, users)
    setup_disease_state(session_state)
    setup_cure_state(session_state)


def setup_city_state(session_state, start_city):
    cities = City.objects.all()
    for city in cities:
        if city == start_city:
            CityState.objects.create(
                session=session_state, city=city, research_station=True)
        else:
            CityState.objects.create(session=session_state, city=city)


def setup_cure_state(session_state):
    colors = Color.objects.all()
    for color in colors:
        if color.name in ["Black", "Yellow", "Red", "Blue"]:
            CureState.objects.create(session=session_state, color=color)


def setup_disease_state(session_state):
    colors = Color.objects.all()
    for color in colors:
        if color.name in ["Black", "Yellow", "Red", "Blue"]:
            DiseaseState.objects.create(session=session_state, color=color)


def setup_player_state(session_state, users, owner, start_city):
    pawn = Pawn.objects.all().order_by("?")
    last_id = 0
    users_qs = users.all()
    for id, user in enumerate(users_qs):
        PlayerState.objects.create(
            session=session_state, city=start_city, user=user, pawn=pawn[id])
        last_id = id
    PlayerState.objects.create(
        session=session_state, city=start_city, user=owner, pawn=pawn[last_id + 1])


def setup_card_state(session_state, epidemic_level, num_players, owner, users):
    infection_deck = Card.objects.all().filter(card_type="Infection").order_by("?")
    for card in infection_deck:
        CardState.objects.create(
            session=session_state, card=card, deck="Infection")

    infection_state_cards = CardState.objects.all().filter(
        deck="Infection", session=session_state)
    infection_slice_begin = 0
    infection_slice_end = 3
    for i in range(3, 0, -1):
        cards = infection_state_cards[infection_slice_begin:infection_slice_end]
        for card in cards:
            city = card.card.city
            city_color = city.color.name
            city_state = CityState.objects.get(
                city=city, session=session_state)
            if city_color == "Black":
                city_state.black_cubes = i
            elif city_color == "Yellow":
                city_state.yellow_cubes = i
            elif city_color == "Red":
                city_state.red_cubes = i
            else:
                city_state.blue_cubes = i
            card.discarded = True
            city_state.save()
            card.save()
        infection_slice_begin = infection_slice_end
        infection_slice_end += 3

    cards_per = {2: 4, 3: 3, 4: 2}
    player_cards = Card.objects.all().filter(
        Q(card_type="Event") | Q(card_type="City")).order_by("?")
    epidemic_cards = Card.objects.all().filter(card_type="Epidemic")

    begin_hand_slice_amount = cards_per[num_players]
    slice_amount = int(len(player_cards) / epidemic_level)
    slice_begin = 0
    slice_end = slice_amount
    hand_slice_begin = 0
    hand_slice_end = begin_hand_slice_amount

    for i in range(num_players):
        cards = player_cards[hand_slice_begin: hand_slice_end]
        for card in cards:
            if i == 0:
                CardState.objects.create(
                    session=session_state, card=card, deck="Player", user=owner)
            else:
                CardState.objects.create(
                    session=session_state, card=card, deck="Player", user=users.all()[i - 1])
        hand_slice_begin = hand_slice_end
        hand_slice_end += begin_hand_slice_amount

    slice_begin = hand_slice_end

    for i in range(epidemic_level):
        card_stack = player_cards[slice_begin:slice_end]
        for card in card_stack:
            CardState.objects.create(
                session=session_state, card=card, deck="Player")
        CardState.objects.create(
            session=session_state, card=epidemic_cards[i], deck="Player")
        slice_begin = slice_end
        slice_end *= 2


def epidemic_event(session_state):
    session_state.infection_rate += 1
    infection_deck = CardState.objects.all().filter(
        deck="Infection", discarded=False, session=session_state)
    card_state = infection_deck.last()
    card = card_state.card
    city = card.city
    city_color = city.color.name
    city_state = CityState.objects.get(session=session_state, city=city)
    if city_color == "Black":
        if city_state.black_cubes > 0:
            city_state.black_cubes = 3
            city_state.last_changed = datetime.now()
            city_state.save()
            session_state.outbreak_count += 1
            neighbours = city.connections.all()
            for neighbour in neighbours:
                city_spread(session_state, neighbour.name,
                            [city_state], city_color)
        else:
            city_state.black_cubes = 3
            city_state.last_changed = datetime.now()
            city_state.save()

    elif city_color == "Yellow":
        if city_state.yellow_cubes > 0:
            city_state.yellow_cubes = 3
            city_state.last_changed = datetime.now()
            city_state.save()
            session_state.outbreak_count += 1
            neighbours = city.connections.all()
            for neighbour in neighbours:
                city_spread(session_state, neighbour.name,
                            [city_state], city_color)
        else:
            city_state.yellow_cubes = 3
            city_state.last_changed = datetime.now()
            city_state.save()

    elif city_color == "Red":
        if city_state.red_cubes > 0:
            city_state.red_cubes = 3
            city_state.last_changed = datetime.now()
            city_state.save()
            session_state.outbreak_count += 1
            neighbours = city.connections.all()
            for neighbour in neighbours:
                city_spread(session_state, neighbour.name,
                            [city_state], city_color)
        else:
            city_state.red_cubes = 3
            city_state.last_changed = datetime.now()
            city_state.save()

    else:
        if city_state.blue_cubes > 0:
            city_state.blue_cubes = 3
            city_state.last_changed = datetime.now()
            city_state.save()
            session_state.outbreak_count += 1
            neighbours = city.connections.all()
            for neighbour in neighbours:
                city_spread(session_state, neighbour.name,
                            [city_state], city_color)
        else:
            city_state.blue_cubes = 3
            city_state.last_changed = datetime.now()
            city_state.save()

    card_state.discarded = True
    card_state.last_changed = datetime.now()
    card_state.save()
    infection_discarded_deck = CardState.objects.all().filter(
        deck="Infection", discarded=True, session=session_state)
    for card in infection_discarded_deck:
        card.discarded = False
        card.last_changed = datetime.now()
        card.save()


def city_spread(session, city_name, outbreak_log, color):
    city = City.objects.get(name=city_name)
    city_state = CityState.objects.get(session=session, city=city)
    if color == "Black":
        if city_state.black_cubes < 3:
            city_state.black_cubes += 1
            city_state.last_changed = datetime.now()
            city_state.save()
        else:
            if city_state not in outbreak_log:
                outbreak_log.append(city_state)
                session.outbreak_count += 1
                neighbours = city.connections.all()
                for neighbour in neighbours:
                    city_spread(session, neighbour.name,
                                outbreak_log, color)

    elif color == "Yellow":
        if city_state.yellow_cubes < 3:
            city_state.yellow_cubes += 1
            city_state.last_changed = datetime.now()
            city_state.save()
        else:
            if city_state not in outbreak_log:
                outbreak_log.append(city_state)
                session.outbreak_count += 1
                neighbours = city.connections.all()
                for neighbour in neighbours:
                    city_spread(session, neighbour.name,
                                outbreak_log, color)

    elif color == "Red":
        if city_state.red_cubes < 3:
            city_state.red_cubes += 1
            city_state.last_changed = datetime.now()
            city_state.save()
        else:
            if city_state not in outbreak_log:
                outbreak_log.append(city_state)
                session.outbreak_count += 1
                neighbours = city.connections.all()
                for neighbour in neighbours:
                    city_spread(session, neighbour.name,
                                outbreak_log, color)

    else:
        if city_state.blue_cubes < 3:
            city_state.blue_cubes += 1
            city_state.last_changed = datetime.now()
            city_state.save()
        else:
            if city_state not in outbreak_log:
                outbreak_log.append(city_state)
                session.outbreak_count += 1
                neighbours = city.connections.all()
                for neighbour in neighbours:
                    city_spread(session, neighbour.name,
                                outbreak_log, color)


def rotate_turn(session_state, player_state):
    # DRAW PHASE
    player = player_state.user
    session = session_state.session
    user_list = session.users.all()
    owner = session.owner
    cards = CardState.objects.all().filter(deck="Player", discarded=False,
                                           user=None, session=session_state)
    if player == owner:
        session_state.current_player = user_list[0]
    else:
        id_num = list(user_list).index(player)
        if id_num == len(user_list) - 1:
            session_state.current_player = owner
        else:
            session_state.current_player = user_list[id_num + 1]
    player_state.num_actions = 4
    player_cards = CardState.objects.all().filter(
        deck="Player", user=player, session=session_state)
    # TODO o que acontece quando muda de turno
    if len(cards) < 2:
        session_state.has_ended = True
        session_state.end_result = "Loss"
    else:
        for i in range(2):
            player_cards = CardState.objects.all().filter(
                deck="Player", user=player, session=session_state)
            card_state = cards[i]
            card = card_state.card
            if card.card_type == "Epidemic":
                epidemic_event(session_state)
                card_state.discarded = True
                card_state.last_changed = datetime.now()
                card_state.save()
            else:
                if len(player_cards) > 6:
                    player_cards[i].discarded = True
                    player_cards[i].user = None
                    player_cards[i].last_changed = datetime.now()
                    player_cards[i].save()
                card_state.user = player
                card_state.last_changed = datetime.now()
                card_state.save()

    # INFECTION PHASE
    if not session_state.quiet_night:
        infection_values = SessionState.infection_rate_values
        infection_value = infection_values[session_state.infection_rate]
        infection_cards = CardState.objects.filter(
            session=session_state, deck="Infection", discarded=False, user=None)
        for _ in range(infection_value):
            infection_card_state = infection_cards[0]
            infection_card = infection_card_state.card
            infected_city = infection_card.city
            infected_city_state = CityState.objects.get(
                session=session_state, city=infected_city)
            city_color = infected_city.color.name

            if city_color == "Black":
                if infected_city_state.black_cubes < 3:
                    infected_city_state.black_cubes += 1
                    infected_city_state.last_changed = datetime.now()
                    infected_city_state.save()
                else:
                    session_state.outbreak_count += 1
                    neighbours = infected_city.connections.all()
                    for neighbour in neighbours:
                        city_spread(session_state, neighbour.name, [
                                    infected_city_state], city_color)

            elif city_color == "Yellow":
                if infected_city_state.yellow_cubes < 3:
                    infected_city_state.yellow_cubes += 1
                    infected_city_state.last_changed = datetime.now()
                    infected_city_state.save()
                else:
                    session_state.outbreak_count += 1
                    neighbours = infected_city.connections.all()
                    for neighbour in neighbours:
                        city_spread(session_state, neighbour.name, [
                                    infected_city_state], city_color)

            elif city_color == "Blue":
                if infected_city_state.blue_cubes < 3:
                    infected_city_state.blue_cubes += 1
                    infected_city_state.last_changed = datetime.now()
                    infected_city_state.save()
                else:
                    session_state.outbreak_count += 1
                    neighbours = infected_city.connections.all()
                    for neighbour in neighbours:
                        city_spread(session_state, neighbour.name, [
                                    infected_city_state], city_color)

            else:
                if infected_city_state.red_cubes < 3:
                    infected_city_state.red_cubes += 1
                    infected_city_state.last_changed = datetime.now()
                    infected_city_state.save()
                else:
                    session_state.outbreak_count += 1
                    neighbours = infected_city.connections.all()
                    for neighbour in neighbours:
                        city_spread(session_state, neighbour.name, [
                                    infected_city_state], city_color)
            infection_card_state.discarded = True
            infection_card_state.last_changed = datetime.now()
            infection_card_state.save()
    else:
        session_state.quiet_night = False

    if session_state.outbreak_count > 7:
        session_state.end_result = "Loss"
        session_state.has_ended = True
    else:
        wintest = win_test(session_state)
        if wintest:
            session_state.end_result = "Win"
            session_state.has_ended = True

    session_state.last_changed = datetime.now()
    session_state.save()
    player_state.last_changed = datetime.now()
    player_state.save()


def eradication_check(session):
    colors = Color.objects.all()
    cubes = {"Black": 0, "Yellow": 0, "Red": 0, "Blue": 0}

    cities = City.objects.all()

    for city in cities:
        city_state = CityState.objects.get(session=session, city=city)
        cubes["Black"] += city_state.black_cubes
        cubes["Yellow"] += city_state.yellow_cubes
        cubes["Red"] += city_state.red_cubes
        cubes["Blue"] += city_state.blue_cubes

    for color in colors:
        if color.name in ["Black", "Yellow", "Red", "Blue"]:
            disease_state = DiseaseState.objects.get(
                session=session, color=color)
            cure_state = CureState.objects.get(session=session, color=color)
            if cure_state.found:
                if cubes[color.name] == 0:
                    disease_state.eradication_status = True
                    disease_state.save()


def make_event(session, card_state, card, data, extra):
    description = card.description
    event_type = description.split(":")[0]
    # Card event
    # Airlift: Move a player to any city. You must have their permission.
    # One Quiet Night: The next Player to begin their infection phase may skip it.
    # Government Grant: Add a Research Station to any city for free.
    # Forecast: Examine the top 6 cards of the Infection Draw Pile. Rearrange them in any order.
    if event_type == "Airlift":
        # How do i ask information to the user?
        city = extra["City"]
        city_object = City.objects.get(name=city)
        user = extra["User"]
        user_object = User.objects.get(username=user)
        player_state = PlayerState.objects.get(
            user=user_object, session=session)
        player_state.city = city_object
        player_state.last_changed = datetime.now()
        player_state.save()
    elif event_type == "One Quiet Night":
        # Talvez criar 2 cartas fantasma para meter no topo do deck de infection
        pass
    elif event_type == "Government Grant":
        # How do i ask information to the user?
        city = extra["City"]
        city_object = City.objects.get(name=city)
        city_state = CityState.objects.get(city=city_object, session=session)
        city_state.research_station = True
        city_state.last_changed = datetime.now()
        city_state.save()
    elif event_type == "Forecast":
        # top card da sessao esta na posicao 0
        # How do i show information to the user?
        user = extra["User"]
        cards_2_show = CardState.objects.all().filter(
            deck="Player", User=None, discarded=False, session=session_state)
        top_card = 0
        last_card_shown = 5
        forecast_cards = cards_2_show[top_card:last_card_shown]
        for card in forecast_cards:
            CardState.objects.create(
                session=session_state, card=card, deck="Forecast", user=user)

    else:
        pass


def win_test(session_state):
    disease_states = DiseaseState.objects.all().filter(session=session_state)
    eradicated_count = 0

    for state in disease_states:
        if state.eradication_status:
            eradicated_count += 1

    return eradicated_count == len(disease_states)


def update_player_state(request, pk=None, session_hash_pk=None):
    player_state = get_object_or_404(PlayerState, id=pk)
    player = player_state.user
    session_state = player_state.session
    if session_state.current_player == player and player_state.num_actions > 0:
        serializer = PlayerStateSerializer(
            player_state, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            instance = serializer.instance
            instance.num_actions -= 1
            instance.last_changed = datetime.now()
            instance.save()
            if instance.num_actions == 0:
                rotate_turn(session_state, instance)
            return Response(serializer.data)
        return Response(serializer.errors)
    return Response(status=status.HTTP_403_FORBIDDEN)


def update_city_state(request, pk=None, session_hash_pk=None):
    city_state = get_object_or_404(CityState, id=pk)
    user = request.user
    session_state = city_state.session
    player_state = PlayerState.objects.get(session=session_state, user=user)
    if session_state.current_player == user and player_state.num_actions > 0:
        if "research_station" in request.data:
            city_card = Card.objects.get(
                card_type="City", city=city_state.city)
            card_state = CardState.objects.get(
                deck="Player", session=session_state, card=city_card)
            if card_state.user == user:
                card_state.user = None
                card_state.last_changed = datetime.now()
                card_state.save()
            else:
                return Response(status=status.HTTP_403_FORBIDDEN)
        serializer = CityStateSerializer(
            city_state, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save(last_changed=datetime.now())
            eradication_check(session_state)
            player_state.num_actions -= 1
            player_state.last_changed = datetime.now()
            player_state.save()
            if player_state.num_actions == 0:
                rotate_turn(session_state, player_state)
            return Response(serializer.data)
        return Response(serializer.errors)
    return Response(status=status.HTTP_403_FORBIDDEN)

# ViewSets for REST API


class SessionViewSet(viewsets.ModelViewSet):
    queryset = Session.objects.all()
    serializer_class = SessionSerializer
    permission_classes = [UserHasAccessToSession]

    def partial_update(self, request, pk=None):
        session = get_object_or_404(Session, session_hash=pk)
        serializer = SessionSerializer(
            session, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            previous_has_started = session.has_started
            serializer.save()
            if request.data.get("has_started", None) and not previous_has_started:
                setup_session(session)
                session.start_time = datetime.now()
                session.save()
        return Response(serializer.data)


class SessionStateViewSet(viewsets.ModelViewSet):
    serializer_class = SessionStateSerializer
    permission_classes = [UserHasAccessToSessionState]

    def get_queryset(self):
        session = get_object_or_404(
            Session, session_hash=self.kwargs['session_hash_pk'])
        queryset = SessionState.objects.all().filter(session=session)
        return queryset

    def partial_update(self, request, pk=None, session_hash_pk=None):
        session_state = get_object_or_404(SessionState, id=pk)
        player = request.user
        player_state = PlayerState.objects.get(
            session=session_state, user=player)
        data = request.data
        if session_state.current_player == player:
            if data["current_player"] == None:
                rotate_turn(session_state, player_state)
            serializer = SessionStateSerializer(session_state)
            return Response(serializer.data)
        return Response(status=status.HTTP_403_FORBIDDEN)


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    permission_classes = [UserHasAccessToSessionParticipants]

    def get_queryset(self):
        queryset = Session.objects.get(
            session_hash=self.kwargs['session_hash_pk']).users
        return queryset


class OwnerViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    permission_classes = [UserHasAccessToSessionParticipants]

    def get_queryset(self):
        queryset = {Session.objects.get(
            session_hash=self.kwargs['session_hash_pk']).owner}
        return queryset


class CityViewSet(viewsets.ModelViewSet):
    serializer_class = CitySerializer

    def get_queryset(self):
        queryset = City.objects.all()
        city = self.request.query_params.get("city", None)
        if city is not None:
            queryset = queryset.filter(name=city)
        return queryset


class PlayerStateViewSet(viewsets.ModelViewSet):
    serializer_class = PlayerStateSerializer
    permission_classes = [UserHasAccessToState]

    def get_queryset(self):
        session = get_object_or_404(
            Session, session_hash=self.kwargs['session_hash_pk'])
        session_state = get_object_or_404(SessionState, session=session)
        queryset = PlayerState.objects.all().filter(session=session_state)
        player = self.request.query_params.get("player", None)
        if player is not None:
            user = User.objects.get(username=player)
            queryset = queryset.filter(user=user)
        return queryset

    def partial_update(self, request, pk=None, session_hash_pk=None):
        return update_player_state(request, pk, session_hash_pk)


class CityStateViewSet(viewsets.ModelViewSet):
    serializer_class = CityStateSerializer
    permission_classes = [UserHasAccessToCityState]

    def get_queryset(self):
        session = get_object_or_404(
            Session, session_hash=self.kwargs['session_hash_pk'])
        session_state = get_object_or_404(SessionState, session=session)
        queryset = CityState.objects.all().filter(session=session_state)
        city = self.request.query_params.get("city", None)
        if city is not None:
            queryset = queryset.filter(city=City.objects.get(id=city))
        return queryset

    def partial_update(self, request, pk=None, session_hash_pk=None):
        return update_city_state(request, pk, session_hash_pk)


class CardStateViewSet(viewsets.ModelViewSet):
    serializer_class = CardStateSerializer
    permission_classes = [UserHasAccessToCardState]

    def get_queryset(self):
        session = get_object_or_404(
            Session, session_hash=self.kwargs['session_hash_pk'])
        session_state = get_object_or_404(SessionState, session=session)
        queryset = CardState.objects.all().filter(session=session_state)
        card_state = self.request.query_params.get("player", None)
        foresight = self.request.query_params.get("foresight", None)

        if card_state is not None:
            user = User.objects.get(username=card_state)
            queryset = queryset.filter(user=user)
        if foresight is not None:
            queryset = queryset.filter(
                deck="Player", user=None, discarded=False)[0:6]

        return queryset

    def partial_update(self, request, pk=None, session_hash_pk=None):
        card_state = get_object_or_404(CardState, id=pk)
        card = card_state.card
        user = request.user
        session_state = card_state.session
        player_state = PlayerState.objects.get(
            user=card_state.user, session=session_state)
        data = request.data
        if "extra" in data:
            extra = data["extra"]
            del data["extra"]
        else:
            extra = None
        if session_state.current_player == user and (player_state.num_actions > 0 or card.card_type == "Event") and card_state.user == user:
            if "user" in data and data["user"] is not None:
                username = data["user"]
                other_user = User.objects.get(username=username)
                data["user"] = other_user.pk
            serializer = CardStateSerializer(
                card_state, data=data, partial=True)
            if serializer.is_valid():
                serializer.save()
                if "user" in data and data["user"] is None and card.card_type == "City":
                    if extra is None:
                        city = card.city
                        player_state.city = city
                    instance = serializer.instance
                    instance.discarded = True
                    instance.last_changed = datetime.now()
                    instance.save()
                    if extra is None:
                        player_state.num_actions -= 1
                        player_state.last_changed = datetime.now()
                        player_state.save()
                        if player_state.num_actions == 0:
                            rotate_turn(session_state, player_state)
                if card.card_type == "Event":
                    make_event(session_state, card_state, card, data, extra)
                return Response(serializer.data)
            return Response(serializer.errors)
        return Response(status=status.HTTP_403_FORBIDDEN)


class CureStateViewSet(viewsets.ModelViewSet):
    serializer_class = CureStateSerializer
    permission_classes = [UserHasAccessToState]

    def get_queryset(self):
        session = get_object_or_404(
            Session, session_hash=self.kwargs['session_hash_pk'])
        session_state = get_object_or_404(SessionState, session=session)
        queryset = CureState.objects.all().filter(session=session_state)
        color = self.request.query_params.get("color", None)
        if color is not None:
            queryset = queryset.filter(color=color)
        return queryset

    def partial_update(self, request, pk=None, session_hash_pk=None):
        cure_state = get_object_or_404(CureState, id=pk)
        session_state = cure_state.session
        user = request.user
        data = request.data
        player_state = PlayerState(user=user, session=session_state)
        if session_state.current_player == user and player_state.num_actions > 0:
            extra = data["extra"]
            del data["extra"]
            serializer = CureStateSerializer(
                cure_state, data=data, partial=True)
            if serializer.is_valid():
                serializer.save()
                instance = serializer.instance
                instance.last_changed = datetime.now()
                instance.save()
                for card_state_id in extra:
                    card_state = CardState(id=card_state_id)
                    card_state.user = None
                    card_state.discarded = True
                    card_state.last_changed = datetime.now()
                    card_state.save()


class DiseaseStateViewSet(viewsets.ModelViewSet):
    serializer_class = DiseaseStateSerializer
    permission_classes = [UserHasAccessToState]

    def get_queryset(self):
        session = get_object_or_404(
            Session, session_hash=self.kwargs['session_hash_pk'])
        session_state = get_object_or_404(SessionState, session=session)
        queryset = DiseaseState.objects.all().filter(session=session_state)
        return queryset


class PawnViewSet(viewsets.ModelViewSet):
    queryset = Pawn.objects.all()
    serializer_class = PawnSerializer


class CardViewSet(viewsets.ModelViewSet):
    queryset = Card.objects.all()
    serializer_class = CardSerializer
