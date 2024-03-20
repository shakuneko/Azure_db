from django.conf import settings

from linebot import LineBotApi
from linebot.models import *
from linebot.models import ConfirmTemplate, PostbackTemplateAction, URITemplateAction
from linebot.models import TextSendMessage,ImageSendMessage,StickerSendMessage,LocationSendMessage,QuickReply,QuickReplyButton,MessageAction
from linebot.models import FlexSendMessage,TemplateSendMessage,ButtonsTemplate, PostbackTemplateAction
from linebot.models.flex_message import (
    BubbleContainer, ImageComponent,BoxComponent,
)
from firstapp.models import users,booking,Task,Gift,UserGift
from linebot.models.actions import URIAction
from datetime import datetime,date
import random
line_bot_api = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)

###Carousel 是一種顯示多個 Bubble（氣泡）的方式，產生多個圖表來存放任務
def generate_carousel(tasks):
    bubbles = []
    for task in tasks:
        bubble = {
                "type": "bubble",
                "size": "hecto",
                "header": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                    {
                        "type": "text",
                        "text": task.task_name,
                        "size": "xl",
                        "weight": "bold"
                    }
                    ],
                    "paddingBottom": "md"
                },
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                    {
                        "type": "text",
                        "text": task.category
                    },
                    {
                        "type": "separator",
                        "margin": "lg"
                    }
                    ],
                    "paddingTop": "none",
                    "paddingBottom": "none"
                },
                "footer": {
                    "type": "box",
                    "layout": "horizontal",
                    "spacing": "sm",
                    "contents": [
                    {
                        "type": "button",
                        "style": "primary",
                        "action": {
                        "type": "postback",
                        "label": "完成",
                        "data": "action=completed&task_name=" + task.tid
                        },
                        "color": "#597EF7"
                    },
                    {
                        "type": "button",
                        "action": {
                        "type": "postback",
                        "label": "刪除",
                        "data": "action=incompleted"
                        },
                        "color": "#496496"
                    }
                    ]
                },
                "styles": {
                    "body": {
                    "separator": False
                    }
                }
        }
        bubbles.append(bubble) # 將每個 Bubble 加入到列表中

    carousel = {
        "type": "carousel",
        "contents": bubbles # 將 Bubble 列表添加到 carousel 中
    }
    return carousel

##冒險故事用回覆框
def generate_carousel2(chapter):
    bubbles = []
    for task in chapter:
        bubble = {
            "type": "bubble",
            "direction": "ltr",
            "body": {
                 "type": "box",
                 "layout": "vertical",
                 "contents": [
                     {"type": "text", "text": task, "weight": "regular", "size": "lg", "align": "center","margin": "xl"},
                     {"type": "separator", "margin": "xl"}
                 ]
             },
            "footer": {
                "type": "box",
                "layout": "horizontal",
                "contents": [
                    {
                        "type": "button",
                        "style": "primary",
                        "color": "#597EF7",
                        "margin": "xl",
                        "action": {"type": "postback", "label": "好啊", "data": "action=completed"}
                    },
                    {
                        "type": "button",
                        "color": "#496496",
                        "margin": "xl",
                        "action": {"type": "postback", "label": "我沒有", "data": "action=incomplete"}
                    }
                ]
            }
        }
        bubbles.append(bubble) # 將每個 Bubble 加入到列表中

    carousel = {
        "type": "carousel",
        "contents": bubbles # 將 Bubble 列表添加到 carousel 中
    }
    return carousel

###今日任務
#判斷是不是今天
def is_today(task_date):
    # 拿到目前日期
    today = date.today()
    # 比教任務跟今天日期
    return task_date == today
def sendMission(event):
    try:
        tasks = Task.objects.all()  # 拿到所有任務
         # 过滤出今天的任务，同时排除已完成的任务
        today_tasks = [task for task in tasks if is_today(task.date) and task.tid not in completed_tasks]
        print(completed_tasks)
        if today_tasks:
            message = TextSendMessage(
                text='以下是今日任務',
            )
            flex_message = FlexSendMessage(
                alt_text='今日任務',
                contents=generate_carousel(today_tasks) # 生成包含多個任務的 Carousel Flex Message
            )
            line_bot_api.reply_message(event.reply_token, [message, flex_message])
        else:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text='目前沒有任務需要處理'))
        
    except Exception as e:
        print(f"Error sending mission: {e}")
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='發生錯誤！'))

