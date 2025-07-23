from django.urls import path
from . import views
from .views import SendSMSView,SendSMSBULKView,BalanceView,TermiiWebhookView

app_name = 'messange'

urlpatterns = [
    path('send-sms/', SendSMSView.as_view(), name='messange'),
    path('send-sms-bulk/', SendSMSBULKView.as_view(), name='messange_bulk'),
    path('balance/', BalanceView.as_view(), name='balance'),
    path('termii-webhook/', TermiiWebhookView.as_view(), name='termii_webhook'),
    path('sms-dashboard/', views.sms_dashboard, name='report'),
    ]