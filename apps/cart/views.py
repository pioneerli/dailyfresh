from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.
from django.views.generic import View
from utils.decorators import FunctionAsApiV2
from django_redis import get_redis_connection
from apps.goods.models import GoodsSKU


class CartAddView(View):
    """
    往购物车新增商品View
    """

    @FunctionAsApiV2()
    def post(self, sku_id, count):
        """
            1、校验数据合法性,包括根据 sku_id 查询出来的sku是否存在,count是否可以转换成int类型
            2、获取redis里面sku_id count数量,判断是否存在,存在则使用redis缓存里面的数量(商品数量=
            count+hget(cart_key,sku_id))加上count,不存在数据则为count
            3、判断最新的count数量是否大于sku库存,如果大于库存,返回商品数量大于库存
            4、把count 写入redis 通过 hset(cart_key,sku_id,count)
            5、通过hlen返回商品条目数并返回
        """

        # 1、校验添加的商品数量
        if not self.request.user:
            return JsonResponse({'res': 1, 'msg': '请先登录'})
        try:
            sku = GoodsSKU.objects.get(id=sku_id)
        except GoodsSKU.DoesNotExist as e:
            return JsonResponse({'res': 3, 'msg': '商品不存在'})

        try:
            count = int(count)
        except Exception as e:
            # 数目出错
            return JsonResponse({'res': 2, 'msg': '商品数目出错'})

        # 2、获取redis里面sku_id count数量,判断是否存在,存在则使用redis缓存里面的数量(商品数量=
        # count+hget(cart_key,sku_id))加上count,不存在数据则为count
        conn = get_redis_connection('default')
        cart_key = f'cart_{self.request.user.id}'
        sku_count = conn.hget(cart_key, sku_id)
        if sku_count:
            count += int(sku_count)

        # 3、判断最新的count数量是否大于sku库存,如果大于库存,返回商品数量大于库存
        if count > sku.stock:
            return JsonResponse({'res': 4, 'msg': '商品数量大于库存,请减少购买数量'})

        # 4、把count写入redis
        conn.hset(cart_key, sku_id, count)

        # 5、获取 redis 条目数
        total_count = conn.hlen(cart_key)
        return JsonResponse({'res': 5, 'total_count': total_count, 'msg': '添加成功'})


class CartInfoView(View):
    """
    商品详情view
    """

    @FunctionAsApiV2()
    def get(self):
        """
        1、获取指定key所有的条目,然后遍历这些条目,计算价格小记、计算商品总数、总价格
        2、组织上下文,返回sku,总价格,总数量
        """
        cart_key = f"cart_{self.request.user.id}"
        conn = get_redis_connection('default')
        cart_dict = conn.hgetall(cart_key)
        skus = []
        total_count = 0
        total_price = 0
        for sku_id, sku_count in cart_dict.items():
            # 根据商品id获取sku对象
            sku = GoodsSKU.objects.get(id=sku_id)
            sku_price_summary = int(sku.price) * int(sku_count)
            # 给sku添加count属性
            sku.sku_count = int(sku_count)
            # 给sku添加价格小结属性
            sku.sku_price_summary = sku_price_summary
            skus.append(sku)
            total_count += int(sku_count)
            total_price += sku_price_summary

        context = {'total_count': total_count, 'total_price': total_price, 'skus': skus}
        return render(self.request, 'cart.html', context)


class CartUpdateView(View):
    @FunctionAsApiV2()
    def post(self, sku_id, count):
        # 1、校验添加的商品数量
        if not self.request.user:
            return JsonResponse({'res': 1, 'msg': '请先登录'})

        try:
            sku = GoodsSKU.objects.get(id=sku_id)
        except GoodsSKU.DoesNotExist as e:
            return JsonResponse({'res': 3, 'msg': '商品不存在'})

        try:
            count = int(count)
        except Exception as e:
            # 数目出错
            return JsonResponse({'res': 2, 'msg': '商品数目出错'})

        conn = get_redis_connection('default')
        cart_key = f'cart_{self.request.user.id}'
        # 2、判断count数量是否大于库存，大于直接返回库存不足，小于则更新缓存
        if count > sku.stock:
            return JsonResponse({'res': 4, 'msg': '购买数量大于库存，请减少购买数量'})
        # 3、更新指定sku数量
        conn.hset(cart_key, sku_id, count)

        sku_val_ls = conn.hvals(cart_key)
        total_count = 0
        for i in sku_val_ls:
            total_count += int(i)

        return JsonResponse({'res': 5, 'total_count': total_count, 'message': '更新成功'})