import re

from django.shortcuts import render,redirect
from django.http.response import HttpResponse
from apps.user.models import User


# Create your views here.
# 首页
def index(request):
    return render(request,'index.html')


def login(request):
    return render(request,'login.html')


# user/register
def register(request):
    return render(request, 'register.html')


def handler_register(request):
    # 接收数据
    username = request.POST.get('user_name')
    passwd = request.POST.get('pwd')
    email = request.POST.get('email')
    allow = request.POST.get('allow')
    # 校验数据
    if not all([username, passwd,email]):
        return render(request,'register.html',{'errmsg': '数据不完整'})
    # 对数据进行处理
    # 校验邮箱
    if not re.match(r'^[a-z0-9][\w.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
        return render(request,'register.html',{'errmsg':'邮箱格式不正确'})
    # 校验用户名
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        user = None

    if user:
        # 用户名已存在
        print('用户名已存在')
        return render(request, 'register.html', {'errmsg': '用户名已存在'})

    # 校验协议
    if allow != 'on':
        return render(request,'register.html',{'errmsg':'请勾选协议'})

    user = User.objects.create(username=username,email=email,password=passwd)
    user.is_active = False
    user.save()
    # 返回应答,跳回首页
    return render(request,'login.html')