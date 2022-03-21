#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
#File: validate.py
#Time: 2022/3/21 9:00 上午
#Author: julius
"""
from django.http import JsonResponse
from django_redis import get_redis_connection

from apps.goods.models import GoodsSKU


def cart_info_validate(request, sku_id):
    """
    返回 conn,sku,cart_key
    """
    if not request.user:
        return JsonResponse({'res': 1, 'msg': '请先登录'})

    try:
        sku = GoodsSKU.objects.get(id=sku_id)
    except GoodsSKU.DoesNotExist as e:
        return JsonResponse({'res': 3, 'msg': '商品不存在'})

    conn = get_redis_connection('default')
    cart_key = f'cart_{request.user.id}'
    return conn, sku,cart_key
