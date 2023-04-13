import django_filters
from django_filters import FilterSet
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, GenericViewSet

from imdb_app.models import Movie, Actor
from imdb_app.serializers import MovieSerializer, ActorSerializer, DetailedMovieSerializer, CreateMovieSerializer, \
    CastForMovieSerializer

class MovieFilterSet(FilterSet):

    name = django_filters.CharFilter(field_name='name', lookup_expr='iexact')
    duration_from = django_filters.NumberFilter('duration_in_min', lookup_expr='gte')
    duration_to = django_filters.NumberFilter('duration_in_min', lookup_expr='lte')
    # description = django_filters.CharFilter(field_name='name', lookup_expr='icontains')

    class Meta:
        model: Movie
        fields = ['release_year']


class MovieViewSet(mixins.CreateModelMixin,
                   mixins.RetrieveModelMixin,
                   mixins.UpdateModelMixin,
                   mixins.ListModelMixin,
                   GenericViewSet):
    serializer_class = MovieSerializer
    queryset = Movie.objects.all()

    @action(methods=['GET'], detail=True, url_path='actors')
    def actors(self):
        movie = self.get_object()
        all_casts = movie.movieactor_set.all()
        serializer = CastForMovieSerializer(instance=all_casts, many=True)
        return Response(data=serializer.data)

    # לנתב לאיזה סיריאלייזר לגשת
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return DetailedMovieSerializer
        elif self.action == 'create':
            return CreateMovieSerializer
        else:
            return super().get_serializer_class()
            # return MovieSerializer

    # def create(self, request, *args, **kwargs):
    #     serializer = self.get_serializer(data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #     self.perform_create(serializer)
    #     headers = self.get_success_headers(serializer.data)
    #     return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class ActorViewSet(ModelViewSet):
    serializer_class = ActorSerializer
    queryset = Actor.objects.all()





