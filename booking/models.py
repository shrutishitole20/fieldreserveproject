from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.db.models import UniqueConstraint

class ActivityType(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        indexes = [
            models.Index(fields=['name']),
        ]

class Location(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=200)
    city = models.CharField(max_length=100, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    is_featured = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    class Meta:
        indexes = [
            models.Index(fields=['name', 'city']),
            models.Index(fields=['is_featured']),
        ]

class Field(models.Model):
    name = models.CharField(max_length=100)
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='fields')
    description = models.TextField(blank=True)
    activity_type = models.ForeignKey(ActivityType, on_delete=models.CASCADE, related_name='fields')
    indoor = models.BooleanField(default=False)
    image = models.ImageField(upload_to='fields/', null=True, blank=True)
    default_image = models.ImageField(upload_to='fields/', default='default_field.jpg')

    def __str__(self):
        return self.name

    def get_image(self):
        return self.image if self.image else self.default_image

    class Meta:
        indexes = [
            models.Index(fields=['name', 'location']),
        ]

class Slot(models.Model):
    field = models.ForeignKey(Field, on_delete=models.CASCADE, related_name='time_slots')
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    price = models.DecimalField(max_digits=8, decimal_places=2, validators=[MinValueValidator(0)])
    available = models.BooleanField(default=True)
    capacity = models.IntegerField(default=10, validators=[MinValueValidator(1)])
    available_slots = models.IntegerField(default=10, validators=[MinValueValidator(0)])

    def __str__(self):
        return f"{self.field.name} - {self.date} {self.start_time} to {self.end_time}"

    def clean(self):
        # Validate start_time and end_time
        if self.start_time >= self.end_time:
            raise ValidationError("Start time must be before end time.")
        # Validate available_slots
        if self.available_slots > self.capacity:
            raise ValidationError("Available slots cannot exceed capacity.")
        if self.available_slots < 0:
            raise ValidationError("Available slots cannot be negative.")

    def save(self, *args, **kwargs):
        # Ensure available_slots is initialized
        if self.available_slots is None:
            self.available_slots = self.capacity
        # Update available based on available_slots
        self.available = self.available_slots > 0
        super().save(*args, **kwargs)

    class Meta:
        indexes = [
            models.Index(fields=['field', 'date', 'start_time']),
            models.Index(fields=['available']),
        ]
        constraints = [
            UniqueConstraint(fields=['field', 'date', 'start_time', 'end_time'], name='unique_slot')
        ]

class Booking(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('CONFIRMED', 'Confirmed'),
        ('PAID', 'Paid'),
        ('CANCELLED', 'Cancelled'),
    )
    PAYMENT_STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    slot = models.ForeignKey(Slot, on_delete=models.CASCADE, related_name='bookings')
    booking_time = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='PENDING')
    participants = models.IntegerField(default=1, validators=[MinValueValidator(1)])

    def __str__(self):
        return f"{self.user.username} - {self.slot}"

    def clean(self):
        # Validate participants against slot capacity
        if self.participants > self.slot.capacity:
            raise ValidationError(f"Participants ({self.participants}) cannot exceed slot capacity ({self.slot.capacity}).")
        # Ensure slot is available
        if not self.slot.available:
            raise ValidationError("This slot is not available for booking.")

    class Meta:
        indexes = [
            models.Index(fields=['user', 'booking_time']),
            models.Index(fields=['slot', 'status']),
        ]
        constraints = [
            UniqueConstraint(fields=['user', 'slot'], name='unique_user_slot_booking')
        ]

class SearchHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='search_history')
    search_term = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.search_term}"

    class Meta:
        indexes = [
            models.Index(fields=['user', 'created_at']),
        ]

class Testimonial(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='testimonials')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    rating = models.IntegerField(
        default=5,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )

    def __str__(self):
        return f"Testimonial by {self.user.username} on {self.created_at}"

    class Meta:
        indexes = [
            models.Index(fields=['user', 'created_at']),
        ]