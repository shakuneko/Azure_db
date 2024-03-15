from django.contrib import admin
from django.urls import path, include
from firstapp.views import sayhello 

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', sayhello),
   # path('', include('azure_content.urls')),
]
