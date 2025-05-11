from django.urls import path
from . views import payment
urlpatterns = [
    path('payment/', payment, name='payment'),
    # path('payment/success/', views.payment_success, name='payment_success'),
    # path('payment/failure/', views.payment_failure, name='payment_failure'),
]
