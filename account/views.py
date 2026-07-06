from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from django.contrib.auth import (authenticate,login,logout)
from .form import RegisterForm
from django.contrib.auth.decorators import login_required
from booking.models import Booking
from movies.models import Review

def register_view(request):
    if request.method =='POST':
         
        form = RegisterForm(request.POST)

        if form.is_valid():

            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password']
            )


            return redirect('login')
    else:
        form = RegisterForm()


    return render(
        request,
        'account/register.html',
        {'form': form}
    )





def login_view(request):

    if request.method =='POST':

        username = request.POST['username']
        password =request.POST['password']

        user = authenticate(
            username=username,
            password=password
        )

        if user:
            login(request,user)

            return redirect('home')
        
    return render(request,
                  'account/login.html')

def logout_view(request):

    logout(request)
    return redirect('home')




@login_required
def profile(request):

    bookings = Booking.objects.filter(
        user=request.user
    )

    total_bookings = bookings.count()

    total_spent = sum(
        booking.total_price
        for booking in bookings
        if booking.status == 'Booked'
    )
    reviews_count = Review.objects.filter(
    user=request.user
    ).count()

    return render(
        request,
        'account/profile.html',
        {
            'bookings': bookings[:5],
            'total_bookings': total_bookings,
            'total_spent': total_spent,
            'reviews_count': reviews_count,
        }
    )