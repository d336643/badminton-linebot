from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from django.shortcuts import render

from appointments.models import User
from appointments.models import Appointment

def indexView(request):
    uid = User.objects.values('uid')[0]['uid']
    return render(request, "appointments/index.html", {'uid': uid})

def formView(request):
    uid = User.objects.values('uid')[0]['uid']
    return render(request, "appointments/form.html", {'uid': uid})

def createAppointment(request):
    if request.method == 'POST':
        try:
            name = request.data['appointment_name']
            starttime = request.data['start_time']
            endtime = request.data['end_time']
        except KeyError:
            return HttpResponse("3 parameters are all required.(name, starttime, endtime)")
        
        new_appointment = Appointment(name=name, starttime=starttime, endtime=endtime, )
        
        return HttpResponse("Success!")