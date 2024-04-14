from django.conf import settings

from linebot import LineBotApi
from linebot.models import *
from linebot.models import ConfirmTemplate, PostbackTemplateAction, URITemplateAction
from linebot.models import TextSendMessage,ImageSendMessage,StickerSendMessage,LocationSendMessage,QuickReply,QuickReplyButton,MessageAction
from linebot.models import FlexSendMessage,TemplateSendMessage,ButtonsTemplate, PostbackTemplateAction
from linebot.models.flex_message import (
    BubbleContainer, ImageComponent,BoxComponent,
)
from firstapp.models import users,Task,Gift,UserGift,CompletedTask,UserLevel
from linebot.models.actions import URIAction
from datetime import datetime,date,timedelta
import random
from django.core.exceptions import ObjectDoesNotExist
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
                        "data": "action=incompleted"+ task.tid
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
# def load_completed_tasks():
#     # 從數據庫中加載已完成的任務ID
#     completed_tasks = set(CompletedTask.objects.values_list('task_id', flat=True))
#     return completed_tasks

def sendMission(event):
    try:
        tasks = Task.objects.filter(date=date.today(), completed=False)  # 获取今天未完成的任务
        if tasks:
            message = TextSendMessage(
                text='以下是今日任務',
            )
            flex_message = FlexSendMessage(
                alt_text='今日任務',
                contents=generate_carousel(tasks)
            )
            line_bot_api.reply_message(event.reply_token, [message, flex_message])
        else:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text='目前沒有需要處理的任務'))
    except Exception as e:
        print(f"Error sending mission: {e}")
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='發生錯誤！'))

###完成任務獎勵
def handle_postback(event):
    postback_data = event.postback.data
    if postback_data.startswith('action=completed'):
        task_id = postback_data.split('&')[1].split('=')[1]
        try:
            task = Task.objects.get(tid=task_id)
            user_id = event.source.user_id  
            user = users.objects.get(uid=user_id)  
            if not task.completed:  # 检查任务是否已经完成
                task.completed = True
                task.save()
                experience_gained = 20
                update_experience(user, experience_gained)  # 更新用户的经验值
                experience_newpercentage = user.experience  # 获取用户当前的经验值百分比
                level = user.level
                # 隨機恭喜句子
                congrats_messages = [
                    '恭喜！又完成一項任務啦～\n繼續努力吧！',
                    '加油！快要升等了',
                    '恭喜完成任務！'
                ]
                congrats_message = random.choice(congrats_messages)

                if user.level > 1 and user.experience == 0:
                    message = f'恭喜！升级到 {user.level}等了！\n快到成就列表查看狀態吧！'
                    image_url = user.image_url  # 新的级别图片URL
                    flex_message = generate_level_up_message(message, image_url)
                    message2 = generate_experience_message(user,experience_newpercentage, level)
                    line_bot_api.reply_message(event.reply_token, [flex_message,message2])
                else:
                    message1 = TextSendMessage(text=congrats_message)
                    message2 = generate_experience_message(user,experience_newpercentage, level)
                    line_bot_api.reply_message(event.reply_token, [message1, message2])
                    
                completed_task_count = Task.objects.filter(completed=True).count()
                if completed_task_count >= 3 and not user.reward_claimed:
                    handle_all_tasks_completed(event.source.user_id)
                    # 更新用户已领取奖励的标志
                    user.reward_claimed = True
                    user.save()
                        
            else:
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text='該任務已經完成過了！'))
        except Task.DoesNotExist:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text='發生錯誤'))
    elif postback_data.startswith('action=open_treasure_box'):
        get_gift(event)
    #刪除任務
    elif postback_data.startswith('action=incompleted'):
        task_id = postback_data.split('action=incompleted')[1] 
        try:
            task = Task.objects.get(tid=task_id)
            if task.completed:
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text='該任務已經完成，無法刪除！'))
            else:
                task.delete()
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text='任務已刪除！'))
        except Task.DoesNotExist:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text='任務不存在'))
