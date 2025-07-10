# # create app/signals.py
# app/signals.py
# app/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Profile

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    # Only create if not already created
    if created and not hasattr(instance, 'profile'):
        Profile.objects.create(user=instance)
