from django.db import models
from django.contrib.auth.models import User

class ActivityType(models.Model):
    name = models.CharField(max_length=50)
    
    def __str__(self):
        return self.name

class Location(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=200)
    city = models.CharField(max_length=100, default='') 
    latitude = models.FloatField(null=True, blank=True) 
    longitude = models.FloatField(null=True, blank=True)  
    is_featured = models.BooleanField(default=False)
    
    def __str__(self):
        return self.name

class Field(models.Model):
    name = models.CharField(max_length=100)
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='fields')
    description = models.TextField()
    activity_type = models.ForeignKey(ActivityType, on_delete=models.CASCADE, related_name='fields')
    indoor = models.BooleanField(default=False)
    image = models.ImageField(upload_to='fields/', blank=True, null=True)
        
    def __str__(self):
        return self.name

class Slot(models.Model): 
    field = models.ForeignKey(Field, on_delete=models.CASCADE, related_name='time_slots')
    activity_type = models.ForeignKey(ActivityType, on_delete=models.CASCADE) 
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    available = models.BooleanField(default=True)
    capacity = models.IntegerField(default=10) 
    available_slots = models.IntegerField(null=True, blank=True) 
        
    def __str__(self):
        return f"{self.field.name} - {self.date} {self.start_time} to {self.end_time}"
        
    def save(self, *args, **kwargs):
        if self.available_slots is None:
            self.available_slots = self.capacity
        super().save(*args, **kwargs)

class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    slot = models.ForeignKey(Slot, on_delete=models.CASCADE)  
    booking_time = models.DateTimeField(auto_now_add=True)
    booking_date = models.DateTimeField(auto_now_add=True)  
    status = models.CharField(max_length=20, default='confirmed')
    payment_status = models.CharField(max_length=20, default='pending')
    participants = models.IntegerField(default=1, help_text="Number of participants")
        
    def __str__(self):
        return f"{self.user.username} - {self.slot}"

class SearchHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    search_term = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
        
    def __str__(self):
        return f"{self.user.username} - {self.search_term}"

class Testimonial(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    rating = models.IntegerField(default=5) 
    
    def __str__(self):
        return f"Testimonial by {self.user.username} on {self.created_at}"