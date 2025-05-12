from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import ActivityType, Location, Slot, Booking, Testimonial, SearchHistory, Field
from .forms import BookingForm, UserRegisterForm, UserLoginForm
from django.contrib.auth import login, authenticate, logout
from datetime import datetime
import math
import random
import os
from django.core.mail import send_mail

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

    # Start with all available slots
    slots = Slot.objects.all()

    # Filter by location
    if location:
        slots = slots.filter(field__location__name__icontains=location)

    # Filter by activity
    if activity:
        slots = slots.filter(field__activity_type__name__icontains=activity)

    # Filter by date
    if date:
        try:
            slots = slots.filter(date=date)
        except ValueError:
            messages.warning(request, "Invalid date format. Please use YYYY-MM-DD.")

    # Check if slots exist
    if not slots.exists():
        messages.warning(
            request,
            "We couldn't find any available slots matching your search criteria. "
            "Please try different search parameters or check back later.<br>"
            "Need help? Contact our support team."
        )
        return render(request, 'search_results.html', {
            'slots': [],
            'activity': activity,
            'location': location,
            'date': date,
        })

    # Pass found slots to the template
    return render(request, 'search_results.html', {
        'slots': slots,
        'activity': activity,
        'location': location,
        'date': date,
    })

def activity_selector(request):
    activity_types = ActivityType.objects.all()
    return render(request, 'activity_selector.html', {
        'activity_types': activity_types
    })

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Authenticate the user
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # If the user is authenticated, log them in
            login(request, user)
            messages.success(request, 'Login successful!')
            return redirect('home')  # Redirect to a success page or home page
        else:
            # If authentication fails, show an error message
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'booking/login.html')
@login_required
def book_slot(request, slot_id):
    slot = get_object_or_404(Slot, id=slot_id)
    
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.slot = slot
            booking.status = 'CONFIRMED'
            booking.save()
            messages.success(request, 'Booking successful!')

            # Send email notification to superuser
            try:
                send_mail(
                    'New Booking Notification',
                    f'User  {request.user.username} has booked a slot on {slot.date}.',
                    'your-email@example.com',  # Replace with your sender email
                    ['Shrutishitole2030@gmail.com'],  # Replace with the superuser's email
                    fail_silently=False,
                )
            except Exception as e:
                # Log the error or provide feedback to the user
                messages.error(request, f"Booking successful, but failed to send email notification: {str(e)}")

            return redirect('payment', booking_id=booking.id)
    else:
        form = BookingForm(initial={'participants': 1})
    
    context = {
        'slot': slot,
        'form': form,
    }
    return render(request, 'book_slot.html', context)


@login_required
def book_ground(request, ground_id):
    """View to book a ground directly."""
    try:
        # Get the ground by ID
        ground = get_object_or_404(Field, id=ground_id)
        
        if request.method == 'POST':
            # Process the booking
            activity = request.POST.get('activity')
            date = request.POST.get('date')
            time_slot = request.POST.get('time_slot')
            players = request.POST.get('players')
            special_requests = request.POST.get('special_requests', '')
            
            # Validate the input
            if not all([activity, date, time_slot, players]):
                messages.error(request, "Please fill all required fields")
                return render(request, 'book_ground.html', {
                    'ground': ground,
                    'today': datetime.now().date()
                })
            
            # Parse the time slot to get start and end times
            start_time_str, end_time_str = time_slot.split(' - ')
            
            # Convert strings to time objects
            start_time = datetime.strptime(start_time_str, '%H:%M').time()
            end_time = datetime.strptime(end_time_str, '%H:%M').time()
            booking_date = datetime.strptime(date, '%Y-%m-%d').date()
            
            # Create or find a time slot
            slot, created = Slot.objects.get_or_create(
                field=ground,
                date=booking_date,
                start_time=start_time,
                end_time=end_time,
                defaults={'price': 500.00, 'available': True}
            )
            
            if not slot.available:
                messages.error(request, "Sorry, this slot is no longer available")
                return render(request, 'book_ground.html', {
                    'ground': ground,
                    'today': datetime.now().date()
                })
            
            # Create the booking
            booking = Booking.objects.create(
                user=request.user,
                slot=slot,
                status='confirmed',
                payment_status='pending'
            )
            
            # Mark the slot as unavailable
            slot.available = False
            slot.save()
            
            # Success message and redirect
            messages.success(request, f"Successfully booked {ground.name} for {activity} on {date} at {time_slot}")
            
            # Redirect to booking confirmation page with the booking id
            return redirect('booking_confirmation', booking_id=booking.id)
        
        # GET request - show the booking form
        return render(request, 'book_ground.html', {
            'ground': ground,
            'today': datetime.now().date()
        })
            
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('index')

