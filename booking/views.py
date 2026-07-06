from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
from movies.models import Movie,Seat
from .models import Booking ,BookingSeat
from .forms import BookingForm
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.admin.views.decorators import staff_member_required
# import io ,base64 ,matplotlib.pyplot as plt
from collections import Counter
from django.db.models import Count,Sum


@login_required
def book_ticket(request,movie_id):

    movie = get_object_or_404(
        Movie,
        id=movie_id,
       
    )

    if request.method =="POST":
        form =BookingForm(request.POST)

        if form.is_valid():

            seats= form.cleaned_data['seats']

            if seats > movie.available_seats:

                return render(
                    request,
                    'booking/book_ticket.html',
                    {
                        'movie': movie,
                        'form': form,
                        'error':
                        'Not enough seats available'
                    }
                )
            

            Booking.objects.create(
                user= request.user,
                movie=movie,
                seats=seats
                #  total_price=total_price
            )


            movie.available_seats -=seats
            movie.save()

            return redirect('home')
        

    else:
        form=BookingForm()


    return render(
        request,
        'booking/book_ticket.html',
        {
            'movie': movie,
            'form':form
        }
    )
# Create your views here.


@login_required
def booking_history(request):

    bookings = Booking.objects.filter(
        user=request.user

    ).order_by('-booking_date')

    return render(
        request,
        'booking/history.html',
        {
            'bookings': bookings
        }
    )


@login_required
def cancel_booking(request,booking_id):

    booking = get_object_or_404(
        Booking,
        id=booking_id,
        user=request.user
    )

    if booking.status == 'Booked':
        seat_links = BookingSeat.objects.filter(
            booking=booking
        )

        for item in seat_links:
             seat = item.seat
             seat.is_booked = False
             seat.save()
        
        booking.status='Cancelled'
        booking.save()

        booking.movie.available_seats += booking.seats
        booking.movie.save()

        

    return redirect('booking_history')
    


@login_required
def select_seats(request,movie_id):
    movie =get_object_or_404(
        Movie,
        id=movie_id
    )
    seats = Seat.objects.filter(
        movie=movie
    )
    if request.method =="POST":
        selected =request.POST.getlist(
            'seats'
        )
        if not selected:
            return render(
        request,
        'booking/select_seats.html',
        {
            'movie':movie,
            'seats':seats,
            'error':'Select at least one seat'
        }
    )

        for seat_id in selected:
            seat =Seat.objects.get(
                id=seat_id
            )

            seat.is_booked =True
            seat.save()

        # booking =Booking.objects.create(
        #     user=request.user,
        #     movie=movie,
        #     seats=len(selected),
        #     total_price=(
        #         len(selected)*movie.ticket_price
        #     )
        # )
        # for seat_id in selected:
        #     seat = Seat.objects.get(
        #         id=seat_id
        #         )

        #     BookingSeat.objects.create(
        #              booking=booking,
        #                 seat=seat
        #                 )

        #     seat.is_booked = True
        #     seat.save()

        # movie.available_seats -= len(selected)
        # movie.save()

        # return redirect(
        #     'booking_history'
        # )
        request.session['movie_id'] =movie.id
        request.session['selected_seats']= selected

        return redirect(
            'payment_page'
        )

        

    
    
    return render(
     request,
        'booking/select_seats.html',
        {
            'movie':movie,
            'seats':seats
        }
    )



@login_required
def payment_page(request):

    movie_id =request.session.get('movie_id')
    selected = request.session.get('selected_seats')

    movie = Movie.objects.get(id=movie_id)
    total_price =(
        len(selected)*movie.ticket_price
    )

    if request.method =="POST":
        booking =Booking.objects.create(
            user =request.user,
            movie=movie,
            seats=len(selected),
            total_price=total_price
        )


        for seat_id in selected:
            seat=Seat.objects.get(id=seat_id)
            BookingSeat.objects.create(
                booking=booking,
                seat=seat
            )

            seat.is_booked=True
            seat.save()

        movie.available_seats-=len(selected)
        movie.save()

        seat_numbers=",".join(
            [
                item.seat.seat_number
                for item in booking.bookingseat_set.all()
            ]
        )
        send_mail(
            subject='BookMyShow Ticket Confirmation',
            message =f'''

            Movie:{movie.title}
            Seats: {seat_numbers}

            Total Price: ₹{booking.total_price}

            Status: {booking.status}

            Thank you for booking with BookingMyShow.
            ''',

                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[
                    request.user.email
                ],
                fail_silently =False

        )


        del request.session['movie_id']
        del request.session['selected_seats']

        return redirect('booking_history')


    return render(
        request,
        'booking/payment.html',
        {
            'movie':movie,
            'seat_count': len(selected),
            'total_price':total_price
        }
    )


