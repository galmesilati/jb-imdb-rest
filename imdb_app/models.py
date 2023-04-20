import datetime
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

# Create your models here.


def validate_birth_date(val):
    if datetime.datetime.today().year - val < 5:
        raise ValidationError("Actor must be at least 5 years old")


class Actor(models.Model):
    name = models.CharField(max_length=256, db_column='name', null=False, blank=False)
    birth_year = models.IntegerField(db_column='birth_year', null=False,
                                     validators=[validate_birth_date])

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'actors'


def validate_year_before_now(val):
    if val > datetime.datetime.today().year:
        raise ValidationError("The year is in future")


class Movie(models.Model):
    name = models.CharField(max_length=256, db_column='name', null=False)
    description = models.TextField(db_column='description', null=False)
    duration_in_min = models.FloatField(db_column='duration', null=False)
    release_year = models.IntegerField(db_column='year', null=False,
                                       validators=[MinValueValidator(1800), validate_year_before_now])
    pic_url = models.URLField(max_length=512, db_column='pic_url', null=True)

    actors = models.ManyToManyField(Actor, through='MovieActor')

    class Meta:
        db_table = 'movies'


class Rating(models.Model):
    movie = models.ForeignKey('Movie', on_delete=models.CASCADE, )
    rating = models.SmallIntegerField(db_column='rating', null=False, validators=[MinValueValidator(1),
                                                                                  MaxValueValidator(10)])
    rating_date = models.DateField(db_column='rating_date', null=False, auto_now_add=True)

    # created_by = models.ForeignKey(User)
    class Meta:
        db_table = 'ratings'


class MovieActor(models.Model):
    actor = models.ForeignKey(Actor, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    salary = models.IntegerField()
    main_role = models.BooleanField(null=False, blank=False)

    def __str__(self):
        return f"{self.actor.name} in movie {self.movie.name}"

    class Meta:
        db_table = 'movie_actors'


class Director(models.Model):
    name = models.CharField(max_length=256, db_column='name', null=False, blank=False)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'directors'


class Oscar(models.Model):
    year = models.IntegerField(db_column='year', null=False,
                                       validators=[MinValueValidator(1800), validate_year_before_now])
    nomination = models.CharField(max_length=256, db_column='nomination', null=False)
    movie = models.ForeignKey('Movie', on_delete=models.CASCADE)
    actor = models.ForeignKey('Actor', on_delete=models.CASCADE, null=True, blank=True)
    director = models.ForeignKey('Director', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.nomination} in movie {self.movie}"

    class Meta:
        db_table = 'oscar'
