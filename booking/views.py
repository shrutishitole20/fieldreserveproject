from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import ActivityType, Location, Slot, Booking, Testimonial, SearchHistory, Field
from .forms import BookingForm, UserRegisterForm, UserLoginForm
from django.contrib.auth import login, authenticate, logout
import math
import random
import os

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
    
    if 'lat' in request.GET and 'lng' in request.GET:
        lat = request.GET.get('lat')
        lng = request.GET.get('lng')
        location = "Current Location"
        if request.user.is_authenticated:
            SearchHistory.objects.create(user=request.user, search_term=location)
    
    elif location and request.user.is_authenticated:
        SearchHistory.objects.create(user=request.user, search_term=location)
    
    slots = Slot.objects.all()
    
    if activity:
        slots = slots.filter(activity_type__name__icontains=activity)
    if location:
        slots = slots.filter(location__city__icontains=location)
    if date:
        slots = slots.filter(date=date)
    
    # Set default image for slots with missing field images
    for slot in slots:
        if not slot.field.image or not os.path.exists(slot.field.image.path):
            slot.field.default_image = '/static/images/placeholder.jpg'
    
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

def location_selector(request):
    """View to display the location selection page."""
    # Get recent searches if user is logged in
    recent_searches = []
    if request.user.is_authenticated:
        recent_searches = SearchHistory.objects.filter(user=request.user).order_by('-created_at')[:5]
    
    # Get list of states - in a real app this would be from database
    states = [
        {'id': 'kerala', 'name': 'Kerala', 'image': 'kerala.png'},
        {'id': 'tamil-nadu', 'name': 'Tamil Nadu', 'image': 'tamil_nadu.png'},
        {'id': 'karnataka', 'name': 'Karnataka', 'image': 'karnataka.png'},
        {'id': 'andhra-pradesh', 'name': 'Andhra Pradesh', 'image': 'andhra_pradesh.png'},
        {'id': 'telangana', 'name': 'Telangana', 'image': 'telangana.png'},
        {'id': 'maharashtra', 'name': 'Maharashtra', 'image': 'maharashtra.png'},
        {'id': 'goa', 'name': 'Goa', 'image': 'goa.png'},
        {'id': 'gujarat', 'name': 'Gujarat', 'image': 'gujarat.png'},
        {'id': 'madhya-pradesh', 'name': 'Madhya Pradesh', 'image': 'madhya_pradesh.png'},
        {'id': 'chhattisgarh', 'name': 'Chhattisgarh', 'image': 'chhattisgarh.png'},
        {'id': 'odisha', 'name': 'Odisha', 'image': 'odisha.png'},
        {'id': 'jharkhand', 'name': 'Jharkhand', 'image': 'jharkhand.png'},
        {'id': 'bihar', 'name': 'Bihar', 'image': 'bihar.png'},
        {'id': 'west-bengal', 'name': 'West Bengal', 'image': 'west_bengal.png'},
        {'id': 'uttar-pradesh', 'name': 'Uttar Pradesh', 'image': 'uttar_pradesh.png'},
        {'id': 'punjab', 'name': 'Punjab', 'image': 'punjab.png'},
    ]
    
    context = {
        'recent_searches': recent_searches,
        'states': states
    }
    
    return render(request, 'location_selector.html', context)
@login_required
def remove_search(request, search_id):
    search = get_object_or_404(SearchHistory, id=search_id, user=request.user)
    search.delete()
    return redirect('location_selector')