@login_required
def download_ticket(request, booking_id):

    booking = get_object_or_404(
        Booking,
        id=booking_id,
        user=request.user
    )

    response = HttpResponse(
        content_type='application/pdf'
    )

    response['Content-Disposition'] = (
        f'attachment; filename="ticket_{booking.id}.pdf"'
    )

    pdf = canvas.Canvas(response)

    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(200, 800, "BOOKMYSHOW TICKET")

    pdf.setFont("Helvetica", 12)

    pdf.drawString(
        100,
        750,
        f"Booking ID: {booking.id}"
    )

    pdf.drawString(
        100,
        720,
        f"Movie: {booking.movie.title}"
    )

    seat_numbers = ", ".join(
        [
            item.seat.seat_number
            for item in booking.bookingseat_set.all()
        ]
    )

    pdf.drawString(
        100,
        690,
        f"Seats: {seat_numbers}"
    )

    pdf.drawString(
        100,
        660,
        f"Total Price: ₹{booking.total_price}"
    )

    pdf.drawString(
        100,
        630,
        f"Status: {booking.status}"
    )

    pdf.drawString(
        100,
        600,
        f"Date: {booking.booking_date.strftime('%d-%m-%Y')}"
    )

    pdf.drawString(
        100,
        550,
        "Enjoy Your Movie!"
    )

    pdf.save()

    return response


@staff_member_required
def admin_dashboard(request):
    total_movies =Movie.objects.count()
    total_users = User.objects.count()

    total_bookings = Booking.objects.filter(
        status='Booked'
    ).count()

    total_revenue= sum(
        booking.total_price
        for booking in Booking.objects.filter(
            status='Booked'
        )
    )

    total_seats=sum(
        movie.available_seats
        for movie in Movie.objects.all()
    )

    recent_bookings =Booking.objects.order_by(
        '-booking_date'
    )[:5]

    return render(
        request,
        'booking/admin_dashboard.html',
        {
            'total_movies': total_movies,
            'total_users':total_users,
            'total_bookings': total_bookings,
            'total_revenue': total_revenue,
            'total_seats':total_seats,
            'recent_bookings': recent_bookings,
        }
    )


@staff_member_required
def analytics_dashboard(request):
    total_movies = Movie.objects.count()

    total_users = User.objects.count()

    total_bookings = Booking.objects.count()
    total_revenue = (
        Booking.objects
        .filter(status='Booked')
        .aggregate(total=Sum('total_price'))
    )['total'] or 0
  
  
  
  
  
    movie_stats = (
        Booking.objects
        .filter(status='Booked')
        .values('movie__title')
        .annotate(total=Count('id'))
        .order_by('-total')
    )

    booking_status = (
        Booking.objects
        .values('status')
        .annotate(total=Count('id'))
    )


    # bookings =Booking.objects.filter(
    #     status='Booked'
    # )

    # movie_names=[
    #     booking.movie.title
    #     for booking in  bookings
    # ]


    # movie_count =Counter(movie_names)

    # plt.figure(figsize=(6,4))
    # plt.bar(
    #     movie_count.keys(),
    #     movie_count.values()
    # )

    # plt.title(
    #     "Bookings Per Movie"
    # )

    # plt.xticks(rotation=20)

    # buffer =io.BytesIO()


    # plt.savefig(
    #     buffer,
    #     format='png'
    # )

    # buffer.seek(0)

    # image_png=buffer.getvalue()

    # buffer.close()

    # graph=base64.b64encode(
    #     image_png
    # ).decode('utf-8')


    # plt.close()

    return render(
        request,
        'analytics_dashboard.html',
        {
            "total_movies": total_movies,
            "total_users": total_users,
            "total_bookings": total_bookings,
            "total_revenue": total_revenue,
            'movie_stats': movie_stats,
            "booking_status": booking_status,
        },
    )