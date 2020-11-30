import logging
import uuid
from enum import Enum

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from .utilities import UpdatedCreatedMixin


logger = logging.getLogger()


class CareerNameEnum(Enum):
    ACTOR = 'actor'
    WRITER = 'writer'
    DIRECTOR = 'director'


class Career(UpdatedCreatedMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.TextField(_('название карьеры'))

    class Meta:
        db_table = settings.MOVIES_SCHEMA % 'career'
        verbose_name = _('карьера')
        verbose_name_plural = _('карьеры')

    def __str__(self):
        return self.name

    @staticmethod
    def get_career_id(career_name:str) -> str:
        """
        Filter Career model with career name and return str(id) else ''
        :param career_name
        :return str: id of the required career name
        """
        career = None
        try:
            career = Career.objects.get(name=career_name)
        except Career.DoesNotExist as error:
            logger.error(error)
            raise Career.DoesNotExist
        return career.id

