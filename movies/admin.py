from django.contrib import admin
from .models import Movie,Seat,Show ,Review
# Register your models here.

admin.site.register(Movie)
admin.site.register(Show)
admin.site.register(Seat)
admin.site.register(Review)