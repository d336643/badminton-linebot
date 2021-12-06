from django.urls import path
from appointments import views

urlpatterns = [
    path('form', views.formView),
    path('index', views.indexView),
    path('list', views.listView),
    path('create', views.createAppointment),
    path('delete', views.deleteAppointment),
    path('invite_all', views.invite_all),
]