###完成任務獎勵
completed_tasks = set() # 用來記錄完成的任務數量
def handle_postback(event):
    global completed_tasks
    postback_data = event.postback.data
    if postback_data.startswith('action=completed'):
        task_id = postback_data.split('&')[1].split('=')[1]
        # 檢查是否已經完成任務
        if task_id not in completed_tasks:
            completed_tasks.add(task_id)  # 將已完成的任務添加到集合中
            experience_percentage = calculate_experience_percentage(len(completed_tasks))
            message1 = TextSendMessage(text='恭喜！又完成一項任務啦～\n繼續努力吧！')
            message2 = generate_experience_message(experience_percentage)
            line_bot_api.reply_message(event.reply_token, [message1, message2])

            #刪除已完成的任務
            # datadel=Task.objects.get(tid=task_id)
            # datadel.delete()
            # print(f"任务 {task_id} 已成功删除")

            # 檢查今天的所有任務是否都已經完成
            # today_tasks = Task.objects.filter(date=date.today())
            # if len(completed_tasks) == today_tasks.count():
            #     handle_all_tasks_completed(event.source.user_id)
            if len(completed_tasks) >= 5:
                handle_all_tasks_completed(event.source.user_id)
        else:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text='該任務已經完成過了！'))
    elif postback_data.startswith('action=open_treasure_box'):
        get_gift(event)

def handle_all_tasks_completed(user_id):
    # 在這裡添加您希望在所有任務完成時執行的代碼
    text1 = TextSendMessage(text='\ 今日任務全部完成 / \n點選寶箱來領取獎勵吧！')
    flex_message = {
        "type": "bubble",
        "hero": {
            "type": "image",
            "url": "https://img.freepik.com/premium-vector/wooden-treasure-box-pirate-isolated-vector-illustration_509778-62.jpg?w=740",
            "size": "full",
            "aspectRatio": "20:13",
            "aspectMode": "cover",
            "action": {
                "type": "postback",
                "label": "開啟寶箱",
                "data": "action=open_treasure_box"
            }
        }
    }
    # 发送文本消息和 Flex Message
    line_bot_api.push_message(user_id, [text1, FlexSendMessage(alt_text="開啟寶箱", contents=flex_message)])


def get_gift(event):
    # 获取用户已经获得的所有礼物
    user_gifts = UserGift.objects.filter(user=event.source.user_id)
    user_gift_names = set(user_gift.gift.giftname for user_gift in user_gifts)

    # 获取所有礼物，并排除用户已经获得的礼物
    available_gifts = Gift.objects.exclude(giftname__in=user_gift_names)

    # 如果还有可用的礼物
    if available_gifts.exists():
        # 从剩余的礼物中随机选择一个
        selected_gift = random.choice(available_gifts)
        # 创建一个 UserGift 实例，将其与用户关联并保存到数据库中
        user_gift = UserGift.objects.create(user=event.source.user_id, gift=selected_gift)
        user_gift.save()

        # 创建 Flex Message 以回复用户
        flex_message = {
            "type": "bubble",
            "header": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": f"恭喜獲得{selected_gift.giftname}～"
                    }
                ]
            },
            "hero": {
                "type": "image",
                "url": selected_gift.image_url,
                "size": "4xl",
                "aspectMode": "cover"
            },
            "footer": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "button",
                        "style": "primary",
                        "height": "md",
                        "action": {
                            "type": "uri",
                            "label": "確認",
                            "uri": "https://example.com/shield_details"
                        },
                        "color": "#597EF7"
                    }
                ]
            }
        }

        # 回复用户
        line_bot_api.reply_message(event.reply_token, FlexSendMessage(alt_text="禮物", contents=flex_message))
    else:
        # 如果所有礼物都已经被用户获得，向用户发送消息提示
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="您已經獲得了所有可用的禮物！"))
def calculate_experience_percentage(completed_tasks):
    # 根據完成的任務數量計算經驗值增加的百分比
    # 這裡可以根據你的需求設定不同的增加規則
    # 以下是一個簡單的範例
    if completed_tasks <= 10:
        return completed_tasks * 10  # 每完成一個任務增加10%
    else:
        return 100  # 最多增加到100%

