# userprofile/models.py
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from items.models import Listing

class UserProfile(models.Model):
    user = models.OneToOneField(User, related_name='profile', on_delete=models.CASCADE)
    favorites = models.ManyToManyField(Listing, blank=True, related_name='favorited_by')  # each user profile has multiple favorite listings
    # user_items = models.ManyToManyField(Listing, blank=True, related_name='user_items')
    is_verified = models.BooleanField(default=False)
    
    def __str__(self):
        return self.user.email

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        print(f"Creating profile for {instance.username}")  # Debugging
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    try:
        print(f"Saving profile for {instance.username}")  # Debugging
        instance.profile.save()
    except UserProfile.DoesNotExist:
        print(f"User {instance.username} has no profile, creating now...")
        UserProfile.objects.create(user=instance)
