from django.urls import path
from appointments import views

urlpatterns = [
    path('form', views.formView),
    path('index', views.indexView),
]