@login_required
def booking_success(request):
    """View to show booking success page."""
    return render(request, 'booking_success.html')

@login_required
def booking_confirmation(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    booking.payment_status = 'COMPLETED'
    booking.status = 'PAID'
    booking.save()  # Save changes to the database
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
    """View to display the user's bookings."""
    bookings = Booking.objects.filter(user=request.user).order_by('-booking_time')
    
    # Process the bookings to make them match the template expectations
    processed_bookings = []
    for booking in bookings:
        processed_booking = {
            'id': booking.id,
            'field': {
                'name': booking.slot.field.name,
                'location': booking.slot.field.location,
                'image': booking.slot.field.image
            },
            'date': booking.slot.date,
            'start_time': booking.slot.start_time,
            'end_time': booking.slot.end_time,
            'price': booking.slot.price,
            'slot': booking.slot,
            'status': booking.status
        }
        processed_bookings.append(processed_booking)
    
    return render(request, 'my_bookings.html', {'bookings': processed_bookings})
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from booking.models import SearchHistory

def location_selector(request):
    """View to display the location selection page with Indian states."""
    # Get recent searches if user is authenticated
    recent_searches = []
    if request.user.is_authenticated:
        recent_searches = SearchHistory.objects.filter(user=request.user).order_by('-created_at')[:5]

    # List of Indian states
    indian_states = [
        'Andhra Pradesh', 'Arunachal Pradesh', 'Assam', 'Bihar', 'Chhattisgarh',
        'Goa', 'Gujarat', 'Haryana', 'Himachal Pradesh', 'Jharkhand', 'Karnataka',
        'Kerala', 'Madhya Pradesh', 'Maharashtra', 'Manipur', 'Meghalaya', 'Mizoram',
        'Nagaland', 'Odisha', 'Punjab', 'Rajasthan', 'Sikkim', 'Tamil Nadu', 'Telangana',
        'Tripura', 'Uttar Pradesh', 'Uttarakhand', 'West Bengal',
        'Andaman and Nicobar Islands', 'Chandigarh', 'Dadra and Nagar Haveli and Daman and Diu',
        'Delhi', 'Jammu and Kashmir', 'Ladakh', 'Lakshadweep', 'Puducherry'
    ]

    # Create states list with id and image
    states = [
        {
            'id': state.lower().replace(' ', '-'),  # e.g., 'Tamil Nadu' -> 'tamil-nadu'
            'name': state,
            'image': f"{state.lower().replace(' ', '-')}.png"  # e.g., 'tamil-nadu.png'
        } for state in indian_states
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
    if 'lat' in request.GET and 'lng' in request.GET:
        try:
            user_lat = float(request.GET.get('lat'))
            user_lng = float(request.GET.get('lng'))
            # Fetch nearby grounds from the database
            locations = Location.objects.all()
            grounds = []
            for location in locations:
                if location.latitude and location.longitude:
                    distance = calculate_distance(user_lat, user_lng, location.latitude, location.longitude)
                    if distance <= 10:  # Filter grounds within 10 km
                        grounds.append({
                            'id': location.id,
                            'name': location.name,
                            'city': location.city,
                            'distance': round(distance, 2),
                            'grounds': [
                                
                                {
                                    'id': field.id,
                                    'name': field.name,
                                    'description': field.description,
                                    'activity_type': field.activity_type.name,
                                    'indoor': field.indoor,
                                    'image_url': field.image.url if field.image else '/static/images/placeholder.jpg'
                                } for field in location.fields.all()
                            ]
                        })
            return JsonResponse({'grounds': grounds})
        except ValueError:
            return JsonResponse({'error': 'Invalid latitude or longitude'}, status=400)
    elif 'location' in request.GET:
        location = request.GET.get('location', '')
        locations = Location.objects.filter(name__icontains=location)
        grounds = [
            {
                'id': loc.id,
                'name': loc.name,
                'city': loc.city,
                'grounds': [
                    {
                        'id': field.id,
                        'name': field.name,
                        'description': field.description,
                        'activity_type': field.activity_type.name,
                        'indoor': field.indoor,
                        'image_url': field.image.url if field.image else '/static/images/placeholder.jpg'
                    } for field in loc.fields.all()
                ]
            } for loc in locations
        ]
        return JsonResponse({'grounds': grounds})
    else:
        return JsonResponse({'error': 'Either location or coordinates (lat/lng) are required'}, status=400)


def generate_nearby_grounds(lat, lng):
    """Generate sample grounds near the provided coordinates."""
    return [
        {
            'location_id': 901,
            'name': 'Local Community Ground',
            'city': 'Your City',
            'distance': 2.5,
            'grounds': [
                {
                    'id': 1,  # Ensure this ID is valid
                    'name': 'Community Ground A',
                    'description': 'A great place for sports.',
                    'activity_type': 'football, cricket',
                    'image_url': '/static/images/grounds/community_ground_a.jpg'
                }
            ]
        },
        {
            'location_id': 902,
            'name': 'City Sports Complex',
            'city': 'Your City',
            'distance': 4.0,
            'grounds': [
                {
                    'id': 2,  # Ensure this ID is valid
                    'name': 'Sports Complex B',
                    'description': 'Modern sports facilities.',
                    'activity_type': 'basketball, tennis',
                    'image_url': '/static/images/grounds/sports_complex_b.jpg'
                }
            ]
        }
    ]

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

@login_required
def direct_book_ground(request, ground_id):
    """View to handle direct booking from nearby grounds page."""
    ground = get_object_or_404(Field, id=ground_id)
    if request.method == 'POST':
        # Validate the presence of required fields
        date = request.POST.get('date')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')

        if not all([date, start_time, end_time]):
            messages.error(request, "Please fill in all required fields.")
            return render(request, 'book_ground.html', {'ground': ground})

        try:
            # Parse the date and time fields
            booking_date = datetime.strptime(date, '%Y-%m-%d').date()
            start_time_obj = datetime.strptime(start_time, '%H:%M').time()
            end_time_obj = datetime.strptime(end_time, '%H:%M').time()

            # Create or find a time slot
            slot, created = Slot.objects.get_or_create(
                field=ground,
                date=booking_date,
                start_time=start_time_obj,
                end_time=end_time_obj,
                defaults={'price': 500.00, 'available': True}
            )

            if not slot.available:
                messages.error(request, "Sorry, this slot is no longer available.")
                return render(request, 'book_ground.html', {'ground': ground})

            # Create the booking
            booking = Booking.objects.create(
                user=request.user,
                slot=slot,
                status='confirmed',
                payment_status='pending'
            )

            # Mark the slot as unavailable
            slot.available = False
            slot.save()

            # Success message and redirect
            messages.success(request, f"Successfully booked {ground.name} on {date} from {start_time} to {end_time}.")
            return redirect('payment', booking_id=booking.id)

        except ValueError:
            messages.error(request, "Invalid date or time format.")
            return render(request, 'book_ground.html', {'ground': ground})

    else:
        form = BookingForm()
    return render(request, 'book_ground.html', {'ground': ground, 'form': form})

def contact_support(request):
    """View to display the contact support page."""
    return render(request, 'contact_support.html')
def booking_list(request):
    # Get bookings for the logged-in user
    user_bookings = Booking.objects.filter(user=request.user).order_by('-date')

    context = {
        'bookings': user_bookings
    }
    return render(request, 'booking_list.html', context)


