import razorpay
from django.shortcuts import render, get_object_or_404
from django.conf import settings
from booking.models import Booking

# Initialize Razorpay client
client = razorpay.Client(auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_API_SECRET))

def payment(request, booking_id):
    # Fetch booking for the authenticated user
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)

    # Calculate amount from booking (convert to paise for Razorpay)
    amount = int(booking.slot.price * 100)  # e.g., Rs.500 -> 50000 paise
    currency = 'INR'
    receipt = f'booking_{booking_id}'

    # Create Razorpay order
    try:
        order = client.order.create({
            'amount': amount,
            'currency': currency,
            'receipt': receipt,
            'payment_capture': 1  # Auto-capture payment
        })
        order_id = order['id']
        
        
    except Exception as e:
        # Handle Razorpay order creation failure
        return render(request, 'payments/payment.html', {
            'booking': booking,
            'error': f'Failed to create order: {str(e)}'
        })

    # Context for template
    context = {
        'booking': booking,
        'order_id': order_id,
        'amount': amount,
        'currency': currency,
        'razorpay_key': settings.RAZORPAY_API_KEY,
    }

    return render(request, 'payments/payment.html', context)