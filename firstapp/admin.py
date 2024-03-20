from django.contrib import admin
from firstapp.models import users
from firstapp.models import booking
from firstapp.models import Task
from firstapp.models import Gift
from firstapp.models import UserGift

class usersAdmin(admin.ModelAdmin):
    list_display=('uid','datatest','created_time')
admin.site.register(users, usersAdmin)
# Register your models here.
class bookingAdmin(admin.ModelAdmin):
    list_display=('bid','datatest','exhibittype','exhibitamount','money','which_date','which_time')
admin.site.register(booking, bookingAdmin)

class TaskAdmin(admin.ModelAdmin):
    list_display=('tid','task_name','time','date','category')
admin.site.register(Task, TaskAdmin)

class GiftAdmin(admin.ModelAdmin):
    list_display=('giftname','image_url')
admin.site.register(Gift, GiftAdmin)

class UserGiftAdmin(admin.ModelAdmin):
    list_display=('user','gift','created_at')
admin.site.register(UserGift, UserGiftAdmin)