def handle_all_tasks_completed(user_id):
    # 在這裡添加您希望在所有任務完成時執行的代碼
    text1 = TextSendMessage(text='\ 今天完成了三項任務 / \n點選寶箱來領取獎勵吧！')
    flex_message = {
        "type": "bubble",
        "hero": {
            "type": "image",
            "url": "https://imgur.com/luxUvdb.png",
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
    user_gift_url = set(user_gift.gift.image_url for user_gift in user_gifts)
    # 获取所有礼物，并排除用户已经获得的礼物
    available_gifts = Gift.objects.exclude(giftname__in=user_gift_names)

    # 如果还有可用的礼物
    if available_gifts.exists():
        # 从剩余的礼物中随机选择一个
        selected_gift = random.choice(available_gifts)
        # 创建一个 UserGift 实例，将其与用户关联并保存到数据库中
        user_gift = UserGift.objects.create(user=event.source.user_id, gift=selected_gift,image_url=selected_gift.image_url,description=selected_gift.description)
        user_gift.save()
        # 更新用戶的reward_claimed屬性為True，表示用戶已經領取了獎勵
        user = users.objects.get(uid=event.source.user_id)
        user.reward_claimed = True
        user.save()
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
                "aspectMode": "cover",
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "separator",
                        "margin": "md"
                    },
                    {
                        "type": "text",
                        "text": f"道具說明:\n {selected_gift.description}",
                        "margin": "md",
                        "wrap": True  # 啟用文字自動換行功能
                    }
                ]
            },
            "footer": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "filler"
                    }
                ],
                "backgroundColor": "#FFFFFF",
                "paddingAll": "10px" 
            }
        }

        # 回复用户
        line_bot_api.reply_message(event.reply_token, FlexSendMessage(alt_text="獲得禮物", contents=flex_message))
    else:
        # 如果所有礼物都已经被用户获得，向用户发送消息提示
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="您已經獲得了所有可用的禮物！"))
# def calculate_experience_percentage(completed_tasks):
#     # 根據完成的任務數量計算經驗值增加的百分比
#     # 這裡可以根據你的需求設定不同的增加規則
#     # 以下是一個簡單的範例
#     if completed_tasks <= 10:
#         return completed_tasks * 10  # 每完成一個任務增加10%
#     else:
#         return 100  # 最多增加到100%

#判斷經驗值
def update_experience(user, experience_gained):
    user.experience += experience_gained
    if user.experience >= 100:  # 假设达到100经验值时升级
        user.level += 1
        user.experience = user.experience % 100  # 减去升级所需的经验值

        # 更新等級照片
        new_level_image_url = UserLevel.objects.get(level=user.level).image_url
        user.image_url = new_level_image_url

    user.save()
def generate_level_up_message(message, image_url):
    # 生成包含升级信息和图片的 Flex Message
    return FlexSendMessage(
        alt_text='升级通知',
        contents={
            "type": "bubble",
            "hero": {
                "type": "image",
                "url": image_url,
                "size": "full",
                "aspectRatio": "1:1",
                "aspectMode": "cover"
            },

            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": message,
                        "size": "lg",
                        "align": "center",
                        "margin": "none",
                        "wrap": True
                    }
                ]
            }
        }
    )
