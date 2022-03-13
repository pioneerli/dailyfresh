import re

from django.shortcuts import render
from apps.user.models import User,Address
from django.views.generic import View
from itsdangerous.serializer import Serializer
from dailyfresh import settings
from django.http import HttpResponseRedirect
from django.urls import reverse
import logging
from celery_tasks.tasks import send_register_active_email
from django.contrib.auth import login,logout
from utils.mixin import LoginRequiredMixin
from django.core.cache import cache
from apps.goods.models import GoodsSKU

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
                # 如果存在next, 则返回next字段的uri值
                if request.GET.get('next'):
                    return HttpResponseRedirect(request.GET.get('next'))
                return HttpResponseRedirect(reverse('index'))
            else:
                # 用户未激活
                return render(request, 'login.html', {'errmsg': '账户未激活'})
        else:
            # 用户名或密码错误
            return render(request, 'login.html', {'errmsg': '用户名或密码错误'})


class LoginOutView(View):
    def get(self,request):
        # 调用logout清楚session信息
        logout(request)
        return HttpResponseRedirect(reverse('login'))


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
class UserInfoView(LoginRequiredMixin,View):
    """
    用户中心View
    """
    page = 'user'

    def get(self, request):
        user = request.user
        is_auth = user.is_authenticated
        print(is_auth)
        address = Address.get_default_address(user)
        user_history_sku_key = f'history_{user.id}'
        print(user_history_sku_key)
        # 获取redis缓存中用户最新浏览的5个商品sku,没有获取到返回[]
        user_history_id_values = cache.get(user_history_sku_key)
        sku_ids = user_history_id_values[:5] if user_history_id_values else []
        print(sku_ids)
        # 把获取到的sku_id 进行展示
        # history_sku_list = []
        # for s_id in sku_ids:
        #     sku = GoodsSKU.objects.get(id=s_id)
        #     history_sku_list.append(sku)
        # 使用列表生成式把 根据sku_id获取到的sku放入列表
        history_sku_list = [GoodsSKU.objects.get(id=s_id) for s_id in sku_ids]

        return render(request, 'user_center_info.html', {'page': 'user','user':user,'address':address,'sku_list':history_sku_list})


# user/order
class UserOrderView(LoginRequiredMixin,View):
    """
    用户订单View
    """
    page = 'order'

    def get(self, request):
        return render(request, 'user_center_order.html', {'page': 'order'})


# user/order
class UserAddressView(LoginRequiredMixin,View):
    """
    用户订单View
    """
    page = 'address'

    def get(self, request):
        user = request.user
        # 获取用户的默认地址,如果存在则返回address,不存在则返回None
        print(f'userAddressView:{user} {type(user)}')
        address_qs = Address.objects.filter(user=user,is_default=True)
        address = address_qs[0] if address_qs.exists() else None
        return render(request, 'user_center_site.html', {'page': 'address','address':address})

    def post(self,request):
        # 1、获取数据
        receiver = request.POST.get('receiver')
        addr = request.POST.get('addr')
        zip_code = request.POST.get('zip_code',None)
        phone = request.POST.get('phone')
        print(f"receiver{receiver}")
        # 2、校验数据
        # 完整性校验
        if not all([receiver,addr,phone]):
            return render(request,'user_center_site.html',{'errmsg':'用户地址信息数据不完整'})

        # 校验手机号
        if not re.match(r'^1[3|4|5|7|8][0-9]{9}$', phone):
            return render(request, 'user_center_site.html', {'errmsg': '手机格式不正确'})

        # 3、业务处理：地址添加
        # 如果用户已存在默认收货地址，添加的地址不作为默认收货地址，否则作为默认收货地址
        # 获取登录用户对应User对象
        user = request.user

        is_default = True if Address.get_default_address(user) else False
        print(f'is_default:{is_default} user:{user}')
        # 4、创建数据
        Address.objects.create(user=user,
                               receiver=receiver,
                               addr=addr,
                               zip_code=zip_code,
                               phone=phone,
                               is_default=is_default)
        # 返回页面
        return HttpResponseRedirect(reverse('UserAddress'))
