import django_filters
from django_filters import FilterSet
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, GenericViewSet

from imdb_app.models import Movie, Actor, Oscar
from imdb_app.serializers import MovieSerializer, ActorSerializer, DetailedMovieSerializer, CreateMovieSerializer, \
    CastForMovieSerializer, OscarSerializer


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


class OscarViewSet(ModelViewSet):
    serializer_class = OscarSerializer
    queryset = Oscar.objects.all()

    def get_queryset(self):
        queryset = Oscar.objects.all()
        year = self.request.query_params.get('year')
        from_year = self.request.query_params.get('from_year')
        to_year = self.request.query_params.get('to_year')
        nomination = self.request.query_params.get('nomination')

        if year:
            queryset = queryset.filter(year__iexact='year').values()
        if from_year:
            queryset = queryset.filter(year__gte__iexact='from_year').values()
        if to_year:
            queryset = queryset.filter(year__lte__iexact='to_year').values()
        if nomination:
            queryset = queryset.filter(nomination__iexact='nomination').values()

        return queryset

    def create_new_oscar(self, request):
        year = request.data.get('year')
        movie_id = request.data.get('movie_id')
        actor_id = request.data.get('actor_id')
        nomination = request.data.get('nomination')
        try:
            movie = Movie.objects.get(id=movie_id)
        except Movie.DoesNotExist:
            return Response({'error': f'Movie with id {movie_id} does not exist'})

        if actor_id:
            try:
                actor = Actor.objects.get(id=actor_id)
            except Actor.DoesNotExist:
                return Response({'error': f'Actor with id {actor_id} does not exist'})

        oscar = Oscar(year=year, movie_id=movie_id, actor_id=actor_id, nomination=nomination)
        oscar.save()
        serializer = OscarSerializer

        return Response(serializer.data)

