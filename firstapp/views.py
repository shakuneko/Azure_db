from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import MessageEvent, TextMessage, PostbackEvent
from module import func
from linebot.models import TextSendMessage,ImageSendMessage,StickerSendMessage,LocationSendMessage,QuickReply,QuickReplyButton,MessageAction
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from module.func import sendMission, handle_postback
from urllib.parse import parse_qsl
from firstapp.models import users
from .models import Task
import json
line_bot_api = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)
parser = WebhookParser(settings.LINE_CHANNEL_SECRET)

def sayhello(request):
    return HttpResponse("Hello Django!")

@csrf_exempt
def create_task(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        max_id = Task.objects.aggregate(Max('id'))['id__max']
        new_id = max_id + 1 if max_id else 1  # 如果数据库中没有任务，则 id 设为 1
        task = Task.objects.create(
            id=new_id,
            task_name=data['task'],
            time=data['time'],
            date=data['date'],
            category=data['category']
        )
        return JsonResponse({'id': task.id, 'task_name': task.task_name, 'time': task.time, 'date': task.date, 'category': task.category})
    else:
        return JsonResponse({'error': 'Only POST method allowed'})
    
    
@csrf_exempt
def callback(request):
    if request.method == 'POST':
        signature = request.META['HTTP_X_LINE_SIGNATURE']
        body = request.body.decode('utf-8')
        try:
            events = parser.parse(body, signature)
        except InvalidSignatureError:
            return HttpResponseForbidden()
        except LineBotApiError:
            return HttpResponseBadRequest()

        for event in events:
            if isinstance(event, MessageEvent):
                user_id = event.source.user_id
                if not (users.objects.filter(uid=user_id).exists()):
                    unit = users.objects.create(uid=user_id)
                    unit.save()
                mtext = event.message.text

                if mtext == '今日任務':
                    func.sendMission(event)
                elif mtext == '時間箱':
                    func.sendTimeBox(event)
                elif mtext == '冒險故事':
                    func.sendStory(event)
                elif mtext == '成就列表':
                    func.sendList(event)
                elif mtext.startswith('新增'):
                    func.manageForm(event, mtext)
                    #func.manageRECEIPT(event, mtext, user_id)

    
            elif isinstance(event, PostbackEvent):
                handle_postback(event)
                
            if isinstance(event, PostbackEvent):
                backdata = dict(parse_qsl(event.postback.data))
                result = event.postback.data[2:].split('&')
                
                if backdata.get('action') == '第一章':
                    func.sendback_1(event, backdata)
                elif backdata.get('action') == '第二章':
                     func.sendback_2(event, backdata)
                elif backdata.get('action') == '第三章':
                    func.sendback_3(event, backdata)
                elif backdata.get('action') == '第四章':
                    func.sendback_4(event, backdata)
                elif backdata.get('action') == '第五章':
                    func.sendback_5(event, backdata)
                elif backdata.get('action') == '日常':
                    func.handle_quick_reply(event)
                        
        return HttpResponse()  
    
    else:
        return HttpResponseBadRequest()