def generate_experience_message(experience_percentage):
    # 生成經驗值計算的 Flex Message
    return FlexSendMessage(
        alt_text='經驗值計算',
        contents={
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "經驗值",
                        "size": "lg",
                        "margin": "none"
                    },
                    {
                        "type": "text",
                        "text": f"{experience_percentage}%",
                        "margin": "lg",
                        "size": "md"
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {
                                "type": "box",
                                "layout": "vertical",
                                "contents": [],
                                "width": f"{experience_percentage}%",
                                "backgroundColor": "#597EF7",
                                "height": "15px",
                                "cornerRadius": "10px"
                            }
                        ],
                        "margin": "md",
                        "backgroundColor": "#D6E4FF",
                        "height": "15px",
                        "cornerRadius": "10px"
                    }
                ]
            },
        }
    )

###時間箱
def create_task_box(start_time, task_name, index):
    is_even = index % 2 == 0
    circle_color = "#6486E3" if is_even else "#ADC6FF"  # 偶數項深藍色，奇數項淺藍色
    circle_size = "14px" if is_even else "10px"  # 偶數項大原，奇數項小圓
    background_color = circle_color if is_even else "#FFFFFF"  # 偶數項填滿整個深藍，奇數項不填充

    return {
        "type": "box",
        "layout": "horizontal",
        "contents": [
            {
                "type": "box",
                "layout": "horizontal",
                "contents": [
                    {
                        "type": "text",
                        "text": start_time,
                        "gravity": "center",
                        "size": "sm",
                        "align": "center",
                        "margin": "none"
                    }
                ],
                "flex": 2,
                "spacing": "sm",
                "margin": "none"
            },
            {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {"type": "filler"},
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [],
                        "cornerRadius": "30px",
                        "width": circle_size,
                        "height": circle_size,
                        "backgroundColor": background_color,  # 修改為 background_color
                        "borderWidth": "2px",
                        "borderColor": circle_color,
                        "margin": "none"
                    },
                    {"type": "filler"}
                ],
                "flex": 2,
                "alignItems": "center",
                "margin": "8px"
            },
            {
                "type": "text",
                "text": task_name,
                "gravity": "center",
                "flex": 4,
                "size": "sm",
                "margin": "xl"
            }
        ],
        "spacing": "lg",
        "cornerRadius": "30px",
        "margin": "md"
    }
def create_time_schedule(today_tasks):
    time_schedule_contents = []
    all_times = ["06:00", "07:00", "08:00", "09:00", "10:00", "11:00",
                 "12:00", "13:00", "14:00", "15:00", "16:00", "17:00",
                 "18:00", "19:00", "20:00", "21:00", "22:00", "23:00"]
    
    for index, time_slot in enumerate(all_times):
        task_names = []  # 用于存储時間槽内的任務名稱列表
        for task in today_tasks:
            task_time = task.time.strftime('%H:%M')  # 將任務時間轉換為字符串格式
            if is_today(task.date) and task_time == time_slot:  # 判斷是否是今天的任務並且時間槽匹配
                task_names.append(task.task_name)

        # 如果該時間槽內沒有任務，則將任務名稱設為空
        if not task_names:
            task_names = [" "]  # 使用空字符串填充

        # 創建包含時間槽和任務名稱的任務框，並將其添加到時間表內容列表中
        task_box = create_task_box(time_slot, ", ".join(task_names), index)
        time_schedule_contents.append(task_box)

    return time_schedule_contents

