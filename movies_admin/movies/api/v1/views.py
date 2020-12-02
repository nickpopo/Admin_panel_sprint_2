import logging

import django.db.utils
from django.conf import settings
from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import F, Q
from django.http import JsonResponse
from django.views.generic.detail import BaseDetailView
from django.views.generic.list import BaseListView
from movies.models import Career, CareerNameEnum, Filmwork

logger = logging.getLogger()


class MoviesApiMixin:
    model = Filmwork
    http_method_names = ['get']  # Список методов, которые реализует обработчик
    
    actor = writer = director = None
    try:
        actor = Q(personfilmwork__role=Career.get_career_id(
            CareerNameEnum.ACTOR))
        writer = Q(personfilmwork__role=Career.get_career_id(
            CareerNameEnum.WRITER))
        director = Q(personfilmwork__role=Career.get_career_id(
            CareerNameEnum.DIRECTOR))
    except (django.db.utils.ProgrammingError, Career.DoesNotExist) as error:
        logger.error(error)

    selected_fields = (
                        'id',
                        'title',
                        'description',
                        'creation_date',
                        'rating',
                        )

    queryset = Filmwork.objects.values(*selected_fields).annotate(
        type=F('type__name'),
        genres=ArrayAgg('genres__name', distinct=True),
        actors=ArrayAgg('persons__full_name', filter=actor, distinct=True),
        writers=ArrayAgg('persons__full_name', filter=writer, distinct=True),
        directors=ArrayAgg('persons__full_name', filter=director, distinct=True),
        )

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse(context)


class MoviesListApi(MoviesApiMixin, BaseListView):
    paginate_by = settings.DJANGO_ITEMS_PER_PAGE
    ordering = 'title'

    def get_context_data(self, *, object_list=None, **kwargs):
        queryset = object_list if object_list is not None else self.object_list
        page_size = self.get_paginate_by(queryset)

        if page_size:
            paginator, page, queryset, _ = self.paginate_queryset(
                queryset, page_size)
            context = {
                'count': paginator.count,
                'total_pages': paginator.num_pages,
                'prev': page.previous_page_number() if page.has_previous() else None,
                'next': page.next_page_number() if page.has_next() else None,
                'results': queryset
            }

        return context

    def render_to_response(self, context, **response_kwargs):
        context['results'] = list(context['results'])
        return JsonResponse(context)


class MoviesDetailApi(MoviesApiMixin, BaseDetailView):
    # pk_url_kwarg = 'uuid'
    def get_context_data(self, **kwargs):
        return self.object
    

