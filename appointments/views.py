from django.shortcuts import redirect, render

# Create your views here.
from appointments.models import User, Appointment, HourDetail, Invitation

from django.views.decorators.http import require_http_methods
from django.http.request import HttpRequest
from django.http.response import HttpResponse, HttpResponseBadRequest

from datetime import datetime, timezone, timedelta

from decouple import config
from linebot import LineBotApi, WebhookParser, WebhookHandler
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import MessageEvent, TextSendMessage, FlexSendMessage, TextMessage, PostbackEvent
line_bot_api = LineBotApi(config('LINE_CHANNEL_ACCEESS_TOKEN'))

    
def indexView(request: HttpRequest):
    tz = timezone(timedelta(hours=+8))
    result = Appointment.objects.filter(endtime__gte=datetime.now(tz)).values('id', 'name', 'starttime')
    apps_info = []
    for a_info in result:
        apps_info.append({'aid':a_info['id'], 'name': a_info['name'], 'date':a_info['starttime'].strftime('%Y-%m-%d')})
    
    return render(request, "appointments/index.html", {"apps_info":apps_info})

def formView(request: HttpRequest):
    return render(request, "appointments/form.html", {'current_step': 1})

def listView(request: HttpRequest):
    if not Appointment.objects.all().exists():
      return render(request, "appointments/list.html", {'apps_info': [], 'hour_details': [], 'users': [], 'current_aid': 0})
 
    current_aid = request.GET.get('aid', None)
    if current_aid:
        current_appointment = Appointment.objects.get(id=current_aid)
    else:
        current_appointment = Appointment.objects.order_by('-starttime')[0]
        
    apps_info = list(Appointment.objects.all().values('id','name'))
    for app_dict in apps_info:
        app_dict['selected'] = current_appointment.id == app_dict['id']
    
    
    hdobjs = current_appointment.hour_details.all()
    hour_details = []
    users = []
    for hdobj in hdobjs:
        hour_details.append({"hour": hdobj.hour,
                             "people_cnt": hdobj.people_cnt,
                             "accepted_cnt": len(list(hdobj.invitation_set.filter(status='Accepted').values())),
                             "ratio": len(list(hdobj.invitation_set.filter(status='Accepted').values())) * 100 / hdobj.people_cnt})
        users += list(hdobj.user_set.values('id','nickname'))

    users = list({myObject['id']:myObject for myObject in users}.values())
    for user_dict in users:
        uid = user_dict['id']
        hdobjs = User.objects.get(id=uid).hourdetails.filter(appointment_id=current_appointment.id)
        hours = hdobjs.values_list('hour')
        hdid = hdobjs.values('id')[0]['id']
        status = Invitation.objects.get(hour_detail=hdid, user=uid).status
        user_dict['starthour'] = min(hours)[0]
        user_dict['endhour'] = max(hours)[0] + 1
        user_dict['status'] = status
    return render(request, "appointments/list.html", {'apps_info': apps_info, 'hour_details': hour_details, 'users': users, 'current_aid': current_appointment.id})

@require_http_methods(["DELETE"])
def deleteAppointment(request: HttpRequest):
    if request.method == 'POST':
        aid = request.POST.get('aid', 0)
        Appointment.objects.get(aid=aid).delete()
        return Response('OK')
    
