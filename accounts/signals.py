from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Profile

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        role = "admin" if instance.is_superuser else "student"
        Profile.objects.create(user=instance, name=instance.get_full_name() or instance.username,
                               email=instance.email, role=role)
    else:
        Profile.objects.get_or_create(user=instance)

