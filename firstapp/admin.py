from django.contrib import admin
from firstapp.models import users,Task,Gift,UserGift,CompletedTask,UserLevel


class usersAdmin(admin.ModelAdmin):
    list_display=('uid','datatest','created_time','experience','level','reward_claimed','nickname','image_url')
admin.site.register(users, usersAdmin)
# Register your models here.

class TaskAdmin(admin.ModelAdmin):
    list_display=('tid','task_name','time','date','category','completed')
admin.site.register(Task, TaskAdmin)

class GiftAdmin(admin.ModelAdmin):
    list_display=('giftname','image_url','description')
admin.site.register(Gift, GiftAdmin)

class UserGiftAdmin(admin.ModelAdmin):
    list_display=('user','gift','created_at','image_url','description')
admin.site.register(UserGift, UserGiftAdmin)

class CompletedTaskAdmin(admin.ModelAdmin):
    list_display=('user_id','task_id')
admin.site.register(CompletedTask, CompletedTaskAdmin)

class UserLevelAdmin(admin.ModelAdmin):
    list_display=('level','image_url')
admin.site.register(UserLevel, UserLevelAdmin)