"""imdb_rest URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from imdb_app import views
from imdb_app.view_set import MovieViewSet, ActorViewSet

# http://127.0.0.1:8000/api/imdb/movies


# http://127.0.0.1:8000/api/imdb/movies
# http://127.0.0.1:8000/api/imdb/movies


router = DefaultRouter()
# לאן אני רוצה לנתב, ומפרק את זה לכמות היישויות בדאטהבייס
router.register('movies', MovieViewSet)
router.register('actors', ActorViewSet)

print(router.urls)

#movies/ POST, GET(list)
#movies/<int:movie_id> # PUT/PATCH, GET, DELETE

urlpatterns = [
    # path('movies', views.get_movies),
    # path('movies/<int:movie_id>', views.get_movie),


    # path('actors', views.get_actors),
    # path('actors/<int:actor_id>', views.get_actor),

    path('movie_actors/<int:movie_id>/<int:actor_id', views.remove_actor_from_movie),
    path('movies/<int:movie_id>/ratings', views.get_movie_ratings),
    path('movies/<int:movie_id>/ratings/avg', views.get_avg_movie_rating),
    path('movies/<int:movie_id>/actor', views.add_actor_to_movie),
    path('movies/<int:movie_id>/ratings/', views.add_rating_to_movie),
    path('movies/<int:movie_id>/actors', views.get_movie_actors),

    path('ratings', views.get_all_ratings),
    path('ratings/delete/<int:movie_id>/', views.delete_specific_movie_rating)

]

# Router-יוסיף את מה שיצרתי ב
urlpatterns.extend(router.urls)