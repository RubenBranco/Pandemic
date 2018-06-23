from django.shortcuts import render, redirect
from rest_framework import viewsets
from django.contrib.auth.models import User


def frontpage(request):
    return render(request, "pandemic/frontpage.html", context={'user': request.user})

def howto(request):
    return render(request, "pandemic/howto.html")

def aboutus(request):
    return render(request, "pandemic/about.html")
