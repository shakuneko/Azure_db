from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
# Create your views here.

def sayhello(request):
    return HttpResponse("Hello Django")