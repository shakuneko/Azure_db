from django.contrib import admin
from firstapp.models import users
from firstapp.models import booking
from firstapp.models import Task

class usersAdmin(admin.ModelAdmin):
    list_display=('uid','datatest','created_time')
admin.site.register(users, usersAdmin)
# Register your models here.
class bookingAdmin(admin.ModelAdmin):
    list_display=('bid','datatest','exhibittype','exhibitamount','money','which_date','which_time')
admin.site.register(booking, bookingAdmin)

class TaskAdmin(admin.ModelAdmin):
    list_display=('task_name','time','date','category')
admin.site.register(Task, TaskAdmin)
