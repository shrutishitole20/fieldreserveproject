from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('search/', views.search_slots, name='search_slots'),
    path('book/<int:slot_id>/', views.book_slot, name='book_slot'),
    path('confirmation/<int:booking_id>/', views.booking_confirmation, name='booking_confirmation'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('my-bookings/', views.my_bookings, name='my_bookings'),
    # New location search history URLs
    path('location/', views.location_selector, name='location_selector'),
    path('location/remove/<int:search_id>/', views.remove_search, name='remove_search'),
]