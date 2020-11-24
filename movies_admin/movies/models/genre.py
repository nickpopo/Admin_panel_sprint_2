import uuid

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from .utilities import UpdatedCreatedMixin


class Genre(UpdatedCreatedMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.TextField(_('название'), blank=False)
    description = models.TextField(_('описание'), blank=True)

    class Meta:
        db_table = settings.MOVIES_SCHEMA % 'genre'
        verbose_name = _('жанр')
        verbose_name_plural = _('жанры')

    def __str__(self):
        return self.name
