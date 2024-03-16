from django.conf import settings

from linebot import LineBotApi
from linebot.models import *
from linebot.models import ConfirmTemplate, PostbackTemplateAction, URITemplateAction
from linebot.models import TextSendMessage,ImageSendMessage,StickerSendMessage,LocationSendMessage,QuickReply,QuickReplyButton,MessageAction
from linebot.models import FlexSendMessage,TemplateSendMessage,ButtonsTemplate, PostbackTemplateAction
from linebot.models.flex_message import (
    BubbleContainer, ImageComponent,BoxComponent,
)
from firstapp.models import users
from firstapp.models import booking
from linebot.models.actions import URIAction
line_bot_api = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)

ex = {"FUTURE":"400",
      "刀鋒劍客":"280",
      "樂透大作戰":"270",
      "心裏美":"300",
      "拆彈倒數30分鐘":"280",
        }
###Carousel 是一種顯示多個 Bubble（氣泡）的方式，產生多個圖表來存放任務
def generate_carousel(tasks):
    bubbles = []
    for task in tasks:
        bubble = {
            "type": "bubble",
            "direction": "ltr",
            "header": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {"type": "text", "text": task, "weight": "bold", "size": "xl"},
                ]
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {"type": "separator", "margin": "md"}
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
                        "action": {"type": "postback", "label": "完成", "data": "action=completed"}
                    },
                    {
                        "type": "button",
                        "color": "#496496",
                        "action": {"type": "postback", "label": "刪除", "data": "action=incomplete"}
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
# 假設 tasks 是一個包含多個任務名稱的列表
tasks = ["任務1", "任務2", "任務3"]
def sendMission(event):
    try:
        message = TextSendMessage(
            text='以下是今日任務',
           )
        flex_message = FlexSendMessage(
            alt_text='今日任務',
            contents=generate_carousel(tasks) # 生成包含多個任務的 Carousel Flex Message
        )

        line_bot_api.reply_message(event.reply_token,[message,  flex_message])
        
    except:
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text='不'))
        
def handle_postback(event):
    if event.postback.data == 'action=completed':
        message1 = TextSendMessage(text='恭喜！又完成一項任務啦～\n繼續努力吧！')
        message2 = FlexSendMessage(
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
                    "text": "20%",
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
                        "width": "20%",
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
        line_bot_api.reply_message(event.reply_token, [message1, message2])
    
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



def create_time_schedule(tasks):
    time_schedule_contents = []
    for index, (start_time, task_name) in enumerate(tasks):
        task_box = create_task_box(start_time, task_name, index)
        time_schedule_contents.append(task_box)
    return time_schedule_contents

def sendTimeBox(event):
    try:
        tasks = [("06:00", "任務1"), ("07:00", "任務2"), ("08:00", " "), ("09:00", "任務2"), ("10:00", "任務2"), ("11:00", "任務2"),
                 ("12:00", " "), ("13:00", " "), ("14:00", " "), ("15:00", " "), ("16:00", " "), ("17:00", " "),
                 ("18:00", " "), ("19:00", " "), ("20:00", " "), ("21:00", " "), ("22:00", " "), ("23:00", " "), ("24:00", " ")
                 
                 ]  # 示例任務列表
        message = TextSendMessage(text='以下是今日任務時間表')
        time_schedule_contents = create_time_schedule(tasks)
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

    except:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='發生錯誤！'))
        
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
        
def manageForm(event, mtext, user_id):
    try:
        flist = mtext[3:].split('/')
        exhibittype = flist[0]
        amount = flist[1]
        money = ex[exhibittype]
        
        unit = booking.objects.create(bid=user_id,exhibittype=exhibittype,exhibitamount=amount,money=money)
        unit.save()
        
        total = int(money)*int(amount)
        
        text1 = "訂票成功，資料如下："
        text1 += "\n 名稱：" + exhibittype
        text1 += "\n 票數：" + amount
        text1 += "\n 單價：" + money
        text1 += "\n 總價：" + str(total)
        message = TextSendMessage(
            text = text1
        )
        line_bot_api.reply_message(event.reply_token,message)
        
    except:
        line_bot_api.reply_message(event.reply_token,TextSendMessage(text='結帳錯誤'))   