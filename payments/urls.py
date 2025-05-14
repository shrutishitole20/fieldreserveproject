from django.urls import path
from . views import payment, booking_confirmation
urlpatterns = [
    path('payment/<int:booking_id>', payment, name='payment'),
    path('confirmation/<int:booking_id>/', booking_confirmation, name='booking_confirmation'),
    # path('payment/success/', views.payment_success, name='payment_success'),
    # path('payment/failure/', views.payment_failure, name='payment_failure'),
]
