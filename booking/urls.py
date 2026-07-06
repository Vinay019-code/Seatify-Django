from django.urls import path 
from . import views 

urlpatterns =[
    path(
        'book/<int:movie_id>/',
        views.book_ticket,
        name='book_ticket'
    ),
    # path(
    #     'book/<int:movie_id>/',
    #     views.book_ticket,
    #     name='book_ticket'
    # ),

    path(
        'history/',
        views.booking_history ,
        name='booking_history'
    ),
   path(
    'cancel/<int:booking_id>/',
    views.cancel_booking,
    name='cancel_booking'
),

    path(
        'select-seats/<int:movie_id>/',
        views.select_seats,
        name='select_seats'
    ),
    path(
        'payment/',
        views.payment_page,
        name='payment_page'
    ),
    path(
    'ticket/<int:booking_id>/',
    views.download_ticket,
    name='download_ticket'
),


    path(
        'admin-dashboard/',
        views.admin_dashboard,
        name='admin_dashboard'
    ),

    path(
        'analytics/',
        views.analytics_dashboard,
        name='analytics_dashboard'
    ),
]