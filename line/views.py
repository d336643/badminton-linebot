from django.shortcuts import render
import logging
from decouple import config

from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.http.request import HttpRequest
from django.http.response import HttpResponse, HttpResponseBadRequest

from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextSendMessage, TextMessage, LocationSendMessage, PostbackEvent, FollowEvent, UnfollowEvent


from appointments.models import User, Appointment, HourDetail, Invitation
from richmenu.models import Richmenu

line_bot_api = LineBotApi(config('LINE_CHANNEL_ACCEESS_TOKEN'))
handler = WebhookHandler(config('LINE_CHANNEL_SECRET'))

logger = logging.getLogger("django")

@csrf_exempt
@require_http_methods(["POST"])
def lineWebhook(request: HttpRequest):
    signature = request.headers["X-Line-Signature"]
    body = request.body.decode()
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        messages = (
            "Invalid signature. Please check your channel access token/channel secret."
        )
        logger.error(messages)
        return HttpResponseBadRequest(messages)
    return HttpResponse("OK")

@handler.add(event=MessageEvent, message=TextMessage)
def handl_message(event: MessageEvent):
    print(event)
    if event.source.user_id != "U4f6b7a8dd9569c69504abb9add177102":
        if event.message.text == '烏拉拉':
            user = User.objects.get(line_uid=event.source.user_id)
            user.role = 'admin'
            user.save()
            richmenu = Richmenu.objects.get(role='admin')
            line_bot_api.link_rich_menu_to_user(event.source.user_id, richmenu.token)
            line_bot_api.reply_message(
                reply_token=event.reply_token,
                messages=TextSendMessage(text='團長你的權限設定好囉～'),
            )
        elif event.message.text == '拉拉烏':
            user = User.objects.get(line_uid=event.source.user_id)
            user.role = ''
            user.save()
            richmenu = Richmenu.objects.get(role='user')
            line_bot_api.link_rich_menu_to_user(event.source.user_id, richmenu.token)
            line_bot_api.reply_message(
                reply_token=event.reply_token,
                messages=TextSendMessage(text='好啊～ 你已經不是團長囉～'),
            )

@handler.add(event=PostbackEvent)
def handl_postback(event: PostbackEvent):
    print(event.postback.data)
    line_uid = event.source.user_id
    select_status = event.postback.data.split('/')[1]
    aid = event.postback.data.split('/')[0].split('_')[1]
    uid = User.objects.get(line_uid=line_uid).id
    appointment_obj = Appointment.objects.get(id=aid)
    hd_objs = appointment_obj.hour_details.values()
    hd_ids = [hd_obj['id'] for hd_obj in hd_objs]
    invitaions_objs = Invitation.objects.filter(user=uid, hour_detail__in=hd_ids)
    current_status = invitaions_objs[0].status
    
    if current_status == 'Waiting' and select_status == 'accepted':
        invitaions_objs.update(status='Accepted')
        ls = appointment_obj.user_order_ls
        ls.remove(uid)
        appointment_obj.user_order_ls = ls
        appointment_obj.save()
        
        line_bot_api.reply_message(
            reply_token=event.reply_token,
            messages=[
                TextSendMessage(text='太好了～ 那我們在「中山運動中心」集合～'),
                LocationSendMessage(
                    title='中山運動中心',
                    address='中山運動中心',
                    latitude=25.055042057398026,
                    longitude=121.52146272638235
                )
            ]
        )
    elif current_status == 'Waiting' and select_status == 'declined':
        invitaions_objs.update(status='Declined')
        ls = appointment_obj.user_order_ls
        ls.remove(uid)
        appointment_obj.user_order_ls = ls
        appointment_obj.save()
        
        line_bot_api.reply_message(
            reply_token=event.reply_token,
            messages=TextSendMessage(text='真可惜，歡迎下次再來～')
        )
    elif current_status == 'Accepted' and select_status == 'declined':
        line_bot_api.reply_message(
            reply_token=event.reply_token,
            messages=TextSendMessage(text='您已接受邀請，要取消報名請聯絡團主')
        )
    elif current_status == 'Accepted' and select_status == 'accepted':
        line_bot_api.reply_message(
            reply_token=event.reply_token,
            messages=TextSendMessage(text='你已經接受報名')
        )
    elif current_status == 'Declined' and select_status == 'declined':
        line_bot_api.reply_message(
            reply_token=event.reply_token,
            messages=TextSendMessage(text='你已經取消報名')
        )
    elif current_status == 'Declined' and select_status == 'accepted':
        line_bot_api.reply_message(
            reply_token=event.reply_token,
            messages=TextSendMessage(text='你已拒絕邀請，請聯絡團主重新報名')
        )

@handler.add(event=FollowEvent)
def handl_follow(event: FollowEvent):
    print('event', event.source.user_id)
    if event.source.user_id != "U4f6b7a8dd9569c69504abb9add177102":
        user = User.objects.get_or_create(line_uid=event.source.user_id)[0]
        profile = line_bot_api.get_profile(event.source.user_id)
        user.nickname = profile.display_name
        user.avatar_url = profile.picture_url
        # user.status = 'follow'
        user.save()
        rich_menu_id = 'richmenu-9ea9e3e9224968fac96b594ebc18bde8'
        line_bot_api.link_rich_menu_to_user(event.source.user_id, rich_menu_id)
        line_bot_api.reply_message(reply_token=event.reply_token,
                                   messages=TextSendMessage(text="你好～\n歡迎加入「老楊揪打球」，團主老楊會邀請你參加指定時段的球約\n你可以接受/拒絕邀請！\n\n選單可以查看報名狀況，以及私訊團主！"))

@handler.add(event=UnfollowEvent)
def handl_follow(event: UnfollowEvent):
    print('event', event.source.user_id)
    if event.source.user_id != "U4f6b7a8dd9569c69504abb9add177102":
        user = User.objects.get(line_uid=event.source.user_id)
        # user.status = 'unfollow'
        user.save()


