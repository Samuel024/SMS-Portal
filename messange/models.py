from django.db import models

# Create your models here.
# models.py

from django.utils import timezone

class SMSMessage(models.Model):
    STATUS_CHOICES = (
        ('sent', 'Message Sent'),
        ('delivered', 'Delivered'),
        ('failed', 'Failed'),
        ('dnd', 'DND Active'),
        ('expired', 'Expired'),
        ('rejected', 'Rejected'),
    )

    message_id = models.CharField(max_length=100, unique=True)
    message_request_id = models.CharField(max_length=100, blank=True, null=True)
    receiver = models.CharField(max_length=20)
    sender = models.CharField(max_length=30)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    channel = models.CharField(max_length=20)
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    sent_at = models.DateTimeField()
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.message_id} - {self.get_status_display()}"