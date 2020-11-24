import uuid

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from .utilities import CreatedMixin, UpdatedCreatedMixin


class Filmwork(UpdatedCreatedMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.TextField(_('название'), blank=False)
    description = models.TextField(_('описание'), blank=True)
    creation_date = models.DateField(_('дата создания фильма'), blank=True, null=True)
    certificate = models.TextField(_('сертификат'), blank=True)
    file_path = models.FileField(_('файл'), upload_to='film_works/', blank=True)
    rating = models.FloatField(_('рейтинг'), validators=[MinValueValidator(0)], blank=True, null=True)
    type = models.ForeignKey(
        'FilmworkType', 
        verbose_name=_("тип кинопроизведения"),
        related_name='films',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    #### Generate correct id through postgres uuid extension (in migration)
    genres = models.ManyToManyField('Genre', related_name='filmworks', through='GenreFilmwork')
    persons = models.ManyToManyField('Person', related_name='filmworks', through='PersonFilmwork')

    class Meta:
        db_table = settings.MOVIES_SCHEMA % 'filmwork'
        verbose_name = _('кинопроизведение')
        verbose_name_plural = _('кинопроизведения')

    def __str__(self):
        return self.title 


class FilmworkType(UpdatedCreatedMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.TextField(_('название'), blank=False)

    class Meta:
        db_table = settings.MOVIES_SCHEMA % 'filmwork_type'
        verbose_name = _('тип кинопроизведения')
        verbose_name_plural = _('типы кинопроизведений')

    def __str__(self):
        return self.name


##
# Associations tables
##
class PersonFilmwork(CreatedMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    person = models.ForeignKey('Person', on_delete=models.CASCADE)
    filmwork = models.ForeignKey('Filmwork', on_delete=models.CASCADE)
    role = models.ForeignKey('Career', verbose_name=_('роль'), on_delete=models.RESTRICT)

    class Meta:
        db_table = settings.MOVIES_SCHEMA % 'persons_filmworks'
        verbose_name = _('участники кинопроизведения')
        verbose_name_plural = _('участники кинопроизведений')
        unique_together = ('filmwork', 'person', 'role')


class GenreFilmwork(CreatedMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    genre = models.ForeignKey('Genre', on_delete=models.CASCADE)
    filmwork = models.ForeignKey('Filmwork', on_delete=models.CASCADE)

    class Meta:
        db_table = settings.MOVIES_SCHEMA % 'genres_filmworks'
        verbose_name = _('жанр кинопроизведения')
        verbose_name_plural = _('жанры кинопроизведений')
        unique_together = ('filmwork', 'genre')


##
# Proxies models
##
class FilmworkManager(models.Manager):

    def __init__(self, filmwork_type:str, **kwargs):
        super().__init__(**kwargs)
        self.filmwork_type = filmwork_type

    def get_queryset(self):
        return super(FilmworkManager, self).get_queryset().filter(type__name=self.filmwork_type)


class TVSeries(Filmwork):

    object = FilmworkManager('tv_show')

    class Meta:
        proxy = True
        verbose_name = _('сериал')
        verbose_name_plural = _('сериалы')


class Movie(Filmwork):

    object = FilmworkManager('movie')

    class Meta:
        proxy = True
        verbose_name = _('фильм')
        verbose_name_plural = _('фильмы')