def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate the great circle distance between two points on earth (specified in decimal degrees)"""
    # Convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    # Radius of earth in kilometers is 6371
    km = 6371 * c
    return km


def nearby_grounds_api(request):
    """API endpoint to get nearby grounds based on latitude and longitude or location name."""
    # Check if we're searching by coordinates or by location name
    if 'lat' in request.GET and 'lng' in request.GET:
        try:
            user_lat = float(request.GET.get('lat'))
            user_lng = float(request.GET.get('lng'))
            
            # ... keep existing code (function to generate grounds near coordinates)
            grounds = generate_nearby_grounds(user_lat, user_lng)
            
            return JsonResponse({'grounds': grounds})
            
            
        except ValueError:
            return JsonResponse({'error': 'Invalid latitude or longitude'}, status=400)
    
    # Search by location name (e.g., "Pune" or state name)
    elif 'location' in request.GET:
        location = request.GET.get('location', '')
        
        # We'll modify this to handle different states
        state_grounds = {
            'kerala': [
                {
                    'location_id': 101,
                    'location_name': 'Kochi Municipal Stadium',
                    'city': 'Kochi',
                    'distance': 2.5,
                    'grounds': [
                        {
                            'id': 101,
                            'name': 'Kochi Municipal Stadium',
                            'description': 'Near Kaloor, Kochi',
                            'activity_type': 'football, cricket',
                            'indoor': False,
                            'image_url': '/static/images/grounds/Kochi Municipal Stadium.png'
                        }
                    ]
                },
                {
                    'location_id': 102,
                    'location_name': 'Jawaharlal Nehru Stadium',
                    'city': 'Kochi',
                    'distance': 3.8,
                    'grounds': [
                        {
                            'id': 102,
                            'name': 'Jawaharlal Nehru Stadium',
                            'description': 'Kaloor, Kochi',
                            'activity_type': 'football, cricket, athletics',
                            'indoor': False,
                            'image_url': '/static/images/grounds/Jawaharlal Nehru Stadium.png'
                        }
                    ]
                }
            ],
            'tamil nadu': [
                {
                    'location_id': 201,
                    'location_name': 'MA Chidambaram Stadium',
                    'city': 'Chennai',
                    'distance': 4.2,
                    'grounds': [
                        {
                            'id': 201,
                            'name': 'MA Chidambaram Stadium',
                            'description': 'Chepauk, Chennai',
                            'activity_type': 'cricket',
                            'indoor': False,
                            'image_url': '/static/images/grounds/MA Chidambaram Stadium.png'
                        }
                    ]
                },
                {
                    'location_id': 202,
                    'location_name': 'Jawaharlal Nehru Stadium',
                    'city': 'Chennai',
                    'distance': 5.1,
                    'grounds': [
                        {
                            'id': 202,
                            'name': 'Jawaharlal Nehru Stadium',
                            'description': 'Periamet, Chennai',
                            'activity_type': 'football, athletics',
                            'indoor': False,
                            'image_url': '/static/images/grounds/Jawaharlal Nehru Stadium(channai).png'
                        }
                    ]
                }
            ],
            'maharashtra': [
                {
                    'location_id': 1,
                    'location_name': 'Force Playing Fields',
                    'city': 'Pune',
                    'distance': 4.9,
                    'grounds': [
                        {
                            'id': 1,
                            'name': 'Force Playing Fields',
                            'description': 'Gokhale Path, Near Om Supermarket, Model Colony, Pune',
                            'activity_type': 'football, cricket',
                            'indoor': False,
                            'image_url': '/static/images/grounds/Force Playing Fields.png'
                        }
                    ]
                },
                {
                    'location_id': 2,
                    'location_name': '4 LIONS ACADEMY',
                    'city': 'Pune',
                    'distance': 5.3,
                    'grounds': [
                        {
                            'id': 2,
                            'name': '4 LIONS ACADEMY',
                            'description': 'Lane Number 3, Vinayak Nagar, Pimple Nilakh, Pune',
                            'activity_type': 'football, cricket',
                            'indoor': False,
                            'image_url': '/static/images/grounds/4 LIONS ACADEMY.png'
                        }
                    ]
                }
            ],
            'karnataka': [
                {
                    'location_id': 301,
                    'location_name': 'M. Chinnaswamy Stadium',
                    'city': 'Bangalore',
                    'distance': 3.2,
                    'grounds': [
                        {
                            'id': 301,
                            'name': 'M. Chinnaswamy Stadium',
                            'description': 'MG Road, Bangalore',
                            'activity_type': 'cricket',
                            'indoor': False,
                            'image_url': '/static/images/grounds/M. Chinnaswamy Stadium.png'
                        }
                    ]
                },
                {
                    'location_id': 302,
                    'location_name': 'Sree Kanteerava Stadium',
                    'city': 'Bangalore',
                    'distance': 4.5,
                    'grounds': [
                        {
                            'id': 302,
                            'name': 'Sree Kanteerava Stadium',
                            'description': 'Kasturba Road, Bangalore',
                            'activity_type': 'football, athletics',
                            'indoor': False,
                            'image_url': '/static/images/grounds/Sree Kanteerava Stadium.png'
                        }
                    ]
                }
            ]
        }
        
        # Default to Pune data if the location is not in our state mapping or location is 'pune'
        grounds = []
        if location.lower() == 'pune':
            grounds = state_grounds.get('maharashtra', [])
        else:
            # Check if location matches any state name
            for state_name, state_data in state_grounds.items():
                if location.lower() == state_name.lower():
                    grounds = state_data
                    break
                
        # Save search history
        if request.user.is_authenticated:
            SearchHistory.objects.create(user=request.user, search_term=location)
            
        return JsonResponse({'grounds': grounds})
                
    else:
        return JsonResponse({'error': 'Either location or coordinates (lat/lng) are required'}, status=400)

@login_required
def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    
    booking.delete()
    messages.success(request, 'Your booking has been cancelled successfully.')
    return redirect('my_bookings')
def generate_nearby_grounds(lat, lng):
    """Generate sample grounds near the provided coordinates."""
    # These are mock grounds for demonstration
    # In a real application, you would query your database
    random_stadiums = [
        {
            'location_id': 901,
            'location_name': 'Local Community Ground',
            'city': 'Near your location',
            'distance': round(random.uniform(0.5, 3.0), 1),
            'grounds': [
                {
                    'id': 901,
                    'name': 'Local Community Ground',
                    'description': 'A community sports ground near your current location',
                    'activity_type': 'football, cricket',
                    'indoor': False,
                    'image_url': '/static/images/grounds/force_playing_fields.jpg'
                }
            ]
        },
        {
            'location_id': 902,
            'location_name': 'City Sports Complex',
            'city': 'Near your location',
            'distance': round(random.uniform(1.0, 5.0), 1),
            'grounds': [
                {
                    'id': 902,
                    'name': 'City Sports Complex',
                    'description': 'Multi-sport facility with modern amenities',
                    'activity_type': 'football, cricket, basketball, tennis',
                    'indoor': True,
                    'image_url': '/static/images/grounds/4lions_academy.jpg'
                }
            ]
        },
        {
            'location_id': 903,
            'location_name': 'Neighborhood Stadium',
            'city': 'Near your location',
            'distance': round(random.uniform(2.0, 7.0), 1),
            'grounds': [
                {
                    'id': 903,
                    'name': 'Neighborhood Stadium',
                    'description': 'Open field perfect for weekend sports',
                    'activity_type': 'football, cricket',
                    'indoor': False,
                    'image_url': '/static/images/grounds/nehru_stadium_kochi.jpg'
                }
            ]
        }
    ]
    
    # Sort by distance
    random_stadiums.sort(key=lambda x: x['distance'])
    
    return random_stadiums
def show_nearby_grounds(request):
    """View to display grounds based on selected location"""
    location = request.GET.get('location', '')
    lat = request.GET.get('lat')
    lng = request.GET.get('lng')
    
    context = {
        'location': location,
        'lat': lat,
        'lng': lng,
    }
    return render(request, 'nearby_grounds.html', context)
