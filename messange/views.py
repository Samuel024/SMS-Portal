import requests
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render
from django.views import View
import re

class SendSMSView(View):
    def get(self, request, *args, **kwargs):
        return render(request, "message.html")

    def post(self, request, *args, **kwargs):
        api_key = settings.TERMII_MESSAGES_API_KEY
        base_url = "https://v3.api.termii.com/api/sms/send/ "

        to = request.POST.get("to")
        sender = request.POST.get("from")
        sms = request.POST.get("sms", "sms")
        sms_type = request.POST.get("type", "plain")

        payload = {
            "api_key": api_key,
            "to": to,
            "from": sender,
            "sms": sms,
            "type": sms_type,
            "channel": "dnd"
        }

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_key}'
        }

        try:
            # Make sure base URL is trimmed properly
            response = requests.post(base_url.strip(), json=payload, headers=headers)
            response.raise_for_status()
            response_data = response.json()

            print("Response from Termii:", response_data)

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'success',
                    'message': response_data.get('message', 'Message sent successfully'),
                    'data': response_data
                })
            else:
                return render(request, "message.html", {
                    'response': response_data.get('message', 'Message sent')
                })

        except requests.exceptions.RequestException as e:
            print("Error sending SMS:", str(e))

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'error',
                    'message': 'Failed to send message'
                }, status=502)
            else:
                return render(request, "message.html", {
                    'error': 'Failed to send message'
                })

class SendSMSBULKView(View):
    def get(self, request, *args, **kwargs):
        return render(request, "message.html")

    def post(self, request, *args, **kwargs):
        api_key = settings.TERMII_MESSAGES_API_KEY
        base_url = "https://v3.api.termii.com/api/sms/send/bulk/ "

        to_raw = request.POST.get("to", "")
        sender = request.POST.get("from")
        sms = request.POST.get("sms", "sms")
        sms_type = request.POST.get("type", "plain")

        # Step 1: Extract all possible 13-digit Nigerian numbers from raw input
        cleaned_numbers = []

        # Remove all non-digit characters
        digits_only = re.sub(r'\D', '', to_raw)

        # Try to find 13-digit blocks starting with 234
        for i in range(0, len(digits_only)):
            if i + 13 > len(digits_only):
                break
            chunk = digits_only[i:i+13]
            if chunk.startswith("234"):
                cleaned_numbers.append(chunk)

        # Step 2: Also try splitting by commas first for manually separated numbers
        comma_split = [num.strip() for num in to_raw.split(",") if num.strip()]
        for number in comma_split:
            digits = re.sub(r'\D', '', number)
            if len(digits) == 13 and digits.startswith("234"):
                if digits not in cleaned_numbers:
                    cleaned_numbers.append(digits)

        # If no valid numbers found
        if not cleaned_numbers:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'error',
                    'message': 'No valid Nigerian phone numbers found. Ensure numbers are 13 digits and start with 234.'
                }, status=400)
            else:
                return render(request, "message.html", {
                    "error": "No valid Nigerian phone numbers found. Ensure numbers are 13 digits and start with 234."
                })

        payload = {
            "api_key": api_key,
            "to": cleaned_numbers,
            "from": sender,
            "sms": sms,
            "type": sms_type,
            "channel": "dnd"
        }

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_key}'
        }

        try:
            response = requests.post(base_url.strip(), json=payload, headers=headers)
            response.raise_for_status()
            response_data = response.json()

            print("Response from Termii:", response_data)

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'success',
                    'message': 'Bulk message sent successfully',
                    'data': response_data
                })
            else:
                return render(request, "message.html", {
                    'response': response_data.get('message', 'Bulk message sent')
                })

        except requests.exceptions.RequestException as e:
            error_msg = str(e)
            print("Error sending SMS:", error_msg)

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'error',
                    'message': 'Failed to send bulk message'
                }, status=502)
            else:
                return render(request, "message.html", {
                    'error': error_msg
                })
        
from django.http import JsonResponse
traceback = __import__('traceback')

class BalanceView(View):
    def get(self, request, *args, **kwargs):
        api_key = settings.TERMII_MESSAGES_API_KEY
        base_url = f"https://v3.api.termii.com/api/get-balance?api_key={api_key}"

        print(f"Attempting to fetch balance with API key: {api_key[:5]}...")  # Debug

        try:
            response = requests.get(
                base_url,
                params={'api_key': api_key},
                headers={'Accept': 'application/json'},
                timeout=10
            )
            
            print(f"Response status: {response.status_code}")  # Debug
            print(f"Response headers: {response.headers}")  # Debug
            print(f"Raw response: {response.text}")  # Debug

            if response.status_code != 200:
                return JsonResponse(
                    {'error': f'API returned {response.status_code}', 'content': response.text},
                    status=response.status_code
                )

            return JsonResponse(response.json())
            
        except Exception as e:
            print(f"Full error: {traceback.format_exc()}")  # Debug
            return JsonResponse(
                {'error': str(e), 'type': type(e).__name__},
                status=500
            )
            
from .models import SMSMessage
from django.utils import timezone
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import json

@method_decorator(csrf_exempt, name='dispatch')
class TermiiWebhookView(View):
    def get(self, request, *args, **kwargs):
        # For Termii webhook verification (handshake)
        print("GET request received - webhook verification")
        return HttpResponse("Webhook Verified", status=200)

    def post(self, request, *args, **kwargs):
        try:
            payload = json.loads(request.body)

            print("Received Termii Webhook:", payload)

            message_id = payload.get('message_id')
            receiver = payload.get('receiver')
            sender = payload.get('sender')
            message_text = payload.get('message')
            sent_at = payload.get('sent_at')
            cost = payload.get('cost')
            status = payload.get('status', '').lower().replace(" ", "_")
            channel = payload.get('channel')

            # Map Termii status to model choices
            status_map = {
                "message sent": "sent",
                "delivered": "delivered",
                "message failed": "failed",
                "dnd active on phone number": "dnd",
                "expired": "expired",
                "rejected": "rejected"
            }

            db_status = status_map.get(status, "failed")

            # Save or update message status
            obj, created = SMSMessage.objects.update_or_create(
                message_id=message_id,
                defaults={
                    'message_request_id': payload.get('id'),
                    'receiver': receiver,
                    'sender': sender,
                    'message': message_text,
                    'status': db_status,
                    'channel': channel,
                    'cost': float(cost) if cost else 0.0,
                    'sent_at': timezone.now()  # You can improve this by parsing ISO format if available
                }
            )

            return JsonResponse({"status": "received"}, status=200)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)


# Standalone function-based view for dashboard
def sms_dashboard(request):
    messages = SMSMessage.objects.all().order_by('-sent_at')[:100]
    return render(request, 'report.html', {'messages': messages})