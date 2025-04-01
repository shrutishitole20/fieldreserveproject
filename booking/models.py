from django.db import models
from django.contrib.auth.models import User

class ActivityType(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    icon = models.CharField(max_length=50, blank=True, null=True)  # For storing icon names

    def __str__(self):
        return self.name

class Location(models.Model):
    name = models.CharField(max_length=200)
    address = models.TextField()
    city = models.CharField(max_length=100)
    image = models.ImageField(upload_to='locations/', blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    is_featured = models.BooleanField(default=False)
    
    def __str__(self):
        return self.name

class Slot(models.Model):
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='slots')
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    capacity = models.IntegerField(default=1)
    activity_type = models.ForeignKey(ActivityType, on_delete=models.SET_NULL, null=True, related_name='slots')
    
    def __str__(self):
        return f"{self.location.name} - {self.date} {self.start_time}"

class Booking(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    field = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='bookings')  # Changed to field
    slot = models.ForeignKey(Slot, on_delete=models.CASCADE, related_name='bookings')
    participants = models.IntegerField(default=1)
    booking_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_status = models.CharField(max_length=20, default='unpaid')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    payment_id = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Booking {self.id} by {self.user.username}"

class Testimonial(models.Model):
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=100, blank=True, null=True)
    quote = models.TextField()
    rating = models.IntegerField(default=5)
    image = models.ImageField(upload_to='testimonials/', blank=True, null=True)
    
    def __str__(self):
        return f"Testimonial by {self.name}"
