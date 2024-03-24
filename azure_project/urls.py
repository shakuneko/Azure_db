from django.contrib import admin
from django.urls import path, include, re_path
from firstapp import views
from firstapp.views import sayhello 

urlpatterns = [
    re_path(r'^callback$',views.callback),
    path('admin/', admin.site.urls),
    path('', sayhello),
    path('api/tasks/', views.get_tasks, name='get_tasks'),
    path('api/items/', views.get_item, name='get_item'),
   # path('', include('azure_content.urls')),
]