def generate_experience_message(user,experience_newpercentage,level):
     #  根據等級變換進度條顏色
    if level == 1:
        progress_bar_color = "#BFBFBF"  # 灰色
        background_color = "#F0F0F0"
        
    elif level == 2:
        progress_bar_color = "#597EF7"  # 蓝色
        background_color = "#D6E4FF" 
        
    else:
        progress_bar_color = "#FFD666"  # 黃色
        background_color = "#FFFAE3" 

    # 生成經驗值計算的 Flex Message
    return FlexSendMessage(
        alt_text='獲得經驗值',
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
                        "type": "box",
                        "layout": "horizontal",
                        "contents": [
                        {
                            "type": "text",
                            "text": f"Lv {level}"
                        },
                        {
                            "type": "text",
                        "text": f"{experience_newpercentage}/100",
                        "margin": "lg",
                        "size": "md",
                        "align": "end"
                        }
                        ],
                         "margin": "md"
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {
                                "type": "box",
                                "layout": "vertical",
                                "contents": [],
                                "width": f"{experience_newpercentage}%",
                                "backgroundColor": progress_bar_color,
                                "height": "15px",
                                "cornerRadius": "10px"
                            }
                        ],
                        "margin": "md",
                        "backgroundColor": background_color,
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
def create_time_schedule(date_range):
    all_times = ["06:00", "07:00", "08:00", "09:00", "10:00", "11:00",
                 "12:00", "13:00", "14:00", "15:00", "16:00", "17:00",
                 "18:00", "19:00", "20:00", "21:00", "22:00", "23:00"]
    
    time_schedule_contents = []

    for date_to_display in date_range:
        today_tasks = Task.objects.filter(date=date_to_display)
        task_boxes = []

        for index, time_slot in enumerate(all_times):
            task_names = []  # 用于存储时间槽内的任务名称列表
            for task in today_tasks:
                task_time = task.time.strftime('%H:%M')  # 将任务时间转换为字符串格式
                if task_time == time_slot:  # 判断时间槽匹配
                    task_names.append(task.task_name)

            # 如果该时间槽内没有任务，将任务名称设置为空字符串
            if not task_names:
                task_names = [" "]  # 使用空字符串填充

            # 创建包含时间槽和任务名称的任务框，并添加到任务框列表中
            task_box = create_task_box(time_slot, ", ".join(task_names), index)
            task_boxes.append(task_box)

        # 将当前日期的任务框列表添加到总的时间表内容列表中
        time_schedule_contents.append(task_boxes)

    return time_schedule_contents

