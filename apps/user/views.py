import re

from django.core.paginator import Paginator
from django.shortcuts import render

from apps.order.models import OrderInfo, OrderGoods
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
from django_redis import get_redis_connection
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
                return HttpResponseRedirect(reverse('goodsIndex'))
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
        conn = get_redis_connection('default')
        # 获取redis 链接使用 redis API 进行数据截取
        sku_ids=conn.lrange(user_history_sku_key,0,4)
        history_sku_list = [GoodsSKU.objects.get(id=s_id.decode()) for s_id in sku_ids]
        # # 获取redis缓存中用户最新浏览的5个商品sku,没有获取到返回[]
        # user_history_id_values = cache.get(user_history_sku_key)
        # sku_ids = user_history_id_values[:5] if user_history_id_values else []
        # print(sku_ids)
        # # 把获取到的sku_id 进行展示
        # history_sku_list = []
        # for s_id in sku_ids:
        #     sku = GoodsSKU.objects.get(id=s_id)
        #     history_sku_list.append(sku)
        # # 使用列表生成式把 根据sku_id获取到的sku放入列表
        # history_sku_list = [GoodsSKU.objects.get(id=s_id) for s_id in sku_ids]

        return render(request, 'user_center_info.html', {'page': 'user','user':user,'address':address,'sku_list':history_sku_list})


# user/order
class UserOrderView(LoginRequiredMixin,View):
    """
    用户订单View
    """
    '''用户中心-订单页'''

    def get(self, request, page):
        '''显示'''
        # 获取用户的订单信息
        user = request.user
        orders = OrderInfo.objects.filter(user=user).order_by('-create_time')

        # 遍历获取订单商品的信息
        for order in orders:
            # 根据order_id查询订单商品信息
            order_skus = OrderGoods.objects.filter(order_id=order.order_id)

            # 遍历order_skus计算商品的小计
            for order_sku in order_skus:
                # 计算小计
                amount = order_sku.count * order_sku.price
                # 动态给order_sku增加属性amount,保存订单商品的小计
                order_sku.amount = amount

            # 动态给order增加属性，保存订单状态标题
            order.status_name = OrderInfo.ORDER_STATUS[order.order_status]
            # 动态给order增加属性，保存订单商品的信息
            order.order_skus = order_skus

        # 分页
        paginator = Paginator(orders, 1)

        # 获取第page页的内容
        try:
            page = int(page)
        except Exception as e:
            page = 1

        if page > paginator.num_pages:
            page = 1

        # 获取第page页的Page实例对象
        order_page = paginator.page(page)

        # todo: 进行页码的控制，页面上最多显示5个页码
        # 1.总页数小于5页，页面上显示所有页码
        # 2.如果当前页是前3页，显示1-5页
        # 3.如果当前页是后3页，显示后5页
        # 4.其他情况，显示当前页的前2页，当前页，当前页的后2页
        num_pages = paginator.num_pages
        if num_pages < 5:
            pages = range(1, num_pages + 1)
        elif page <= 3:
            pages = range(1, 6)
        elif num_pages - page <= 2:
            pages = range(num_pages - 4, num_pages + 1)
        else:
            pages = range(page - 2, page + 3)

        # 组织上下文
        context = {'order_page': order_page,
                   'pages': pages,
                   'page': 'order'}

        # 使用模板
        return render(request, 'user_center_order.html', context)


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
