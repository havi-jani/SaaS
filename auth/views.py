from django.contrib.auth import authenticate , login
from django.shortcuts import render , redirect
from django.contrib.auth import get_user_model

User = get_user_model()

# Create your views here.

def loginView(req):
    if req.method == 'POST':
        
        username = req.POST.get('name') or None
        password = req.POST.get('pass') or None

        if all([username , password]):
            user = authenticate(req , username=username, password=password)

            if user is not None:
                login(req , user)
                print("Login Here")
                return redirect('/')
        else:
            return render(req, 'auth/login.html' , {})
    return render(req, 'auth/login.html' , {})


def registerView(req):

    if req.method == 'POST':
        username = req.POST.get('name') or None
        email = req.POST.get('email') or None
        password = req.POST.get('pass') or None

        User.objects.create_user(username=username, email=email , password=password)


    return render(req, 'auth/register.html' , {})