def sendTimeBox(event):
    try:
        today = date.today()  # 获取今天日期
        three_days_later = today + timedelta(days=2)  # 获取三天后的日期
        date_range = [today + timedelta(days=i) for i in range(3)]  # 构建日期范围列表

        # 自定义英文星期到中文星期的转换
        day_mapping = {
            "Mon": "一",
            "Tue": "二",
            "Wed": "三",
            "Thu": "四",
            "Fri": "五",
            "Sat": "六",
            "Sun": "日"
        }

        # 发送任务时间表的 FlexMessage
        time_schedule_contents = create_time_schedule(date_range)
        carousel_contents = []
        for idx, task_boxes in enumerate(time_schedule_contents):
            date_to_display = date_range[idx]
            # 获取中文星期的表示
            week_day_cn = day_mapping.get(date_to_display.strftime("%a"), "")  # 根据星期简称获取中文星期表示
            date_display_text = date_to_display.strftime("%m/%d （%a）").replace(date_to_display.strftime("%a"), week_day_cn)  # 添加日期和星期（中文）
            
            bubble_content = {
                "type": "bubble",
                "size": "mega",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "box",
                            "layout": "horizontal",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": date_display_text,  # 添加日期和星期
                                    "gravity": "center",
                                    "size": "sm",
                                    "align": "center",
                                    "margin": "none"
                                }
                            ]
                        },
                        {
                            "type": "separator",  # 添加分隔线
                            "margin": "md"
                        },
                        *task_boxes  # 添加任务时间表的内容
                    ]
                }
            }
            carousel_contents.append(bubble_content)
        message = TextSendMessage(text='以下是近三天的任務時間表')
        flex_message = FlexSendMessage(
            alt_text='時間箱',
            contents={
                "type": "carousel",
                "contents": carousel_contents
            }
        )

        # 发送 FlexMessage
        line_bot_api.reply_message(event.reply_token, [message,flex_message])

    except Exception as e:
        print(f"Error sending mission: {e}")
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='發生錯誤！'))
###冒險故事
def sendStory(event):
    try:
        # 提示信息
        message = TextSendMessage(
            text='點擊下方按鈕選擇想看的章節吧！\n(如未達到特定等級將無法觀看後續內容)'
        )

        # 构建 Carousel Flex Message
        carousel_contents = [
            BubbleContainer(
                hero=ImageComponent(
                    type="image",
                    size="full",
                    aspect_ratio="20:13",
                    aspect_mode="cover",
                    url="https://imgur.com/rEGBUYT.png"
                ),
                footer=BoxComponent(
                    type="box",
                    layout="vertical",
                    spacing="sm",
                    contents=[
                        ButtonComponent(
                            type="button",
                            action=PostbackAction(
                                type="postback",
                                label="第一章",
                                data="action=第一章"
                            )
                        )
                    ]
                )
            ),
            BubbleContainer(
                hero=ImageComponent(
                    type="image",
                    size="full",
                    aspect_ratio="20:13",
                    aspect_mode="cover",
                    url="https://imgur.com/D2vpSnA.png"
                ),
                footer=BoxComponent(
                    type="box",
                    layout="vertical",
                    spacing="sm",
                    contents=[
                        ButtonComponent(
                            type="button",
                            action=PostbackAction(
                                type="postback",
                                label="第二章",
                                data="action=第二章"
                            )
                        )
                    ]
                )
            ),
            BubbleContainer(
                hero=ImageComponent(
                    type="image",
                    size="full",
                    aspect_ratio="20:13",
                    aspect_mode="cover",
                    url="https://imgur.com/D2vpSnA.png"
                ),
                footer=BoxComponent(
                    type="box",
                    layout="vertical",
                    spacing="sm",
                    contents=[
                        ButtonComponent(
                            type="button",
                            action=PostbackAction(
                                type="postback",
                                label="第三章",
                                data="action=第三章"
                            )
                        )
                    ]
                )
            )
        ]
        
        flex_message = FlexSendMessage(
            alt_text='章節選擇',
            contents=CarouselContainer(contents=carousel_contents)
        )

        # 发送提示信息和 FlexMessage
        line_bot_api.reply_message(event.reply_token, [message, flex_message])

    except Exception as e:
        print(f"Error sending story: {e}")
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='發生錯誤！'))
        
def sendback_1(event, backdata):  
    try:
       text1 = TextSendMessage(text='<第一章> - 冒險的開始！')
       text2 = TextSendMessage(text='離開了新手村，你來到了一片森林，聽說這裡充滿了各種危險，你做好準備前進下去了嗎？')
       #森林圖片
       image_url = "https://i.imgur.com/mXblhcp.png"
       image_message = ImageSendMessage(original_content_url=image_url, preview_image_url=image_url)
       flex_message1 = FlexSendMessage(
        alt_text='是否繼續',
        contents={
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "horizontal",
                "contents": [
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {
                                "type": "button",
                                "action": {
                                    "type": "message",
                                    "label": "繼續前進",
                                    "text": "我要繼續前進！"
                                },
                                "color": "#ffffff"
                            }
                        ],
                        "backgroundColor": "#597EF7",
                        "cornerRadius": "lg"
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {
                                "type": "button",
                                "action": {
                                    "type": "message",
                                    "label": "先不要好了",
                                    "text": "先不要好了"
                                }
                            }
                        ]
                    }
                ]
            }
        }
    )

    #    flex_message = FlexSendMessage(
    #        alt_text='今日任務',
    #        contents=generate_carousel2(chapter) # 生成包含多個任務的 Carousel Flex Message
    #    )

       line_bot_api.reply_message(event.reply_token, [text1, text2,image_message,flex_message1])

    except:
       line_bot_api.reply_message(event.reply_token,TextSendMessage(text='不'))

def sendback_2(event, backdata):  
    try:
       text = TextSendMessage(text='目前尚未解鎖該章節，3等後就能查看囉！')
       line_bot_api.reply_message(event.reply_token, [text])
    except:
       line_bot_api.reply_message(event.reply_token,TextSendMessage(text='不'))
