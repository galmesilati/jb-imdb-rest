from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import transaction
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from imdb_app.models import Movie, Actor, MovieActor, Rating, Oscar


# class MovieSerializer(serializers.Serializer):
#     name = serializers.CharField()
#     release_year = serializers.IntegerField()
#     description = serializers.CharField()


class MovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        # fields = '__all__'
        fields = ['id', 'name', 'release_year', 'duration_in_min', 'pic_url']
        # or : exclude תחזיר הכל חוץ ממה שכתוב בתוך
        # depth : יחזיר את האובייקט כולו במקרים של אובייקטים מסג מילון או רשימות למשל


class DetailedMovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        exclude = 'actors'


class ActorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Actor
        fields = '__all__'
        extra_kwargs = {
            'birth_year': {
                # for optional field
                'required': False,
                'validators': [MinValueValidator(5)]
            }
        }


class DetailedActorSerializer(serializers.ModelSerializer):
    class Meta:
        model = MovieActor
        # fields = '__all__'
        exclude = ['id', 'movie']
        depth = 1


class RatingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        exclude = ['id', 'movie']


class RatingMovieSerializers(serializers.ModelSerializer):
    class Meta:
        model = Rating
        exclude = ['id', 'movie', 'rating_date']



class CreateActor(serializers.ModelSerializer):
    class Meta:
        model = Actor
        fields = ['id', 'name', 'birth_year']
        extra_kwargs = {
            'id': {'read_only': True}
        }


class MovieActorSerializer(serializers.ModelSerializer):
    class Meta:
        model = MovieActor
        fields = '__all__'


class MovieRating(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = ['id', 'rating_date', 'rating']


class CastForMovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = MovieActor
        fields = ['actor', 'salary', 'main_role']


class CreateMovieSerializer(serializers.ModelSerializer):
    cast = CastForMovieSerializer(required=False, many=True)

    class Meta:
        model = Movie
        fields = ['id', 'name', 'description', 'duration_in_min', 'release_year', 'cast']
        extra_kwargs = {
            'id': {'read_only': True}
        }
        # validate unique movie name
        validators = [
            UniqueTogetherValidator(
                queryset=Movie.objects.all(),
                fields=['name']
            )
        ]

    def create(self, validated_data):
        # יריץ פקודות עד שהקוד יסתיים ואז יעדכן שינויים , בזמן הריצה אף אחד לא רואה את השינויים
        with transaction.atomic():
            cast_data = validated_data.pop('cast')
            movie = Movie.objects.create(**validated_data)
            for cast in cast_data:
                MovieActor.objects.create(**cast, movie_id=movie.id)
            return movie

    def validate(self, attrs):
        if attrs['release_year'] <= 1920 and attrs['duration_in_min'] >= 60:
            raise ValidationError('Old movies supposed to me short')
        return attrs


class OscarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Oscar
        fields = '__all__'
        extra_kwargs = {
            'actor': {
                'required': False,  # for optional value
                'validators': None,
            },
            'director': {'required': False}
        }


class SignupSerializer(serializers.ModelSerializer):

    password = serializers.CharField(max_length=128, validators=validate_password, write_only=True)

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'password']
        extra_kwargs = {
            'email': {'required': True},
            'username': {'read_only': True}
        }
        # validate unique movie name
        validators = [
            UniqueTogetherValidator(User.objects.all(), ['email'])
        ]

    def create(self, validated_data):
        user = User.objects.create(username=validated_data['email'],
                                   email=validated_data['email'],
                                   first_name=validated_data.get(['first_name', '']),
                                   last_name=validated_data.get(['last_name', '']))

        # set_password - מריץ את ההאש מחזיר את הסטרינג הארוך ובודק את תקינות הססמא
        user.set_password(validated_data['password'])
        user.save()
        return user

