from django.urls import path
from django.conf.urls import include
from . import views

urlpatterns = [
    path('', views.home,name='home'),
    path('index/', views.index,name='index'),
    path('qr_code/', include('qr_code.urls', namespace="qr_code")),
    path('send_sms/',views.send_sms,name="sendSms"),
    path('login/',views.login_user,name='login'),
    path('register/',views.register,name='register'),
    path('logout',views.logout_user,name='logout')
]