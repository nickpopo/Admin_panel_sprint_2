import uuid

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from .utilities import CreatedMixin, UpdatedCreatedMixin


class Gender(models.TextChoices):
    MALE = 'male', _('мужской')
    FEMALE = 'female', _('женский')


class Person(UpdatedCreatedMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    full_name = models.TextField(_('полное имя'), blank=False)
    birth_day = models.DateField(_('дата рождения'), blank=True, null=True)
    gender = models.TextField(_('пол'), choices=Gender.choices, blank=True)
    careers = models.ManyToManyField('Career', related_name='persons', through='CareerPerson')

    class Meta:
        db_table = settings.MOVIES_SCHEMA % 'person'
        verbose_name = _('персона')
        verbose_name_plural = ('персоны')

    def __str__(self):
        return self.full_name


##
# Associations tables
##
class CareerPerson(CreatedMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    career = models.ForeignKey('Career', verbose_name=_('профессия'), on_delete=models.RESTRICT)
    person = models.ForeignKey('Person', on_delete=models.CASCADE)
    date_start = models.DateField(_('дата начала карьеры'), blank=True, null=True)
    date_finish = models.DateField(_('дата завершения карьеры'), blank=True, null=True)

    class Meta:
        db_table = settings.MOVIES_SCHEMA % 'careers_persons'
        verbose_name = 'карьера'
        verbose_name_plural = 'карьеры'
        unique_together = ('person', 'career')


##
# Proxies models
##
class ActorManager(models.Manager):
    
    def get_queryset(self):
        return super(ActorManager, self).get_queryset().filter(careers__name='actor')


class Actor(Person):

    objects = ActorManager()

    class Meta:
        proxy = True
