from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django_countries.fields import CountryField

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    gender = models.CharField(max_length=6, blank=True)
    dob = models.DateField(blank=True, null=True)
    country = CountryField(blank=True)
    image = models.ImageField(blank=True, null=True, upload_to='thumbnails')
    district = models.CharField(max_length=32, blank=True, null=True)
    county = models.CharField(max_length=32, blank=True, null=True)

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    instance.userprofile.save()

class District(models.Model):
    name = models.CharField(max_length=32)


class Municipality(models.Model):
    name = models.CharField(max_length=32)
    district = models.ForeignKey(District, on_delete=models.CASCADE)

