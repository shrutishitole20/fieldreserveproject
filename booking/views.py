from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import ActivityType, Location, Slot, Booking, Testimonial
from .forms import BookingForm, UserRegisterForm, UserLoginForm
from django.contrib.auth import login, authenticate, logout

def index(request):
    featured_locations = Location.objects.filter(is_featured=True)[:2]
    testimonials = Testimonial.objects.all()[:6]
    activity_types = ActivityType.objects.all()
    
    context = {
        'featured_locations': featured_locations,
        'testimonials': testimonials,
        'activity_types': activity_types,
    }
    return render(request, 'index.html', context)

def search_slots(request):
    activity = request.GET.get('activity', '')
    location = request.GET.get('location', '')
    date = request.GET.get('date', '')
    
    slots = Slot.objects.all()
    
    if activity:
        slots = slots.filter(activity_type__name__icontains=activity)
    if location:
        slots = slots.filter(location__city__icontains=location)
    if date:
        slots = slots.filter(date=date)
    
    context = {
        'slots': slots,
        'activity': activity,
        'location': location,
        'date': date,
    }
    return render(request, 'search_results.html', context)

@login_required
def book_slot(request, slot_id):
    slot = get_object_or_404(Slot, id=slot_id)
    
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.slot = slot
            booking.save()
            messages.success(request, 'Booking successful!')
            return redirect('booking_confirmation', booking_id=booking.id)
    else:
        form = BookingForm(initial={'participants': 1})
    
    context = {
        'slot': slot,
        'form': form,
    }
    return render(request, 'book_slot.html', context)

@login_required
def booking_confirmation(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    return render(request, 'booking_confirmation.html', {'booking': booking})

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('index')
    else:
        form = UserRegisterForm()
    return render(request, 'register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, 'Login successful!')
                return redirect('index')
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = UserLoginForm()
    return render(request, 'login.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'Logged out successfully!')
    return redirect('index')

@login_required
def my_bookings(request):
    bookings = Booking.objects.filter(user=request.user).order_by('-booking_date')
    return render(request, 'my_bookings.html', {'bookings': bookings})