#逃跑的回覆
def sendStoryBack(event, backdata):  
    try:
       text = TextSendMessage(text='回村莊蒐集道具後再來挑戰吧！')
       line_bot_api.reply_message(event.reply_token, [text])
    except:
       line_bot_api.reply_message(event.reply_token,TextSendMessage(text='不'))

def sendStoryNext(event, backdata): 
    try:
       text1 = TextSendMessage(text='突然，一隻看起來很餓的史萊姆出現在你的眼前，該怎麼做呢...')
       #肚子餓史萊姆
       image_url = "https://imgur.com/xG7uDJG.png"
       image_message = ImageSendMessage(original_content_url=image_url, preview_image_url=image_url)
       flex_message1 = FlexSendMessage(
        alt_text='是否使用道具',
        contents={
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "horizontal",
                "contents": [
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {
                                "type": "button",
                                "action": {
                                    "type": "message",
                                    "label": "使用道具",
                                    "text": "用看看道具好了"
                                },
                                "color": "#ffffff"
                            }
                        ],
                        "backgroundColor": "#597EF7",
                        "cornerRadius": "lg"
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {
                                "type": "button",
                                "action": {
                                    "type": "message",
                                    "label": "逃跑",
                                    "text": "逃跑"
                                }
                            }
                        ]
                    }
                ]
            }
        }
    )

   
    #    flex_message = FlexSendMessage(
    #        alt_text='今日任務',
    #        contents=generate_carousel2(chapter) # 生成包含多個任務的 Carousel Flex Message
    #    )

       line_bot_api.reply_message(event.reply_token, [text1,image_message,flex_message1])

    except Exception as e:
        print(f"Error saving task: {e}")
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text='不'))
def sendStoryUseItem(event, backdata): 
    try:
        user_id = event.source.user_id  
        user_gifts = UserGift.objects.filter(user=user_id) 
        
        bubbles = []
        for user_gift in user_gifts:
            bubble = {
                "type": "bubble",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "image",
                            "url": user_gift.image_url,
                            "size": "3xl"
                        },
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                                {
                                    "type": "text",
                                    "text": user_gift.gift.giftname,
                                    "weight": "bold",
                                    "size": "lg",
                                    "align": "center",
                                    "margin": "md"
                                }
                            ]
                        }
                    ]
                },
                "footer": {
                    "type": "box",
                    "layout": "vertical",
                    "spacing": "sm",
                    "contents": [
                        {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                                {
                                    "type": "button",
                                    "action": {
                                        "type": "message",
                                        "label": "使用",
                                        "text": f"使用{user_gift.gift.giftname}"  # 不同道具的標識
                                    },
                                    "color": "#ffffff"
                                }
                            ],
                            "backgroundColor": "#597EF7",
                            "cornerRadius": "md"
                        }
                    ],
                    "flex": 0
                }
            }
            bubbles.append(bubble)

        carousel = {
            "type": "carousel",
            "contents": bubbles
        }

        flex_message = FlexSendMessage(alt_text='是否使用道具', contents=carousel)

        line_bot_api.reply_message(event.reply_token, flex_message)
    except Exception as e:
        print(f"Error sending story use item message: {e}")
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="發生錯誤"))

