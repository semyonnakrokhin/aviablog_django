from django.dispatch import receiver
from django.db.models.signals import pre_save
from flights.models import Airframe


@receiver(pre_save, sender=Airframe)
def delete_previous_photo(sender, instance, **kwargs):
    if instance.pk:
        try:
            old_instance = sender.objects.get(pk=instance.pk)
            if old_instance.photo != instance.photo:
                old_instance.photo.delete(save=False)
        except sender.DoesNotExist:
            pass