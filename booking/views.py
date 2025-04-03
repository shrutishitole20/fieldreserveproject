from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import ActivityType, Location, TimeSlot, Booking, Testimonial, SearchHistory  # Updated Slot to TimeSlot
from .forms import BookingForm, UserRegisterForm, UserLoginForm
from django.contrib.auth import login, authenticate, logout
import math

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
    
    # If lat and lng are provided, use current location
    if 'lat' in request.GET and 'lng' in request.GET:
        lat = request.GET.get('lat')
        lng = request.GET.get('lng')
        # Here you would use a geocoding service to get the location name
        # For demonstration, we'll use a placeholder
        location = "Current Location"
        
        # Save to search history if user is authenticated
        if request.user.is_authenticated:
            SearchHistory.objects.create(user=request.user, search_term=location)
    
    # Regular search flow
    elif location and request.user.is_authenticated:
        SearchHistory.objects.create(user=request.user, search_term=location)
    
    slots = TimeSlot.objects.all()  # Updated from Slot to TimeSlot
    
    if activity:
        slots = slots.filter(field__activity_type__name__icontains=activity)  # Updated to match model relationship
    if location:
        slots = slots.filter(field__location__address__icontains=location)  # Updated city to address
    if date:
        slots = slots.filter(date=date)
    
    context = {
        'slots': slots,
        'activity': activity,
        'location': location,
        'date': date,
    }
    return render(request, 'search_results.html', context)

def activity_selector(request):
    activity_types = ActivityType.objects.all()
    return render(request, 'activity_selector.html', {
        'activity_types': activity_types
    })

@login_required
def book_slot(request, slot_id):
    slot = get_object_or_404(TimeSlot, id=slot_id)  # Updated from Slot to TimeSlot
    
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
    bookings = Booking.objects.filter(user=request.user).order_by('-booking_time')  # Updated booking_date to booking_time
    return render(request, 'my_bookings.html', {'bookings': bookings})

def location_selector(request):
    recent_searches = []
    if request.user.is_authenticated:
        recent_searches = SearchHistory.objects.filter(user=request.user).order_by('-created_at')[:5]
    
    return render(request, 'location_selector.html', {
        'recent_searches': recent_searches
    })

@login_required
def remove_search(request, search_id):
    search = get_object_or_404(SearchHistory, id=search_id, user=request.user)
    search.delete()
    return redirect('location_selector')

def calculate_distance(lat1, lon1, lat2, lon2):
    # Haversine formula to calculate distance between two coordinates
    R = 6371  # Radius of Earth in kilometers
    dLat = math.radians(lat2 - lat1)
    dLon = math.radians(lon2 - lon1)
    a = math.sin(dLat/2) * math.sin(dLat/2) + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dLon/2) * math.sin(dLon/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    distance = R * c
    return round(distance, 2)  # Round to 2 decimal places

def nearby_grounds_api(request):
    """API endpoint to get nearby grounds based on latitude and longitude."""
    if 'lat' not in request.GET or 'lng' not in request.GET:
        return JsonResponse({'error': 'Latitude and longitude are required'}, status=400)
    
    try:
        user_lat = float(request.GET.get('lat'))
        user_lng = float(request.GET.get('lng'))
    except ValueError:
        return JsonResponse({'error': 'Invalid latitude or longitude'}, status=400)
    
    # Get all locations with coordinates
    locations = Location.objects.all()
    
    # Calculate distance and filter nearby locations
    nearby_grounds = []
    for location in locations:
        if location.latitude and location.longitude:
            distance = calculate_distance(user_lat, user_lng, float(location.latitude), float(location.longitude))
            
            # Only include locations within 20km
            if distance <= 20:
                grounds = []
                # Get all fields in this location
                for field in location.fields.all():  # Updated field_set to fields (matches related_name)
                    grounds.append({
                        'id': field.id,
                        'name': field.name,
                        'activity_type': field.activity_type.name,  # Updated to return name
                        'description': field.description,
                        'indoor': field.indoor,
                        'image_url': field.image.url if field.image else None,
                    })
                
                if grounds:  # Only include locations with fields
                    nearby_grounds.append({
                        'location_id': location.id,
                        'location_name': location.name,
                        'city': location.address,  # Updated city to address
                        'distance': distance,
                        'grounds': grounds
                    })
    
    # Sort by distance
    nearby_grounds.sort(key=lambda x: x['distance'])
    
    return JsonResponse({'grounds': nearby_grounds})