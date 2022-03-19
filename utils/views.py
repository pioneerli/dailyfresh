#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
#File: views.py
#Time: 2022/3/19 6:36 下午
#Author: julius
"""
from django.views import generic as generic_views
from django import http
from django.core.paginator import (
    Paginator,
    EmptyPage,
    PageNotAnInteger,
)
from . import serializer,exception
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()


class BaseView(generic_views.View):
    """视图基类，提供了一些视图的常用方法"""

    @staticmethod
    def get_param(request, param_name=None, default_value=None):
        """根据请求方法获取某个请求参数"""
        url_params = request.GET
        data_params = {}
        json_params = {}

        if request.method == 'POST':
            data_params = request.POST
        elif request.method == 'PUT':
            data_params = http.QueryDict(request.body)

        if 'CONTENT_TYPE' in request.META and \
                request.META['CONTENT_TYPE'].startswith('application/json') and request.body:
            try:
                json_params = serializer.json_decode(request.body)
            except ValueError:
                errmsg = 'json参数格式不合法'
                logger.error(f'{errmsg}: {request.body}')

                raise exception.BadRequestException(errmsg)

        params = dict()
        params.update(url_params.items())
        params.update(data_params.items())
        params.update(json_params.items())

        if not param_name:
            return params

        return params.get(param_name, default_value)

    @staticmethod
    def parse_to_bool(param):
        return param in [True, 'true', 'True']

    @staticmethod
    def paginate_queryset(qs, page_len, page):
        """将queryset分页，并返回指定页"""
        paginator = Paginator(qs, page_len)
        try:
            page_qs = paginator.page(page)
        except PageNotAnInteger:
            page_qs = paginator.page(1)
        except EmptyPage:
            # 超出范围，返回最后一页
            page_qs = paginator.page(paginator.num_pages)

        return page_qs