def sendTimeBox(event):
    try:
        today_tasks = Task.objects.filter(date=date.today())  # 获取今天的任务列表
        if not today_tasks:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text='今天没有任务'))
            return
        
        message = TextSendMessage(text='以下是今天的任務時間表')
        time_schedule_contents = create_time_schedule(today_tasks)
        message2 = FlexSendMessage(
            alt_text='時間箱',
            contents={
                "type": "bubble",
                "size": "mega",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": time_schedule_contents
                }
            }
        )
        line_bot_api.reply_message(event.reply_token, [message, message2])

    except Exception as e:
        print(f"Error sending mission: {e}")
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='发生错误！'))
###冒險故事
chapter = ["要給他紅蘿菠嗎？"]
def sendStory(event):
    try:
        # 快速回覆按鈕
        message = TextSendMessage(
           text='點擊下方按鈕選擇想看的章節吧！\n(如未達到特定等級將無法觀看後續內容)',
        quick_reply=QuickReply(items=[
                QuickReplyButton(action=PostbackAction(label="第一章", text="第一章",data='action=第一章')),
                QuickReplyButton(action=PostbackAction(label="第二章", text="第二章",data='action=第二章')),
                QuickReplyButton(action=PostbackAction(label="第三章", text="第三章",data='action=第三章')),
                QuickReplyButton(action=PostbackAction(label="第四章", text="第四章",data='action=第四章')),
                QuickReplyButton(action=PostbackAction(label="第五章", text="第五章",data='action=第五章')),
            ]))
        # 發送消息
        line_bot_api.reply_message(event.reply_token,message)

    except:
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text='不'))
        
def sendback_1(event, backdata):  
    try:
       text1 = TextSendMessage(text='<第一章> - 收服夥伴吧！')
       text2 = TextSendMessage(text='離開了新手村，首先映入眼簾的是一隻奇怪的兔子，他看起來肚子很餓，苦苦哀求的看著你...')
       # 圖片
       image_url = "https://png.pngtree.com/png-vector/20221222/ourmid/pngtree-super-cute-cartoon-vector-bear-png-image_6504049.png"
       image_message = ImageSendMessage(original_content_url=image_url, preview_image_url=image_url)
   
       flex_message = FlexSendMessage(
           alt_text='今日任務',
           contents=generate_carousel2(chapter) # 生成包含多個任務的 Carousel Flex Message
       )

       line_bot_api.reply_message(event.reply_token, [text1, text2, image_message, flex_message])

    except:
       line_bot_api.reply_message(event.reply_token,TextSendMessage(text='不'))

###成就列表
def sendList(event):
    try:
        
        List = FlexSendMessage(
            alt_text='時間箱',
            contents={
              "type": "bubble",
              "hero": {
                "type": "image",
                "url": "https://scdn.line-apps.com/n/channel_devcenter/img/fx/01_1_cafe.png",
                "size": "full",
                "aspectRatio": "20:13",
                "aspectMode": "cover",
                "action": {
                  "type": "uri",
                  "uri": "http://linecorp.com/"
                }
              },
              "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                  {
                    "type": "text",
                    "text": "使用者名稱",
                    "weight": "bold",
                    "size": "md"
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
                            "text": "等級",
                            "size": "sm",
                            "flex": 2
                          },
                          {
                            "type": "text",
                            "text": "1",
                            "wrap": True,
                            "color": "#666666",
                            "size": "sm",
                            "flex": 3
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
                            "text": "經驗值",
                            "size": "sm",
                            "flex": 2
                          },
                          {
                            "type": "text",
                            "text": "20%",
                            "wrap": True,
                            "color": "#666666",
                            "size": "sm",
                            "flex": 3
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
                            "text": "連續天數",
                            "size": "sm",
                            "flex": 2
                          },
                          {
                            "type": "text",
                            "text": "10",
                            "wrap": True,
                            "color": "#666666",
                            "size": "sm",
                            "flex": 3
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
                      "type": "uri",
                      "label": "道具一覽",
                      "uri": "https://liff.line.me/2002705912-1B8eQdAx"
                    }
                  },
                  {
                    "type": "button",
                    "style": "link",
                    "height": "sm",
                    "action": {
                      "type": "uri",
                      "label": "角色圖鑑",
                      "uri": "https://liff.line.me/2002705912-bXP7OwR0"
                    }
                  }
                ],
                "flex": 0
              }
            }
        )
        line_bot_api.reply_message(event.reply_token, List)

    except:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='發生錯誤！'))
        
