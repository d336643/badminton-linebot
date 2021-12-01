from django.urls import path
from appointments import views

urlpatterns = [
    path('test', views.homePageView),
]