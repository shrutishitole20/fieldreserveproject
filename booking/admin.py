from django.contrib import admin
from .models import ActivityType, Location, Field, Slot, Booking, SearchHistory, Testimonial

# Register your models here
admin.site.register(ActivityType)
admin.site.register(Location)
admin.site.register(Field)
admin.site.register(Slot)  # Changed from TimeSlot to Slot
admin.site.register(Booking)
admin.site.register(SearchHistory)
admin.site.register(Testimonial)