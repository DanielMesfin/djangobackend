from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import UserProfile, SocialLink, Wallet

User = get_user_model()

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Create a UserProfile and Wallet when a new User is created.
    """
    if created:
        # Only create if they don't exist
        UserProfile.objects.get_or_create(user=instance)
        Wallet.objects.get_or_create(user=instance)

@receiver(post_save, sender=UserProfile)
def create_social_links(sender, instance, created, **kwargs):
    """
    Create SocialLink when a new UserProfile is created.
    """
    if created and not hasattr(instance, 'social_links'):
        SocialLink.objects.get_or_create(user_profile=instance)

@receiver(post_save, sender=User)
def ensure_user_has_profile(sender, instance, created, **kwargs):
    """
    Ensure User has a profile after save.
    This is a safer alternative to the pre_save signal.
    """
    if not created:  # Only for updates
        UserProfile.objects.get_or_create(user=instance)
