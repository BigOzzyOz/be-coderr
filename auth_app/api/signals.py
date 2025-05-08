from django.db.models.signals import post_save
from django.dispatch import receiver
from profiles_app.models import Profile


@receiver(post_save, sender=Profile)
def edit_user_after_profile_update(sender, instance, **kwargs):
    """Update user fields after profile update."""
    user = instance.user
    user.first_name = instance.first_name
    user.last_name = instance.last_name
    user.email = instance.email
    user.save()
