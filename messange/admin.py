from django.contrib import admin

# Register your models here.
from .models import SMSMessage

@admin.register(SMSMessage)
class SMSMessageAdmin(admin.ModelAdmin):
    list_display = ['message_id', 'receiver', 'sender', 'status', 'channel', 'cost', 'sent_at']
    search_fields = ['receiver', 'sender', 'message_id']
    list_filter = ['status', 'channel', 'sent_at']
    ordering = ['-sent_at']
    readonly_fields = ['message_id', 'receiver', 'sender', 'message', 'status', 'channel', 'cost', 'sent_at']

    def has_add_permission(self, request):
        # Prevent manual additions from admin
        return False