def sendStoryItem(event):
    try:
        message = event.message.text
        gift_name = message.split("使用")[1].strip()  # 獲取道具名稱並去除前後空格
        user_id = event.source.user_id  
        user = users.objects.get(uid=user_id) 
        user_gifts = UserGift.objects.filter(user=user_id, gift__giftname=gift_name)  # 过滤出用户和指定礼物名称的 UserGift 对象
        if user_gifts.exists():
            for user_gift in user_gifts:
                user_gift.used_gift = True
                user_gift.save() 
            if gift_name == "謎之藥水":
                response_message = "你使用了謎之藥水，史萊姆的顏色逐漸變化了！"
                image_url = "https://imgur.com/DRtcDGW.png"  # 生氣史萊姆
                congratulation_message = "史萊姆生氣的攻擊了你，你的經驗值減少了5%。"
                # 扣除经验值
                experience_decrease = 5
                user.experience -= experience_decrease
                if user.experience <= 0:
                    user.level = 1
                    user.experience = 95
                    user.image_url = "https://i.imgur.com/Qk4cUGL.png"  # 将图片 URL 设置为 1 级对应的图片
                user.save()
                # 生成消息回覆
                messages = [
                    TextSendMessage(text=response_message),
                    ImageSendMessage(original_content_url=image_url, preview_image_url=image_url),
                    TextSendMessage(text=congratulation_message),
                    generate_experience_message(user, user.experience, user.level)  # 加入經驗值變化的 Flex Message
                ]
            elif gift_name == "軟綿綿果實":
                response_message = "你使用了軟綿綿果實，史萊姆對你的好感度增加了！"
                image_url = "https://imgur.com/Q7jNQtU.png"  # 開心史萊姆
                dislike_message = "史萊姆很開心，決定帶你繼續前進探索森林。"
            
                # 生成消息回覆
                messages = [
                    TextSendMessage(text=response_message),
                    ImageSendMessage(original_content_url=image_url, preview_image_url=image_url),
                    TextSendMessage(text=dislike_message)
                ]
            else:
                response_message = "你使用了未知的道具。"
                messages = [TextSendMessage(text=response_message)]

        line_bot_api.reply_message(event.reply_token, messages)
    except Exception as e:
        print(f"Error handling message: {e}")



###成就列表
def sendList(event):
    try:
        user_id = event.source.user_id  
        user = users.objects.get(uid=user_id)  

        List = FlexSendMessage(
            alt_text='成就列表',
            contents={
              "type": "bubble",
              "hero": {
                "type": "image",
                "url": user.image_url,
                "size": "full",
              },
              "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                  {
                    "type": "text",
                    "text": user.nickname,
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
                            "text": str(user.level),
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
                            "text": f"{user.experience}%",
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
                            "text": "1",
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
                      "label": "統計圖表",
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
def manageForm(event, mtext):
    try:
        flist = mtext[3:].split('/')
        task_name = flist[0]
        task_date = flist[1]
        task_time = flist[2]
        task_category = flist[3]
        task_id = Task.objects.count() + 1
        formatted_time = datetime.strptime(task_time, '%H:%M').strftime('%H:%M:%S')
        unit = Task.objects.create(tid=task_id,task_name=task_name,date=task_date,time=task_time,category=task_category)
        unit.save()
        
        #Flex Message
        flex_message = {
            "type": "carousel",
            "contents": [
                {
                    "type": "bubble",
                    "size": "kilo",
                    "header": {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {
                                "type": "text",
                                "text": "- 新增任務 -",
                                "color": "#434343",
                                "align": "center",
                                "size": "md",
                                "gravity": "center",
                                "weight": "bold"
                            }
                        ],
                        "backgroundColor": "#FFF1B8",
                        "paddingTop": "19px",
                        "paddingAll": "12px",
                        "paddingBottom": "16px",
                        "spacing": "none"
                    },
                    "body": {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {
                                "type": "box",
                                "layout": "vertical",
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": f"任務名稱：{task_name}",
                                        "color": "#434343",
                                        "size": "md",
                                        "wrap": True,
                                        "weight": "regular"
                                    }
                                ],
                                "flex": 1
                            },
                            {
                                "type": "box",
                                "layout": "vertical",
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": f"日期：{task_date}",
                                        "color": "#434343",
                                        "size": "sm",
                                        "wrap": True
                                    }
                                ],
                                "flex": 1
                            },
                            {
                                "type": "box",
                                "layout": "vertical",
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": f"預計執行時間：{task_time}",
                                        "color": "#434343",
                                        "size": "sm",
                                        "wrap": True
                                    }
                                ],
                                "flex": 1
                            },
                            {
                                "type": "box",
                                "layout": "vertical",
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": f"類別：{task_category}",
                                        "color": "#434343",
                                        "size": "sm",
                                        "wrap": True
                                    }
                                ],
                                "flex": 1
                            },
                            {
                                "type": "button",
                                "action": {
                                    "type": "postback",
                                    "label": "修改",
                                    "data": "action=nothing" 
                                },
                            }
                        ],
                        "spacing": "sm",
                        "paddingAll": "12px",
                        "margin": "none"
                    },
                    "styles": {
                        "footer": {
                            "separator": False
                        }
                    }
                }
            ]
        }
        line_bot_api.reply_message(event.reply_token, [ FlexSendMessage(alt_text="新增任務", contents=flex_message)])
        
    except Exception as e:
        print(f"Error saving task: {e}")
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text='發生錯誤！'))   

