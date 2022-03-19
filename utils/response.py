#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
#File: response.py
#Time: 2022/3/19 6:46 下午
#Author: julius
"""
from django.http import response

from utils import serializer


class PlainResponse(response.HttpResponse):
    """返回原生字符串
    Content-Type: text/plain
    """
    def __init__(self, content=b'', *args, **kwargs):
        kwargs.setdefault('content_type', 'text/plain')
        super(PlainResponse, self).__init__(content=content, *args, **kwargs)


class JsonResponse(response.JsonResponse):
    """响应一个json数据

    示例：return JsonResponse({'message': 'ok'}, status=200)
    """
    def __init__(self, *args, **kwargs):
        kwargs['encoder'] = serializer.UtilsJSONEncoder
        super(JsonResponse, self).__init__(*args, **kwargs)


class RestErrorResponse(JsonResponse):
    def __init__(self, data, *args, **kwargs):
        data = {'code': -1, 'msg': data}
        super(RestErrorResponse, self).__init__(data, *args, **kwargs)


class BadRequestResponse(RestErrorResponse):
    """400 Bad Request
    示例：return BadRequestResponse('缺少参数"foo"！')
    会返回一个状态为400的{'code': -1, 'msg': '缺少参数"foo"！'}数据
    """
    status_code = 400


class UnauthorizedResponse(RestErrorResponse):
    """401 Unauthorized"""
    status_code = 401


class ForbiddenResponse(RestErrorResponse):
    """403 Forbidden
    示例：return ForbiddenResponse('没有权限！')
    会返回一个状态为403的{'code': -1, 'msg': '没有权限！'}数据
    """
    status_code = 403


class NotFoundResponse(RestErrorResponse):
    """400 Not Found"""
    status_code = 404


class MethodNotAllowedResponse(RestErrorResponse):
    """405 Method Not Allowed"""
    status_code = 405