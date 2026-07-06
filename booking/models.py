from django.db import models
from django.contrib.auth.models import User
from movies.models import  Movie,Seat


class Booking(models.Model):
    STATUS_CHOICES =   [
        ('Booked','Booked'),
        ('Cancelled','Cancelled'),
    ]

    user = models.ForeignKey(User,on_delete =models.CASCADE)
    
    movie= models.ForeignKey(Movie,on_delete=models.CASCADE)
    
    # show = models.ForeignKey(Show,on_delete=models.CASCADE)

    seats = models.IntegerField()


    total_price = models.DecimalField(

        max_digits=10,
        decimal_places=2,
     default=0
    )


    booking_date = models.DateTimeField(auto_now_add=True)

    status = models.CharField(
        max_length=20,
        choices=[('Booked','Booked'),
                 ('Cancelled','Cancelled' )],
                 default= 'Booked'
    )


    def __str__(self):
        return f"{self.user.username} - {self.movie.title}"


# Create your models here.

class BookingSeat(models.Model):

    booking = models.ForeignKey(
        Booking,
        on_delete=models.CASCADE
    )

    seat = models.ForeignKey(
        Seat,
        on_delete=models.CASCADE
    )

    def __str__(self):
        return f"{self.booking.id } - {self.seat.seat_number}"