def sendUsername(event):
    try:
        user_id = event.source.user_id
        user = users.objects.get(uid=user_id)
        first_level_image_url = UserLevel.objects.get(level=1).image_url
        user.image_url = first_level_image_url
        user.save()
        message = TextSendMessage(text='好的！請以下列格式輸入想要的暱稱“我想叫XXX”')
      
        line_bot_api.reply_message(event.reply_token, [message])

    except Exception as e:
        print(f"Error sending mission: {e}")
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='发生错误！'))

#圖片選轉木馬
def generate_carousel_teach(images):
    carousel_contents = []
    for image_url in images:
        bubble = {
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "image",
                        "url": image_url,
                        "size": "full",
                        "aspectMode": "cover",
                        "aspectRatio": "2:3",
                        "gravity": "top"
                    }
                ],
                "paddingAll": "0px"
            }
        }
        carousel_contents.append(bubble)
    carousel = {
        "type": "carousel",
        "contents": carousel_contents
    }
    return carousel

def sendnickname(event,mtext):
    try:
        user_id = event.source.user_id
        # 检查用户是否存在，如果不存在则创建用户
        if not users.objects.filter(uid=user_id).exists():
            user = users.objects.create(uid=user_id, nickname='')  # 初始化 nickname 为空字符串
        else:
            user = users.objects.get(uid=user_id)
        
        # 在这里保存暱稱到用户对象中
        nickname = mtext[3:].strip()  # 取得使用者輸入的暱稱部分，并移除首尾空格
        user.nickname = nickname
        user.save()
        reply_message = TextSendMessage(text=f'好的，{nickname}\n那麼接下來要進入新手教學的部分，如果看完有不懂的地方或是忘記的話，隨時點擊“新手教學”我就會再教你一次喔！')
        images = [
            "https://imgur.com/omfjK8F.png", #新增任務
            "https://imgur.com/CxCBlkx.png", #今日任務
            "https://imgur.com/wAVX9EM.png",
            "https://imgur.com/ZVNUmFq.png", #時間箱
            "https://imgur.com/rzmXlT5.png", #冒險故事
            "https://imgur.com/7bx9lnV.png", #成就列表
            "https://imgur.com/E87ArXO.png",
            "https://imgur.com/ho538O6.png", #推播功能
        ]
        carousel_message = generate_carousel_teach(images)
        flex_message_object = FlexSendMessage(alt_text="新手教學", contents=carousel_message)
        line_bot_api.reply_message(event.reply_token, [reply_message, flex_message_object])
    except Exception as e:
        print(f"Error sending mission: {e}")
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='发生错误！'))
###新手教學
def sendTeach(event):
    try:
        images = [
            "https://imgur.com/omfjK8F.png", #新增任務
            "https://imgur.com/CxCBlkx.png", #今日任務
            "https://imgur.com/wAVX9EM.png",
            "https://imgur.com/ZVNUmFq.png", #時間箱
            "https://imgur.com/rzmXlT5.png", #冒險故事
            "https://imgur.com/7bx9lnV.png", #成就列表
            "https://imgur.com/E87ArXO.png",
            "https://imgur.com/ho538O6.png", #推播功能
        ]
        carousel_message = generate_carousel_teach(images)
        flex_message_object = FlexSendMessage(alt_text="新手教學", contents=carousel_message)
        line_bot_api.reply_message(event.reply_token, [flex_message_object])
    except Exception as e:
        print(f"Error sending mission: {e}")
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='发生错误！'))

 ###自我回顧
