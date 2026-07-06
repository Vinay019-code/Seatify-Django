from django.db import models
from django.contrib.auth.models import User


class Movie(models.Model):
    title=models.CharField(max_length=200)
    description = models.TextField()
    duration = models.IntegerField()
    release_date = models.DateField()
    available_seats =models.IntegerField(default=100)
    poster=models.ImageField(
        upload_to='posters/',
        blank=True,
        null=True
    )
    category = models.CharField(
        max_length=50,
        default='Action'
    )

    ticket_price =models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=250
    )
    # poster = models.ImageField(upload_to='posters/')
    # language =models.CharField(max_length=100)
    def __str__(self):
        return self.title
# Create your models here.
class Show(models.Model):
    movie=models.ForeignKey(Movie,on_delete=models.CASCADE)
    show_date=models.DateField()
    show_time=models.TimeField()
    price = models.DecimalField(max_digits = 8, decimal_places=2)

    def __str__(self):
        return f"{self.movie.title} - {self.show_time}"

class Seat(models.Model):
    # show = models.ForeignKey(Show,on_delete=models.CASCADE)
    # seat_number= models.CharField(max_length=10)
    # is_booked = models.BooleanField(default=False)

    movie =models.ForeignKey(
        Movie,
        on_delete=models.CASCADE
    )
    seat_number= models.CharField(
        max_length=10
    )

    is_booked =models.BooleanField(
        default=False
    )


    def __str__(self):
        return self.seat_number
    

class Review(models.Model):

    movie = models.ForeignKey(
        Movie,
        on_delete=models.CASCADE
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    rating = models.IntegerField()

    comment = models.TextField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=[
                'movie',
                'user'
                  ],
                  name='one_review_per_movie'
        )

    ]


    def __str__(self):
        return f"{self.user.username} - {self.movie.title}"