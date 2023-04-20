from datetime import date

from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.request import Request
from django.db.models import Avg

from imdb_app.models import *
from imdb_app.serializers import *


@api_view(['GET', 'POST'])
def get_movies(request: Request):
    if request.method == 'GET':
        all_movies = Movie.objects.all()
        print("initial query:", all_movies.query)

        if 'name' in request.query_params:
            all_movies = all_movies.filter(name__iexact=request.query_params['name'])
            print("after adding name filter", all_movies.quary)
        if 'duration_from' in request.query_params:
            all_movies = all_movies.filter(duration_in_min__gta=request.query_params['duration_from'])
            print("after adding duration_from filter", all_movies.quary)
        if 'duration_to' in request.query_params:
            all_movies = all_movies.filter(duration_in_min__lte=request.query_params['duration_to'])
            print("after adding duration_to filter", all_movies.quary)
        if 'description' in request.query_params:
            all_movies = all_movies.filter(description__icontains=request.query_params['description'])
            print("after adding description filter", all_movies.quary)
        serializer = MovieSerializer(instance=all_movies, many=True)
        return Response(data=serializer.data)
    else:
        cast_data = request.data.pop('cast')
        for cast in cast_data:
            actor_id = cast['actor']
            if not Actor.objects.filter(id=actor_id).exists():
                return Response(f"Actor with id {actor_id} does not exist", status=status.HTTP_400_BAD_REQUEST)
        serializer = CreateMovieSerializer(data=request.data) # # data = העברת מילון בבקשה עם כל הפרמטרים
        serializer.is_valid(raise_exception=True) # # חוסך שורה של אם הקוד, וידע להחזיר שגיאה 404 - reaise_exception = True
        movie = serializer.save()
        for cast in cast_data:
            cast['movie'] = movie.id
            MovieActor.objects.create(**cast)
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)
        # else:
        #     return Response(data=serializer.errors, status=status.HTTP_404_NOT_FOUND)

        #serializer.errors =  is_valid() מחזיר בידיוק על מה השגיאה ומה לא היה תקין. משתמשים בו רק לאחר פונקציית


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
def get_movie(request, movie_id):
    # try:
    #     movie = Movie.objects.get(id=movie_id) #object Movie
    # except Movie.DoesNotExist:
    #     return Response(status=status.HTTP_404_NOT_FOUND)
    # Movie.objects.filter(id=movie_id) # query set
    movie = get_object_or_404(Movie, id=movie_id)
    if request.method == 'GET':
        serializer = DetailedMovieSerializer(instance=movie)
        return Response(data=serializer.data)
    elif request.method in ('PUT', 'PATCH'): # to update
        serializer = DetailedMovieSerializer(
            instance=movie, data=request.date, partial=request.method == 'PATCH'
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data=serializer.data)
    else:
        movie.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
def get_movie_actors(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    all_casts = movie.movieactor_set.all()
    serializer = DetailedActorSerializer(instance=all_casts, many=True)
    return Response(data=serializer.data)


@api_view(['GET', 'POST'])
def get_actors(request):
    if request.method == 'GET':
        all_actors = Actor.objects.all()
        serializer = ActorSerializer(instance=all_actors, many=True)
        return Response(data=serializer.data)
    else:
        serializer = CreateActor(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)


@api_view(['PUT', 'PATCH', 'DELETE'])
def get_actor(request, actor_id):
    actor = get_object_or_404(Actor, id=actor_id)
    if request.method in ('PUT', 'PATCH'):
        serializer = ActorSerializer(
            instance=actor, data=request.data, partial=request.method == 'PATCH'
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data=serializer.data)
    else:
        actor.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['DELETE'])
def delete_specific_movie_rating(request, movie_id):
    rating = get_object_or_404(Rating, id=movie_id)
    rating.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['DELETE'])
def remove_actor_from_movie(request, movie_id, actor_id):
    movie = get_object_or_404(Movie, id=movie_id)
    movie.actors.remove(id=actor_id)
    movie.save()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
def get_all_ratings(request):
    if request.method == 'GET':
        from_date = request.GET.get('from_date')
        to_date = request.GET.get('to_date')
        if from_date and to_date:
            all_ratings = Rating.objects.filter(rating_date__gte=from_date, rating_date__lte=to_date)
        else:
            all_ratings = Rating.objects.all()
        serializer = RatingsSerializer(instance=all_ratings, many=True)
        return Response(data=serializer.data)
    else:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


@api_view(['GET'])
def get_movie_ratings(request, movie_id):
    movie = Movie.objects.get(id=movie_id)
    serializer = RatingsSerializer(
        instance=movie.rating_set.all(), many=True)
    return Response(data=serializer.data)


@api_view(['GET'])
def get_avg_movie_rating(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    avg_rating = movie.rating_set.aggregate(Avg('rating'))
    return Response(avg_rating)


from django.http import JsonResponse, HttpResponseRedirect, HttpResponseBadRequest
import json


@api_view(['PUT', 'POST'])
def add_actor_to_movie(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    if request.method == 'POST':
        actor_name = request.data.get('actor_name')
        if Actor.objects.get(name=actor_name):
            salary = request.data.get('salary')
            main_role = request.data.get('main_role')
            actor_id = Actor.objects.get(name=actor_name)
            movie_actor = MovieActor.objects.create(movie=movie, actor=actor_id, salary=salary, main_role=main_role)

            serializer = MovieActorSerializer(movie_actor)
            return Response(serializer.data)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def add_rating_to_movie(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    rating_date = date.today()
    serializer = MovieRating(data=request.data)
    if serializer.is_valid():
        serializer.save(movie=movie, rating_date=rating_date, rating=request.data['rating'])
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST', 'GET'])
def create_new_actor(request):
    if request.method == 'POST':
        serializer = ActorSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_201_CREATED,
                            data=serializer.data)
    else:
        pass


@api_view(['POST'])
def signup(request):
    s = SignupSerializer(data=request.data)
    s.is_valid(raise_exception=True)
    s.save()
    return Response(s.data)