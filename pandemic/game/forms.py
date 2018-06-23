from .models import Session
from django import forms
from django_countries.fields import CountryField
from accounts.models import District, Municipality
from .models import Session

class DateInput(forms.DateInput):
    input_type = 'time'

class SessionCreationForm(forms.ModelForm):
    name = forms.CharField(max_length=30, label="Name(*)", help_text="Lobby name", required=True)
    max_players = forms.IntegerField(label="Maximum Players(*)", help_text="Maximum amount of players in the game", required=True, initial=2,min_value=2,max_value=4)
    description = forms.CharField(label="Description(*)", help_text="Session description", required=True, max_length=512)
    difficulty = forms.ChoiceField(label="Difficulty", choices=Session.difficulty_level, help_text="Difficulty of the game", required=True)
    eta_to_start = forms.TimeField(label="Start time", help_text="When should the game start automatically", required=False)
    min_age = forms.IntegerField(label="Minimum Age", help_text="Minimum age of a player", required=False)
    password = forms.CharField(label="Password:", help_text="Password for the lobby", widget=forms.PasswordInput, required=False)

    name.widget.attrs.update({'class':'form-control'})
    max_players.widget.attrs.update({'class':'form-control'})
    description.widget.attrs.update({'class':'form-control'})
    difficulty.widget.attrs.update({'class':'form-control'})
    eta_to_start.widget.attrs.update({'class':'form-control'})
    min_age.widget.attrs.update({'class':'form-control'})
    password.widget.attrs.update({'class':'form-control'})

    class Meta:
        model = Session
        fields = ("name", "max_players", "description", "eta_to_start", "difficulty", "min_age", "password", )


class SessionPasswordForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput, required=True)