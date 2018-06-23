from django.db import models
from accounts.models import District, Municipality
from django.contrib.auth.models import User
from django_countries.fields import CountryField
import uuid


class Session(models.Model):
    STANDARD_DIFFICULTY = '4'
    PRO_DIFFICULTY = '5'
    MASTER_DIFFICULTY = '6'
    difficulty_level = (
        (STANDARD_DIFFICULTY, 'Normal'),
        (PRO_DIFFICULTY, 'Profissional'),
        (MASTER_DIFFICULTY, 'Master'),
    )
    session_hash = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    has_started = models.BooleanField(default=False)
    name = models.CharField(max_length=30, blank=True)
    description = models.TextField(null=True)
    max_players = models.PositiveSmallIntegerField(blank=True)
    start_time = models.DateTimeField(blank=True, null=True)
    eta_to_start = models.TimeField(blank=True, null=True)
    locked = models.BooleanField(default=False)
    # Restrictions
    difficulty = models.CharField(max_length=1, choices=difficulty_level, default=STANDARD_DIFFICULTY)
    min_age = models.PositiveSmallIntegerField(blank=True, null=True)
    password = models.CharField(max_length=256, blank=True, null=True)
    users = models.ManyToManyField(User, blank=True)
    owner = models.ForeignKey(User, blank=True, on_delete=models.CASCADE, related_name="owner")
    
class Color(models.Model):
    colors = [
        ('Black', 'Black'),
        ('Red', 'Red'),
        ('Yellow', 'Yellow'),
        ('Blue', 'Blue'),
        ('LightBlue', 'LightBlue'),
        ('Brown', 'Brown'),
        ('Orange', 'Orange'),
        ('LightGreen', 'LightGreen'),
        ('DarkGreen', 'DarkGreen'),
        ('White', 'White'),
        ('Pink', 'Pink'),
    ]
    name = models.CharField(max_length=10, choices=colors)
    hex_code = models.TextField()

class City(models.Model):
    name = models.TextField()
    latitude = models.FloatField()
    longitude = models.FloatField()
    thumbnail = models.ImageField(blank=True, null=True, upload_to='game')
    color = models.ForeignKey(Color, null=True, on_delete=models.CASCADE)
    connections = models.ManyToManyField("self")

class Card(models.Model):
    card_types = [
        ('City', 'City'),
        ('Event', 'Event'),
        ('Infection', 'Infection'),
        ('Epidemic', 'Epidemic'),
    ]

    card_type = models.CharField(max_length=10, choices=card_types)
    city = models.ForeignKey(City, null=True, on_delete=models.CASCADE)
    color = models.ForeignKey(Color, null=True, on_delete=models.CASCADE)
    thumbnail = models.ImageField(blank=True, null=True, upload_to='game')
    # Card event
    # Airlift: Move a player to any city. You must have their permission.
    # One Quiet Night: The next Player to begin their infection fase may skip it.
    # Government Grant: Add a Research Station to any city for free.
    # Forecast: Examine the top 6 cards of the Infection Draw Pile. Rearrange them in any order.
    description = models.CharField(max_length=50, null=True)

class Pawn(models.Model):
    color = models.ForeignKey(Color, models.CASCADE)
    icon = models.ImageField(blank=True, null=True, upload_to='game')

class SessionState(models.Model):
    end_results = [
        ('Win', 'Win'),
        ('Loss', 'Loss'),
    ]
    
    infection_rate_values = [2, 2, 2, 3, 3, 4, 4]

    session = models.OneToOneField(Session, on_delete=models.CASCADE)
    quiet_night = models.BooleanField(default=False)
    current_player = models.ForeignKey(User, on_delete=models.CASCADE)
    infection_rate = models.PositiveSmallIntegerField(default=0)
    outbreak_count = models.PositiveSmallIntegerField(default=0)
    has_ended = models.BooleanField(default=False)
    end_result = models.CharField(max_length=4, choices=end_results, null=True)
    last_changed = models.DateTimeField(auto_now_add=True, null=True)

class PlayerState(models.Model):
    session = models.ForeignKey(SessionState, on_delete=models.CASCADE)
    num_actions = models.PositiveSmallIntegerField(default=4)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    pawn = models.ForeignKey(Pawn, blank=True, null=True, on_delete=models.CASCADE)
    last_changed = models.DateTimeField(auto_now_add=True, null=True)

class CardState(models.Model):
    deck_types = [
        ('Player', 'Player'),
        ('Infection', 'Infection'),
    ]

    session = models.ForeignKey(SessionState, on_delete=models.CASCADE)
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    card = models.ForeignKey(Card, on_delete=models.CASCADE)
    deck = models.CharField(max_length=9, choices=deck_types)
    discarded = models.BooleanField(default=False)
    last_changed = models.DateTimeField(auto_now_add=True, null=True)

class CityState(models.Model):
    session = models.ForeignKey(SessionState, on_delete=models.CASCADE)
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    black_cubes = models.PositiveSmallIntegerField(default=0)
    red_cubes = models.PositiveSmallIntegerField(default=0)
    yellow_cubes = models.PositiveSmallIntegerField(default=0)
    blue_cubes = models.PositiveSmallIntegerField(default=0)
    research_station = models.BooleanField(default=False)
    last_changed = models.DateTimeField(auto_now_add=True, null=True)

class CureState(models.Model):
    session = models.ForeignKey(SessionState, on_delete=models.CASCADE)
    city = models.ForeignKey(CityState, null=True, on_delete=models.CASCADE)
    color = models.ForeignKey(Color, on_delete=models.CASCADE)
    found = models.BooleanField(default=False)
    last_changed = models.DateTimeField(auto_now_add=True, null=True)

class DiseaseState(models.Model):
    session = models.ForeignKey(SessionState, on_delete=models.CASCADE)
    color = models.ForeignKey(Color, on_delete=models.CASCADE)
    eradication_status = models.BooleanField(default=False)
    last_changed = models.DateTimeField(auto_now_add=True, null=True)
