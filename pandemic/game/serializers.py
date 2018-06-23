from rest_framework.serializers import ModelSerializer, SlugRelatedField, SerializerMethodField
from django.contrib.auth.models import User
from .models import Session, City, PlayerState, CityState, CardState, CureState, DiseaseState, Pawn, SessionState, Card

class SessionSerializer(ModelSerializer):
    class Meta:
        model = Session
        exclude = ("password", )

class SessionStateSerializer(ModelSerializer):
    class Meta:
        model = SessionState
        fields = "__all__"

class UserSerializer(ModelSerializer):
    img_url = SerializerMethodField('get_image_url')
    class Meta:
        model = User
        fields = ("username", "id", "img_url")

    def get_image_url(self, user):
        return user.userprofile.image.url if user.userprofile.image.name != '' is not None else '/media/default/stock.png'

class CitySerializer(ModelSerializer):
    color = SlugRelatedField(
        read_only=True,
        slug_field='hex_code',
    )
    connections = SlugRelatedField(
        read_only=True,
        slug_field='name',
        many=True,
    )
    class Meta:
        model = City
        fields = "__all__"

class PlayerStateSerializer(ModelSerializer):
    class Meta:
        model = PlayerState
        fields = "__all__"

class CityStateSerializer(ModelSerializer):
    class Meta:
        model = CityState
        fields = "__all__"

class CardStateSerializer(ModelSerializer):
    class Meta:
        model = CardState
        fields = "__all__"

class CureStateSerializer(ModelSerializer):
    color = SlugRelatedField(
        read_only=True,
        slug_field='name',
    )
    class Meta:
        model = CureState
        fields = "__all__"

class DiseaseStateSerializer(ModelSerializer):
    color = SlugRelatedField(
        read_only=True,
        slug_field='name',
    )
    class Meta:
        model = DiseaseState
        fields = "__all__"

class PawnSerializer(ModelSerializer):
    color = SlugRelatedField(
        read_only=True,
        slug_field='hex_code',
    )
    class Meta:
        model = Pawn
        fields = "__all__"

class CardSerializer(ModelSerializer):
    color = SlugRelatedField(
        read_only=True,
        slug_field='name',
    )
    class Meta:
        model = Card
        fields = "__all__"