@require_http_methods(["POST"])
def createAppointment(request: HttpRequest):
    if request.method == 'POST':
        step = int(request.POST.get('step', 0))
        if step == 2:
            try:
                name = request.POST.get('appointment_name', "No name")
                starttime = request.POST.get('start_time', "1997-11-20 00:00")
                endtime = request.POST.get('end_time', "1997-11-20 00:00")
            except KeyError:
                return HttpResponseBadRequest("4 parameters are all required.(name, starttime, endtime, step)")
            
            starthour = int(starttime.split()[1].split(':')[0])
            endhour = int(endtime.split()[1].split(':')[0])
            date_ = endtime.split()[0]
            hours = endhour - starthour
            new_appointment = Appointment(name=name, starttime=starttime, endtime=endtime, step=step, hours=hours)
            new_appointment.save()
            return render(request, "appointments/form.html", {'current_step': step, 'aid': new_appointment.id, 'range': [f"{i}-{i+1}" for i in range(starthour, endhour)], 'date': date_})
        
        elif step == 3:
            aid = int(request.POST.get('aid', 0))
            appointment = Appointment.objects.get(id=aid)
            
            starthour = appointment.starttime.hour
            hours = [starthour+h for h in range(appointment.hours)]
            
            # delete_hds = HourDetail.objects.filter(appointment_id=aid).exclude(hour__in=hours)
            # delete_hds.delete()
            
            for i,h in enumerate(hours, start=1):
                hd = HourDetail.objects.get_or_create(appointment_id=aid, hour=h)[0]
                hd.court_cnt= request.POST.get(f'court_cnt_{i}', 0)
                hd.people_cnt=request.POST.get(f'people_cnt_{i}', 0)
                hd.save()
            
            date_ = appointment.starttime.strftime("%Y%m%d")
            users = User.objects.all()
            
            appointment.step = step
            appointment.save()
            
            return render(request, "appointments/form.html", {'current_step': step, 'aid': aid, 'date': date_, 'users': users})
        
        elif step == 4: 
            aid = int(request.POST.get('aid', 0))
            uids = request.POST.getlist('uids')
            appointment = Appointment.objects.get(id=aid)
            starthour = appointment.starttime.hour
            hours = [starthour+h for h in range(appointment.hours)]
            
            users = User.objects.filter(id__in=uids)
            
            hour_array = [i for i in range(appointment.starttime.hour, appointment.endtime.hour)]
            
            appointment.step = step
            appointment.save()
            return render(request, "appointments/form.html", {'current_step': step, 'aid': aid, 'users': users, 'hours': hour_array})
        
        elif step == 5:
            # selected_hours = {uid: [hour1, hour2..], ...}
            selected_hours = {}
            for k in request.POST.keys():
                if k.split('_')[0] == 'uid':
                    selected_hours[int(k.split('_')[1])] = request.POST.getlist(k)    
            aid = int(request.POST.get('aid', 0))
            
            
            # search hd_ids
            hour_objs = HourDetail.objects.filter(appointment_id=aid)
            for uid, hours in selected_hours.items():
                # Invitation.objects.filter(user_id=uid).exclude(hour_detail_id__in=hour_objs.filter(hour__in=hours).values_list('id')).delete()
                for hour in hours:
                    hd_id = hour_objs.get(hour=hour).id
                    invitation = Invitation.objects.get_or_create(user_id=uid, hour_detail_id=hd_id)[0]
                    invitation.status = 'Accepted'
                    invitation.save()
            
            datum = []
            for h_obj in hour_objs:
                data = {}
                data['hour'] = h_obj.hour
                data['accepted_cnt'] = len(h_obj.invitation_set.values())
                data['people_cnt'] = h_obj.people_cnt
                data['ratio'] = len(h_obj.invitation_set.filter(status='Accepted').values()) * 100 / h_obj.people_cnt
                datum.append(data)
            
            # search for uninvited users
            invited_uids = list(selected_hours.keys())
            uninvited_users = User.objects.exclude(id__in=invited_uids)
            
            appointment = Appointment.objects.get(id=aid)
            appointment.step = step
            appointment.save()
            
            return render(request, "appointments/form.html", {'current_step': step, 'aid': aid, 'datum': datum, 'users': uninvited_users})
        
        elif step == 6: 
            aid = int(request.POST.get('aid', 0))
            uids = request.POST.getlist('uids')
            appointment = Appointment.objects.get(id=aid)
            
            starthour = appointment.starttime.hour
            hours = [starthour+h for h in range(appointment.hours)]
            
            users = User.objects.filter(id__in=uids)
            
            hour_array = [i for i in range(appointment.starttime.hour, appointment.endtime.hour)]
            
            appointment.step = step
            appointment.save()
            return render(request, "appointments/form.html", {'current_step': step, 'aid': aid, 'users': users, 'hours': hour_array})
        
        elif step == 7:
            # selected_hours = {uid: [hour1, hour2..], ...}
            selected_hours = {}
            for k in request.POST.keys():
                if k.split('_')[0] == 'uid':
                    selected_hours[int(k.split('_')[1])] = request.POST.getlist(k)    
            aid = int(request.POST.get('aid', 0))
            
            
            # search hd_ids
            hour_objs = HourDetail.objects.filter(appointment_id=aid)
            for uid, hours in selected_hours.items():
                # Invitation.objects.filter(user_id=uid).exclude(hour_detail_id__in=hour_objs.filter(hour__in=hours).values_list('id')).delete()
                for hour in hours:
                    hd_id = hour_objs.get(hour=hour).id
                    invitation = Invitation.objects.get_or_create(user_id=uid, hour_detail_id=hd_id)[0]
                    invitation.status = 'Uninvited'
                    invitation.save()
            
            # search each user's start hour and end hour
            to_be_invited_uids = list(selected_hours.keys())
            to_be_invited_users = User.objects.filter(id__in=to_be_invited_uids)
            users = []
            uids = []
            for user in to_be_invited_users:
                u = {}
                u['uid'] = user.id
                uids.append(str(user.id))
                u['nickname'] = user.nickname  
                hours = user.hourdetails.filter(appointment_id=aid).values_list('hour')  
                u['starthour'] = min(hours)[0]
                u['endhour'] = max(hours)[0]+1
                    
                users.append(u)
            uids = ','.join(uids)
            appointment = Appointment.objects.get(id=aid)
            appointment.step = step
            appointment.save()
            
            return render(request, "appointments/form.html", {'current_step': step, 'aid': aid, 'users': users, 'uids': uids})

        elif step == 8:
            aid = request.POST.get('aid', 0)
            uids = [int(i) for i in request.POST.get('uids', '0').split(',')]
            appointment = Appointment.objects.get(id=aid)
            
            appointment.step = step
            appointment.user_order_ls = uids
            appointment.save()
            
            return redirect(f"/web/list?aid={aid}")
        
