from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render, redirect, reverse
from django.contrib.auth import authenticate, login, logout
from django.utils.datastructures import MultiValueDictKeyError
from .pyscripts.emailpdf import *
from users.models import User
from qr_code.qrcode.utils import QRCodeOptions
from django.contrib.auth.hashers import make_password, check_password
from twilio.rest import Client
import os

account_sid = os.getenv('TWILIO_ACCOUNT_SID')
auth_token = os.getenv('TWILIO_AUTH_TOKEN')
client = Client(account_sid, auth_token)

def home(request):
    return render(request, "home.html")

def index(request):
    if request.user.is_authenticated :
        if request.method == "GET":
            return render(request,"index.html",{"name": request.user.name, "mcin":request.user.mcin})

        if request.method == "POST":
            raw = request.POST
            d = dict(raw)
            d.pop('csrfmiddlewaretoken')
            d.pop('submit')
            text = " ".join([f"{x} {d[x][0]}" for x in d])
            context = dict(
                my_options=QRCodeOptions(size='L', border=6, error_correction='L'),
                text=text,
                data=text
            )
            return render(request,"qr_code.html",context=context)

    return redirect('home')

def send_sms(request):
    if request.method == 'POST':
        fl=True
        url = request.POST['url']
        data = request.POST['data']
        a = data.split("#")
        print(data,a)
        d = {}
        for i in range(0,len(a),2):
            if i+1<len(a):
                d[a[i]] = a[i+1]
        if "mcin" in d:
            d["mcin"] = d["mcin"].strip()
        d["url"] = url
        func(d)
        message = client.messages.create(body=f'The url to your prescription is: {url}',from_=os.getenv('MOBILE_NO'),to="+91"+d['mobile_no'])
        return HttpResponse("Sent Mails And Sms",content_type="text/plain") if fl else HttpResponse("Error",content_type="text/plain")

def login_user(request):

    if request.method == "GET":
        if request.user.is_authenticated:
            return redirect('index')
        return render(request,"login.html")

    if request.method == "POST":
        email = request.POST['email']
        password = request.POST['pass']
        check = User.objects.filter(email=email)
        if len(check)==1 and check_password(password,check[0].password):
            login(request,check[0],backend='django.contrib.auth.backends.ModelBackend')
        else:
            return redirect('login')

        return redirect('index')

def register(request):

    if request.method == "GET":
        return render(request,"register.html")

    if request.method == "POST":
        name = request.POST['name']
        email = request.POST['email']
        mobile_no = request.POST['mobile_no']
        mcin = request.POST['mcin']
        check = User.objects.filter(email=email)

        if len(check) != 0:
            return redirect('register')

        password = make_password(request.POST['password'])
        usr = User.objects.create(email=email,password=password,name=name,mobile_no=mobile_no,mcin=mcin)

        if usr is not None:
            usr.save()
            return redirect("login")
        else:
            return redirect('register')

        return redirect('index')

def logout_user(request):
    logout(request)
    return redirect('home')