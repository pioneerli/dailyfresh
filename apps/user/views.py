import re

from django.shortcuts import render, redirect
from apps.user.models import User
from django.views.generic import View
from itsdangerous.serializer import Serializer
from dailyfresh import settings
from django.http import HttpResponseRedirect
from django.urls import reverse
import logging
from celery_tasks.tasks import send_register_active_email
from django.contrib.auth import login

logging.basicConfig()
logger = logging.getLogger(__name__)


# 首页
def index(request):
    return render(request, 'index.html')


class LoginView(View):
    def get(self, request):
        return render(request, 'login.html')

    def post(self, request):
        # 校验数据
        username = request.POST.get('username')
        password = request.POST.get('pwd')
        print(username, password)
        # 如果username或password有一个为空,all(username,password)返回False
        if not all([username, password]):
            return render(request, 'login.html', {'errmsg': '数据不完整'})

        user_qs = User.objects.filter(username=username, password=password)
        print(username, password)
        if user_qs.exists():
            # 用户名密码正确
            if user_qs[0].is_active:
                print('登录成功')
                # 把用户session保存到redis服务器
                login(request, user_qs[0])
                return HttpResponseRedirect(reverse('index'))
            else:
                # 用户未激活
                return render(request, 'login.html', {'errmsg': '账户未激活'})
        else:
            # 用户名或密码错误
            return render(request, 'login.html', {'errmsg': '用户名或密码错误'})


class ActiveView(View):
    def get(self, request, token):
        """
        解析token,获得用户id,根据id把is_active=1,跳转到登陆页
        """
        try:
            print('开始激活')
            serializer = Serializer(settings.SECRET_KEY)
            user_id = serializer.loads(token)
            # 通过用户id获取user
            user = User.objects.get(id=user_id)
            print(user.id)
            user.is_active = True
            user.save()
            return HttpResponseRedirect(reverse('login'))
        except Exception as e:
            print(f'激活失败 {e}')


# user/register
class RegisterView(View):
    def get(self, request):
        return render(request, 'register.html')

    def post(self, request):
        # 接收数据
        username = request.POST.get('user_name')
        passwd = request.POST.get('pwd')
        email = request.POST.get('email')
        allow = request.POST.get('allow')
        # 校验数据
        if not all([username, passwd, email]):
            return render(request, 'register.html', {'errmsg': '数据不完整'})
        # 对数据进行处理
        # 校验邮箱
        if not re.match(r'^[a-z0-9][\w.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            return render(request, 'register.html', {'errmsg': '邮箱格式不正确'})
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
            return render(request, 'register.html', {'errmsg': '请勾选协议'})

        user = User.objects.create(username=username, email=email, password=passwd)
        user.is_active = False
        user.save()
        # 创建序列化对象
        serializer = Serializer(settings.SECRET_KEY)
        # 把新创建的user.id进行加密
        user_token = serializer.dumps(user.id)
        # 往broker里面发送消息
        send_register_active_email.delay(email, username, user_token)
        # 返回应答,跳回登陆页面
        return render(request, 'login.html')


# user/info
class UserInfoView(View):
    """
    用户中心View
    """
    page = 'user'

    def get(self, request):
        return render(request, 'user_center_info.html', {'page': 'user'})


# user/order
class UserOrderView(View):
    """
    用户订单View
    """
    page = 'order'

    def get(self, request):
        return render(request, 'user_center_order.html', {'page': 'order'})


# user/order
class UserAddressView(View):
    """
    用户订单View
    """
    page = 'address'

    def get(self, request):
        return render(request, 'user_center_order.html', {'page': 'address'})
