from django.urls import path
from line import views

urlpatterns = [
    path('line_webhook', views.lineWebhook),
]