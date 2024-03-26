from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import User, userProfile

@receiver(post_save, sender = User)
def post_save_create_profile_receiver(sender, instance, created, **kwargs):
    if created:
        userProfile.objects.create(user=instance)
    else:
        try:
            profile = userProfile.objects.get(user=instance)
            profile.save()
        except:
            userProfile.objects.create(user=instance)
        print('User Updated')

@receiver(pre_save, sender = User)
def pre_save_profile_receiver(sender, instance, **kwargs):
    print('User is being Created')
