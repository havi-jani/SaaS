from django.shortcuts import render , HttpResponse 
from saasapp.models import *

# Decoraters
from django.contrib.auth.decorators import login_required

# Create your views here.
from django.views.decorators.csrf import csrf_protect


@csrf_protect


@login_required()
def homepage(req):
    # PageVisits.objects.create()
    data = PageVisits.objects.all()
    msg = "Welcome to Home Page"

    name = req.POST
    return render(req , 'index.html' , context={
        'msg' : msg,
        'count' : data.count()
    })

