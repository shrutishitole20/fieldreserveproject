from django.urls import path
from . import views
from .views import user_login

urlpatterns = [
    path('', views.index, name='index'),
    path('search/', views.search_slots, name='search_slots'),
    path('book/<int:slot_id>/', views.book_slot, name='book_slot'),
    
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('login/', user_login, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('my-bookings/', views.my_bookings, name='my_bookings'),
    path('location/', views.location_selector, name='location_selector'),
    path('location/remove/<int:search_id>/', views.remove_search, name='remove_search'),

    path('bookings/', views.booking_list, name='booking_list'),
    path('api/nearby-grounds/', views.nearby_grounds_api, name='nearby_grounds_api'),
    path('show-nearby-grounds/', views.show_nearby_grounds, name='show_nearby_grounds'),
    path('activity/', views.activity_selector, name='activity_selector'),
    path('remove-search/<int:search_id>/', views.remove_search, name='remove_search'),
    path('nearby-grounds/', views.show_nearby_grounds, name='show_nearby_grounds'),
    path('direct-book-ground/<int:ground_id>/', views.direct_book_ground, name='direct_book_ground'),
    
]