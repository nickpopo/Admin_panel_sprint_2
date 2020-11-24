import datetime
from django.dispatch import receiver
from django.db.models.signals import post_save, pre_save

# https://docs.djangoproject.com/en/3.1/ref/signals/
@receiver(post_save, sender='movies.Person')
def congratulatory(sender, instance, created, **kwargs):
    if created and instance.birth_day == datetime.date.today():
        print(f"У {instance.full_name} сегодня день рождения! 🥳")


# post_save.connect(receiver=congratulatory, sender='movies.Person',
#                   weak=True, dispatch_uid='congratulatory_signal')
