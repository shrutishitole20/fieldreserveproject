import razorpay
from fieldreserve.settings import RAZORPAY_API_KEY, RAZORPAY_API_SECRET
client = razorpay.Client(auth=(RAZORPAY_API_KEY, RAZORPAY_API_SECRET))
from django.shortcuts import render, redirect

def payment(request):
    # if request.method == 'POST':
        amount = 50000  # Amount in paise (500.00 INR)
        currency = 'INR'
        receipt = 'receipt#1'
        # notes = {'note_key': 'note_value'}

        # Create a Razorpay order
        order = client.order.create(dict(amount=amount, currency=currency, receipt=receipt, payment_capture=1) )
        order_id = order['id']
        context = {
            'order_id': order_id,
            'amount': amount,
            'currency': currency,
            'razorpay_key': RAZORPAY_API_KEY,
        }
        return render(request, 'payments/payment.html', context)
    # else:
    #     return render(request, 'payments/payment.html')