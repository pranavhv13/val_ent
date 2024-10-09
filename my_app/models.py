from django.db import models
from django.db.models import JSONField

class Event(models.Model):
    id = models.IntegerField(primary_key=True)
    title = models.CharField(max_length=100)
    description = models.TextField()
    date = models.DateTimeField()
    isDone = models.BooleanField(default=False)  # True for completed, False for upcoming
    location = models.CharField(max_length=50)
    banner = models.ImageField(upload_to='banners/', blank=True, null=True)
    poster = models.ImageField(upload_to='posters/', blank=True, null=True)
    more_info = models.TextField(blank=True, null=True)
    form_id = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.title

class FormConfig(models.Model):
    id = models.IntegerField(primary_key=True)
    title = models.CharField(max_length=20, blank=True, null=True)
    fields = JSONField()  # Store form fields as JSON data

    def __str__(self):
        return self.title


class Ticket(models.Model):
    event_id = models.ForeignKey(Event, on_delete=models.DO_NOTHING, null=True)
    ticket_id = models.CharField(max_length=20, unique=True)
    enc_tk_id = models.CharField(max_length=100, unique=True, null=True, blank=True)
    ticket_data = models.JSONField()  # This will store the dynamic form data as JSON.
    uploaded_file = models.FileField(upload_to='uploads/', null=True, blank=True)  # To store uploaded files.

    def __str__(self):
        return f"{self.ticket_id}"