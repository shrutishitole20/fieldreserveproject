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
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from booking import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('search-slots/', views.search_slots, name='search_slots'),
    path('book-slot/<int:slot_id>/', views.book_slot, name='book_slot'),
    path('booking-confirmation/<int:booking_id>/', views.booking_confirmation, name='booking_confirmation'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('my-bookings/', views.my_bookings, name='my_bookings'),
    path('location/', views.location_selector, name='location_selector'),
    path('activity/', views.activity_selector, name='activity_selector'),
    path('remove-search/<int:search_id>/', views.remove_search, name='remove_search'),
    path('api/nearby-grounds/', views.nearby_grounds_api, name='nearby_grounds_api'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


