# booking/migrations/0011_clean_activitytype_duplicates.py
from django.db import migrations
from django.db.models import Count

def merge_duplicate_activity_types(apps, schema_editor):
    ActivityType = apps.get_model('booking', 'ActivityType')
    Field = apps.get_model('booking', 'Field')

    # Find duplicates
    duplicates = ActivityType.objects.values('name').annotate(count=Count('id')).filter(count__gt=1)
    
    for dup in duplicates:
        name = dup['name']
        # Get all ActivityType objects with this name
        activity_types = ActivityType.objects.filter(name=name).order_by('id')
        # Keep the first one (lowest ID)
        keep = activity_types.first()
        # Delete the rest, but update related Fields first
        for at in activity_types[1:]:
            # Update Fields to point to the kept ActivityType
            Field.objects.filter(activity_type=at).update(activity_type=keep)
            at.delete()

class Migration(migrations.Migration):
    dependencies = [
        ('booking', '0011_remove_booking_booking_date_alter_activitytype_name_and_more'),  # Replace with the actual previous migration
    ]

    operations = [
        migrations.RunPython(merge_duplicate_activity_types, reverse_code=migrations.RunPython.noop),
    ]