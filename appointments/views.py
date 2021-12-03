from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from django.shortcuts import render

from appointments.models import User

def homePageView(request):
    uid = User.objects.values('uid')[0]['uid']
    return render(request, "appointments/index.html", {'uid': uid})