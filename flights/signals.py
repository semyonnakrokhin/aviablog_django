from django.dispatch import receiver
from django.db.models.signals import pre_save
from flights.models import Airframe, TrackImage, Meal


@receiver(pre_save, sender=Airframe)
@receiver(pre_save, sender=TrackImage)
@receiver(pre_save, sender=Meal)
def delete_previous_photo(sender, instance, **kwargs):
    print('SIGNAL')
    if instance.pk:
        try:
            old_instance = sender.objects.get(pk=instance.pk)
            if isinstance(old_instance, Airframe) and old_instance.photo != instance.photo:
                old_instance.photo.delete(save=False)
            elif isinstance(old_instance, TrackImage) and old_instance.track_img != instance.track_img:
                old_instance.track_img.delete(save=False)
            elif isinstance(old_instance, Meal) and old_instance.photo != instance.photo:
                old_instance.photo.delete(save=False)
        except sender.DoesNotExist:
            pass