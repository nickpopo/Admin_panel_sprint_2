from django.db import models
from django.utils.translation import gettext_lazy as _
from model_utils.fields import AutoCreatedField, AutoLastModifiedField


class UpdatedCreatedMixin(models.Model):
    """
    An abstract base class model that provides self-updating
    ``created_at`` and ``updated_at`` fields.

    """
    created_at = AutoCreatedField(_('created_at'))
    updated_at = AutoLastModifiedField(_('updated_at'))

    class Meta:
        abstract = True


class CreatedMixin(models.Model):
    """
    An abstract base class model that provides self-updating
    ``created_at`` field.

    """
    created_at = AutoCreatedField(_('created_at'))

    class Meta:
        abstract = True
