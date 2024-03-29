from django.shortcuts import render

from django.views.decorators.http import require_http_methods
from django.http.request import HttpRequest
from django.http.response import HttpResponse, HttpResponseBadRequest

from decouple import config
from linebot import LineBotApi
from linebot.models import RichMenu, RichMenuSize, RichMenuArea, RichMenuBounds, URIAction, MessageAction
from richmenu.models import Richmenu
line_bot_api = LineBotApi(config('LINE_CHANNEL_ACCEESS_TOKEN'))

# Create your views here.
@require_http_methods(["POST"])
def createRichmenu(request: HttpRequest):
    if request.method == 'POST':
        role = request.POST.get('role', "user")
        if role == 'admin':
            rich_menu_to_create = RichMenu(
                size=RichMenuSize(width=2500, height=843),
                selected=False,
                name="團長選單",
                chat_bar_text="開啟選單",
                areas=[
                    RichMenuArea(bounds=RichMenuBounds(x=0, y=0, width=833, height=843),
                                    action=URIAction(label='發起球約邀請', uri='https://badminton-linebot.herokuapp.com/web/form')),
                    RichMenuArea(bounds=RichMenuBounds(x=833, y=0, width=833, height=843),
                                    action=URIAction(label='查看所有球約', uri='https://badminton-linebot.herokuapp.com/web/index')),
                                    RichMenuArea(bounds=RichMenuBounds(x=1663, y=0, width=833, height=843),
                                    action=URIAction(label='查看報名表單', uri='https://badminton-linebot.herokuapp.com/web/list'))
                ]
            )
            rich_menu_id = line_bot_api.create_rich_menu(rich_menu=rich_menu_to_create)
            line_bot_api.set_rich_menu_image(rich_menu_id, 'image/png', open('image/admin.png', 'rb'))
            Richmenu(name='團長選單', token=rich_menu_id, role='admin', urls=['https://badminton-linebot.herokuapp.com/web/form',
                                                                             'https://badminton-linebot.herokuapp.com/web/index',
                                                                             'https://badminton-linebot.herokuapp.com/web/list']).save()
        else:
            rich_menu_to_create = RichMenu(
                size=RichMenuSize(width=2500, height=843),
                selected=False,
                name="一般選單",
                chat_bar_text="開啟選單",
                areas=[
                    RichMenuArea(bounds=RichMenuBounds(x=0, y=0, width=833, height=843),
                                    action=URIAction(label='私訊團主', uri='https://line.me/ti/p/0arAve3Q6R')),
                    RichMenuArea(bounds=RichMenuBounds(x=833, y=0, width=833, height=843),
                                    action=MessageAction(label='查看報名表單', text='此功能未開啟')),
                                    RichMenuArea(bounds=RichMenuBounds(x=1663, y=0, width=833, height=843),
                                    action=MessageAction(label='更改暱稱', text='此功能未開啟'))
                ]
            )
            rich_menu_id = line_bot_api.create_rich_menu(rich_menu=rich_menu_to_create)
            line_bot_api.set_rich_menu_image(rich_menu_id, 'image/png', open('image/user.png', 'rb'))
            Richmenu(name='使用者選單', token= rich_menu_id, role='user', urls=['https://line.me/ti/p/0arAve3Q6R']).save()