###LIFF回傳
# def manageForm(event, mtext):
#     try:
#         flist = mtext[3:].split('/')
#         task_name = flist[0]
#         task_date = flist[1]
#         task_time = flist[2]
#         task_category = flist[3]
#         task_id = Task.objects.count() + 1
#         formatted_time = datetime.strptime(task_time, '%H:%M').strftime('%H:%M:%S')
#         unit = Task.objects.create(tid=task_id,task_name=task_name,date=task_date,time=task_time,category=task_category)
#         unit.save()
        
#         #Flex Message
#         flex_message = {
#             "type": "carousel",
#             "contents": [
#                 {
#                     "type": "bubble",
#                     "size": "kilo",
#                     "header": {
#                         "type": "box",
#                         "layout": "vertical",
#                         "contents": [
#                             {
#                                 "type": "text",
#                                 "text": "- 新增任務 -",
#                                 "color": "#434343",
#                                 "align": "center",
#                                 "size": "md",
#                                 "gravity": "center",
#                                 "weight": "bold"
#                             }
#                         ],
#                         "backgroundColor": "#FFF1B8",
#                         "paddingTop": "19px",
#                         "paddingAll": "12px",
#                         "paddingBottom": "16px",
#                         "spacing": "none"
#                     },
#                     "body": {
#                         "type": "box",
#                         "layout": "vertical",
#                         "contents": [
#                             {
#                                 "type": "box",
#                                 "layout": "vertical",
#                                 "contents": [
#                                     {
#                                         "type": "text",
#                                         "text": f"任務名稱：{task_name}",
#                                         "color": "#434343",
#                                         "size": "md",
#                                         "wrap": True,
#                                         "weight": "regular"
#                                     }
#                                 ],
#                                 "flex": 1
#                             },
#                             {
#                                 "type": "box",
#                                 "layout": "vertical",
#                                 "contents": [
#                                     {
#                                         "type": "text",
#                                         "text": f"日期：{task_date}",
#                                         "color": "#434343",
#                                         "size": "sm",
#                                         "wrap": True
#                                     }
#                                 ],
#                                 "flex": 1
#                             },
#                             {
#                                 "type": "box",
#                                 "layout": "vertical",
#                                 "contents": [
#                                     {
#                                         "type": "text",
#                                         "text": f"預計執行時間：{task_time}",
#                                         "color": "#434343",
#                                         "size": "sm",
#                                         "wrap": True
#                                     }
#                                 ],
#                                 "flex": 1
#                             },
#                             {
#                                 "type": "box",
#                                 "layout": "vertical",
#                                 "contents": [
#                                     {
#                                         "type": "text",
#                                         "text": f"類別：{task_category}",
#                                         "color": "#434343",
#                                         "size": "sm",
#                                         "wrap": True
#                                     }
#                                 ],
#                                 "flex": 1
#                             },
#                             {
#                                 "type": "button",
#                                 "action": {
#                                     "type": "message",
#                                     "label": "修改",
#                                     "text": "hello"
#                                 },
#                                 "margin": "xs"
#                             }
#                         ],
#                         "spacing": "sm",
#                         "paddingAll": "12px",
#                         "margin": "none"
#                     },
#                     "styles": {
#                         "footer": {
#                             "separator": False
#                         }
#                     }
#                 }
#             ]
#         }
#         line_bot_api.reply_message(event.reply_token, [ FlexSendMessage(alt_text="新增任務", contents=flex_message)])
        
#     except Exception as e:
#         print(f"Error saving task: {e}")
#         line_bot_api.reply_message(event.reply_token,TextSendMessage(text='發生錯誤！'))   

def create_task(event, mtext):
    try:
        # 在这里处理 LIFF 发送的消息
        # 从 LIFF 发送的消息中获取任务的相关信息
        task_name = mtext['task']
        task_date = mtext['date']
        task_time = mtext['time']
        task_category = mtext['category']

        # 创建任务对象
        task_id = Task.objects.count() + 1
        unit = Task.objects.create(tid=task_id,task_name=task_name,date=task_date,time=task_time,category=task_category)
        unit.save()

        # 创建回复消息内容
        message = f"您添加的任务信息如下：\n任务名称：{task_name}\n日期：{task_date}\n时间：{task_time}\n类别：{task_category}"

        # 使用 Line Bot API 发送消息给用户
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=message))
        
    except Exception as e:
        print(f"Error saving task: {e}")
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='发生错误！'))