from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth import login, authenticate, update_session_auth_hash
from .forms import RegisterForm, ProfileForm, ProfileUserForm
from .models import UserProfile, District, Municipality
from django.http import HttpResponse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from .tokens import RegistrationTokenizer
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm
from django.core.mail import EmailMessage, get_connection
import os
from pandemic.settings import BASE_DIR
from rest_framework import viewsets
from rest_framework.response import Response
from .serializers import DistrictSerializer, MunicipalitySerializer

def register(request):
    if request.user.is_authenticated:
        return redirect('frontpage')
    elif request.method == "POST":
        user_form = RegisterForm(request.POST)
        profile_form = ProfileForm(request.POST)
        if user_form.is_valid() and profile_form.is_valid():
            connection = get_connection()
            new_user = user_form.save(commit=False)
            new_user.is_active = False
            new_user.save()
            # Profile
            new_user.userprofile.gender = request.POST['gender']
            new_user.userprofile.dob = request.POST['dob']
            new_user.userprofile.country = request.POST['country']
            if 'district' in request.POST:
                new_user.userprofile.district = request.POST['district']
                new_user.userprofile.county = request.POST['county']
            new_user.save()
            domain = get_current_site(request)
            email_subject = "Confirm Registration"
            context = {
                'user': new_user,
                'domain': domain,
                'uid': urlsafe_base64_encode(force_bytes(new_user.pk)).decode(),
                'token': RegistrationTokenizer.make_token(new_user),
            }
            message = render_to_string("registration/registration_email.html", context)
            email = EmailMessage(email_subject, message, to=[user_form.cleaned_data.get('email')],
            connection=connection)
            email.send()
            connection.close()
            return render(request, 'registration/registration_done.html')
    return render(request, 'registration/registration.html', {'user_form': (RegisterForm() if request.method == "GET" else user_form), 'profile_form': (ProfileForm() if request.method == "GET" else profile_form)})

def registration_activate(request, uidb64, token):
    """
    """
    try:
        uidb64 = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uidb64)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and RegistrationTokenizer.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        reg_status = "success"
    else:
        reg_status = "insuccess"
    return render(request, 'registration/registration_confirmation_done.html', {'reg_status': reg_status})
        

def profile(request, username):
    req_user = get_object_or_404(User, username=username)
    is_owner = (request.user.is_authenticated and request.user.username == req_user.username)
    context = {
        'req_user': req_user,
        'is_owner': is_owner,
        'req_username': username,
    }
    return render(request, "pandemic/profile.html", context=context)

def edit_profile(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            past_image_path = (request.user.userprofile.image.path if request.user.userprofile.image.name != '' else None)
            user_form = ProfileUserForm(request.POST, instance=request.user)
            profile_form = ProfileForm(request.POST, request.FILES, instance=request.user.userprofile)
            if user_form.is_valid() and profile_form.is_valid():
                if request.user.userprofile.image.name != '' and request.FILES.get('image', False):
                    if past_image_path is not None:
                        os.remove(os.path.join(BASE_DIR, 'pandemic', past_image_path))
                user_form.save()
                return redirect('profile', username=request.user.username)
        else:
            user_form = ProfileUserForm(instance=request.user)
            profile_form = ProfileForm(instance=request.user.userprofile)
        context = {
            'user_form': user_form,
            'profile_form': profile_form,
            'req_user': request.user,
        }
        return render(request, 'pandemic/edit_profile.html', context=context)
    else:
        return redirect('login')

def change_password(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            form = PasswordChangeForm(request.user, request.POST)
            if form.is_valid():
                user = form.save()
                update_session_auth_hash(request, user)
                connection = get_connection()
                email_subject = 'You just changed your password'
                context = {
                    'user': user,
                    'domain': get_current_site(request)
                }
                message = render_to_string("registration/change_password_email.html", context)
                email = EmailMessage(email_subject, message, to=[user.email],
                connection=connection)
                email.send()
                connection.close()
                return redirect('/user/{}'.format(user.username))
        return render(request, 'registration/change_password.html', context={'form': PasswordChangeForm(request.user) if request.method == "GET" else form})
    else:
        return redirect('login')

class DistrictViewSet(viewsets.ModelViewSet):
    queryset = District.objects.all()
    serializer_class = DistrictSerializer

    def retrieve(self, request, pk=None):
        queryset = District.objects.all()
        district = get_object_or_404(queryset, pk=pk)
        counties = Municipality.objects.filter(district=district)
        serializer = MunicipalitySerializer(counties, many=True)
        return Response(serializer.data)