def invite_all(request: HttpRequest):
    aid = request.GET.get('aid', None)
    appointment = Appointment.objects.get(id=aid)
    invited_uids = appointment.user_order_ls
    if not invited_uids:
      return redirect(f"/web/index")
    users_info = User.objects.filter(id__in=invited_uids).values()
    hd_objs = Appointment.objects.get(id=aid).hour_details.values()
    hd_ids = [hd_obj['id'] for hd_obj in hd_objs]
    Invitation.objects.exclude(status='Accepted')\
                      .filter(user_id__in=invited_uids, hour_detail_id__in=hd_ids)\
                      .update(status='Waiting')
    ## 傳給多人
    line_bot_api.multicast([user_info['line_uid'] for user_info in users_info],
                           FlexSendMessage(alt_text='打球啊',
                                           contents=invitationFlexMessageFormat(appointment)))
    ## 一次傳給一個人
    # for user_info in users_info:
    #     line_bot_api.push_message(user_info['line_uid'], FlexSendMessage(alt_text='打球啊', contents=invitationFlexMessageFormat(appointment)))
    
    return redirect(f"/web/index")

def invitationFlexMessageFormat(appointment):
    return {
        "type": "bubble",
        "hero": {
          "type": "image",
          "url": "https://tnimage.s3.hicloud.net.tw/photos/2020/01/21/1579574456-5e2664b82353c.jpg",
          "size": "full",
          "aspectRatio": "20:13",
          "aspectMode": "cover"
        },
        "body": {
          "type": "box",
          "layout": "vertical",
          "contents": [
            {
              "type": "text",
              "text": "老楊邀請你打球",
              "weight": "bold",
              "size": "xl"
            },
            {
              "type": "box",
              "layout": "vertical",
              "margin": "lg",
              "spacing": "sm",
              "contents": [
                {
                  "type": "box",
                  "layout": "baseline",
                  "spacing": "sm",
                  "contents": [
                    {
                      "type": "text",
                      "text": "日期",
                      "color": "#aaaaaa",
                      "size": "sm",
                      "flex": 1
                    },
                    {
                      "type": "text",
                      "text": appointment.starttime.strftime('%Y-%m-%d'),
                      "wrap": True,
                      "color": "#666666",
                      "size": "sm",
                      "flex": 5
                    }
                  ]
                },
                {
                  "type": "box",
                  "layout": "baseline",
                  "spacing": "sm",
                  "contents": [
                    {
                      "type": "text",
                      "text": "時間",
                      "color": "#aaaaaa",
                      "size": "sm",
                      "flex": 1
                    },
                    {
                      "type": "text",
                      "text": f"{appointment.starttime.strftime('%H:%M')} - {appointment.endtime.strftime('%H:%M')}",
                      "wrap": True,
                      "color": "#666666",
                      "size": "sm",
                      "flex": 5
                    }
                  ]
                }
              ]
            }
          ]
        },
        "footer": {
          "type": "box",
          "layout": "horizontal",
          "spacing": "sm",
          "contents": [
            {
              "type": "button",
              "style": "link",
              "height": "sm",
              "action": {
                "type": "postback",
                "label": "接受",
                "data": f"aid_{appointment.id}/accepted",
                "displayText": "我要參加！"
              }
            },
            {
              "type": "button",
              "style": "link",
              "height": "sm",
              "action": {
                "type": "postback",
                "label": "拒絕",
                "data": f"aid_{appointment.id}/declined",
                "displayText": "我有事ＱＱ"
              }
            }
          ],
          "flex": 0,
          "paddingTop": "0px"
        }
    }