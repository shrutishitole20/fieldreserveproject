"""
URL configuration for fieldreserve project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from booking import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('booking.urls')),
    path('', views.index, name='index'),
    path('search-slots/', views.search_slots, name='search_slots'),
    path('book-slot/<int:slot_id>/', views.book_slot, name='book_slot'),
    path('book-ground/<int:ground_id>/', views.book_ground, name='book_ground'),
    path('booking-success/', views.booking_success, name='booking_success'),
    path('booking-confirmation/<int:booking_id>/', views.booking_confirmation, name='booking_confirmation'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('my-bookings/', views.my_bookings, name='my_bookings'),
    path('location/', views.location_selector, name='location_selector'),
    path('activity/', views.activity_selector, name='activity_selector'),
    path('remove-search/<int:search_id>/', views.remove_search, name='remove_search'),
    path('api/nearby-grounds/', views.nearby_grounds_api, name='nearby_grounds_api'),
    path('cancel-booking/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),
    path('nearby-grounds/', views.show_nearby_grounds, name='show_nearby_grounds'),
    path('direct-book-ground/<int:ground_id>/', views.direct_book_ground, name='direct_book_ground'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])\
  + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