def sendReview(event):
    try:
        user_id = event.source.user_id  
        user = users.objects.get(uid=user_id)  

        List = FlexSendMessage(
            alt_text='自我回顧',
            contents={
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                {
                    "type": "text",
                    "text": "自我回顧",
                    "weight": "bold",
                    "size": "xl"
                },
                {
                    "type": "text",
                    "text": "一天又過去了，有好好完成該做的事情嗎？",
                    "size": "xs",
                    "margin": "lg"
                }
                ]
            },
            "footer": {
                "type": "box",
                "layout": "vertical",
                "spacing": "sm",
                "contents": [
                {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                    {
                        "type": "button",
                        "action": {
                        "type": "postback",
                        "label": "今天有把該做的事都做完",
                        "data": "hello"
                        },
                        "color": "#434343"
                    }
                    ],
                    "margin": "sm",
                    "backgroundColor": "#ADC6FF",
                    "cornerRadius": "10px"
                },
                {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                    {
                        "type": "button",
                        "action": {
                        "type": "postback",
                        "label": "差一點點就全部完成了",
                        "data": "hello"
                        },
                        "color": "#434343"
                    }
                    ],
                    "margin": "md",
                    "backgroundColor": "#FFE58F",
                    "cornerRadius": "10px"
                },
                {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                    {
                        "type": "button",
                        "action": {
                        "type": "postback",
                        "label": "今天的進度跟想像中有點落差...",
                        "data": "hello"
                        },
                        "color": "#434343"
                    }
                    ],
                    "margin": "md",
                    "backgroundColor": "#ADC6FF",
                    "cornerRadius": "10px"
                },
                {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                    {
                        "type": "button",
                        "action": {
                        "type": "postback",
                        "label": "放縱了自己一天...明天再努力吧",
                        "data": "hello"
                        },
                        "color": "#434343"
                    }
                    ],
                    "margin": "md",
                    "backgroundColor": "#FFE58F",
                    "cornerRadius": "10px"
                }
                ],
                "flex": 0
            }
        }
        )
        line_bot_api.reply_message(event.reply_token, List)

    except Exception as e:
        print(f"Error sending mission: {e}")
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='發生錯誤！'))

###任務整理
def sendLeftList(event):
    try:
        text = TextSendMessage(text='昨天還遺留了一些任務...\n今天還要繼續完成嗎？')
        List = FlexSendMessage(
            alt_text='任務整理',
            contents={
                "type": "bubble",
                "size": "hecto",
                "header": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                    {
                        "type": "text",
                        "text": "準備考試",
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
                        "text": "學校"
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
                        "type": "message",
                        "label": "繼續",
                        "text": "當然要繼續啊！"
                        },
                        "color": "#597EF7"
                    },
                    {
                        "type": "button",
                        "action": {
                        "type": "message",
                        "label": "捨棄",
                        "text": "捨棄"
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
        )
        line_bot_api.reply_message(event.reply_token, [text,List])

    except Exception as e:
        print(f"Error sending mission: {e}")
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='發生錯誤！'))

def sendContinue(event):  
    try:
       text = TextSendMessage(text='已添加入今日清單，今天繼續努力吧！')
       line_bot_api.reply_message(event.reply_token, [text])
    except:
       line_bot_api.reply_message(event.reply_token,TextSendMessage(text='不'))

def sendLeft(event):  
    try:
       text = TextSendMessage(text='已刪除該任務！')
       line_bot_api.reply_message(event.reply_token, [text])
    except:
       line_bot_api.reply_message(event.reply_token,TextSendMessage(text='不'))

