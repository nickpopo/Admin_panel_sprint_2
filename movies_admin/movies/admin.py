from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import (Actor, Career, CareerPerson, Filmwork, FilmworkType,
                     Genre, GenreFilmwork, Movie, Person, PersonFilmwork,
                     TVSeries)


class PersonFilmworkInline(admin.TabularInline):
    model = PersonFilmwork
    readonly_field = ["created_at"]
    autocomplete_fields = ['person']
    extra = 1


class GenreFilmworkInline(admin.TabularInline):
    model = GenreFilmwork
    readonly_field = ["created_at"]
    autocomplete_fields = ['genre']
    extra = 1


@admin.register(Filmwork)
class FilmworkAdmin(admin.ModelAdmin):
    # отобажение полей в списке
    list_display =  ('title', 'type', 'description', 'creation_date', 'rating')

    # фильтрация в списке
    list_filter = ('type',)

    # поиск по полям
    search_fields = ('title', 'description', 'id')

    # порядок следования полей в форме создания/редактирования
    fields = (
        'title', 'type', 'description', 'creation_date', 'certificate',
        'file_path', 'rating',
    )

    inlines = [
        PersonFilmworkInline,
        GenreFilmworkInline,
    ]


@admin.register(TVSeries)
class TVSeriesAdmin(admin.ModelAdmin):
    # отобажение полей в списке
    list_display =  ('title', 'type', 'description', 'creation_date', 'rating')

    # поиск по полям
    search_fields = ('title', 'description', 'id')

    # порядок следования полей в форме создания/редактирования
    fields = (
        'title', 'type', 'description', 'creation_date', 'certificate',
        'file_path', 'rating',
    )

    inlines = [
        PersonFilmworkInline,
        GenreFilmworkInline,
    ]


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    # отобажение полей в списке
    list_display =  ('title', 'type', 'creation_date', 'rating')

    # поиск по полям
    search_fields = ('title', 'description', 'id')

    # порядок следования полей в форме создания/редактирования
    fields = (
        'title', 'type', 'description', 'creation_date', 'certificate',
        'file_path', 'rating',
    )

    inlines = [
        PersonFilmworkInline,
        GenreFilmworkInline,
    ]


class FilmworkPersonInline(admin.TabularInline):
    model = PersonFilmwork
    search_fields = ("title",)
    autocomplete_fields = ('filmwork',)
    extra = 0


class CareerPersonInline(admin.TabularInline):
    model = CareerPerson
    extra = 0

    fields = (
        'career', 'date_start', 'date_finish',
    )


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'persons_films')

    fields = (
        'full_name', 'gender', 'birth_day',
    )

    inlines = [
        CareerPersonInline,
        FilmworkPersonInline,
    ]

    # поиск по полям
    search_fields = ('full_name', 'id')

     # фильтрация в списке
    list_filter = ('careers',)

    def persons_films(self, obj):
        in_filmworks = []
        for filmwork in obj.filmworks.all():
            in_filmworks.append(filmwork.title)
        return ','.join(in_filmworks)

    persons_films.short_description = _('фильмы')


@admin.register(Actor)
class ActorAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'persons_films')

    def persons_films(self, obj):
        in_filmworks = []
        for filmwork in obj.filmworks.all():
            in_filmworks.append(filmwork.title)
        return ','.join(in_filmworks)

    persons_films.short_description = _('фильмы')

    def upper_case_name(self, obj):
        return ("%s %s" % (obj.full_name, obj.full_name)).upper()

    upper_case_name.short_description = 'Name'


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    search_fields = ['name']
    readonly_fields = ["created_at", "updated_at"]


@admin.register(FilmworkType)
class FilmworkTypeAdmin(admin.ModelAdmin):
    pass


@admin.register(Career)
class CareerAdmin(admin.ModelAdmin):
    fields = (
        'name',
    )

