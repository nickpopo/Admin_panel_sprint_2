from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import Q, F
from django.http import JsonResponse
from django.views.generic.list import BaseListView
from django.views.generic.detail import BaseDetailView
from movies.models import Filmwork, Career, CareerNameEnum


class MoviesApiMixin:
    model = Filmwork
    http_method_names = ['get']  # Список методов, которые реализует обработчик

    actor = Q(personfilmwork__role=Career.get_career_id(
        CareerNameEnum.ACTOR.value))
    writer = Q(personfilmwork__role=Career.get_career_id(
        CareerNameEnum.WRITER.value))
    director = Q(personfilmwork__role=Career.get_career_id(
        CareerNameEnum.DIRECTOR.value))

    selected_fields = (
                        'id',
                        'title',
                        'description',
                        'creation_date',
                        'rating',
                        )

    queryset = Filmwork.objects.prefetch_related('genres', 'persons').values(*selected_fields).annotate(
        type=F('type__name')).annotate(
        genres=ArrayAgg('genres__name', distinct=True)).annotate(
        actors=ArrayAgg('persons__full_name', filter=actor, distinct=True)).annotate(
        writers=ArrayAgg('persons__full_name', filter=writer, distinct=True)).annotate(
        directors=ArrayAgg('persons__full_name', filter=director, distinct=True))

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse(context)


class MoviesListApi(MoviesApiMixin, BaseListView):
    paginate_by = 50

    def get_context_data(self, *, object_list=None, **kwargs):
        queryset = object_list if object_list is not None else self.object_list
        page_size = self.get_paginate_by(queryset)

        if page_size:
            paginator, page, queryset, is_paginated = self.paginate_queryset(
                queryset, page_size)
            context = {
                'count': paginator.count,
                'total_pages': paginator.num_pages,
                'prev': page.number - 1 if page.number > 1 else None,
                'next': page.number + 1 if page.number + 1 < paginator.num_pages else None,
                'results': list(queryset)
            }

        return context

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse(context)


class MoviesDetailApi(MoviesApiMixin, BaseDetailView):
    # pk_url_kwarg = 'uuid'
    def get_context_data(self, **kwargs):
        return self.object
    

