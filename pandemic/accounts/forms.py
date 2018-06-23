from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django_countries.fields import CountryField
from .models import UserProfile

class RegisterForm(UserCreationForm):
    email = forms.EmailField(max_length=254, label="Email", help_text="Your contact email", required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2','first_name','last_name')

class DateInput(forms.DateInput):
    input_type = 'date'

class ProfileForm(forms.ModelForm):
    gender = forms.ChoiceField(choices=[('Male', 'Male'), ('Female', 'Female')], label="Gender", help_text="Choose your gender")
    dob = forms.DateField(label="Date of Birth", widget=DateInput, help_text="Choose your date of birth")
    country = CountryField(blank_label='(Select country)', help_text="Choose your country")
    image = forms.ImageField(label="Image", help_text="Display picture", required=False, widget=forms.FileInput)
    district = forms.CharField(label="District", help_text="Choose your district", required=False, widget=forms.Select)
    county = forms.CharField(label="City", help_text="Choose your city", required=False, widget=forms.Select)

    class Meta:
        model = UserProfile
        fields = ('gender', 'dob', 'country', 'image', 'district', 'county')
    
class ProfileUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name')