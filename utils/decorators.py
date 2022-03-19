#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
#File: decorators.py
#Time: 2022/3/19 6:13 下午
#Author: julius
"""
import collections

from utils import views, exception
from django.http import response as django_response
from utils import response


def build_param_dict(func, request, param_desc, **kwargs):
    """从环境中组装函数参数，并返回字典
    XXX: 如果缺少参数，该函数会抛出可被自动捕捉的BadRequestException"""
    # def func(self, a, b=0, **c): d=''
    #
    # func.func_defaults         == (0,)
    # func.func_code.n_locals    == 4
    # func.func_code.co_argcount == 3
    # func.func_code.co_varnames == ('self', 'a', 'b', 'c')
    param_dict = collections.OrderedDict()

    # 获取参数列表和默认值
    arg_names = func.__code__.co_varnames[1:func.__code__.co_argcount]
    arg_defaults = func.__defaults__

    # 使用默认值初始化参数列表（无默认值填充None）
    if arg_defaults is None:
        nr_position_arg = len(arg_names)
    else:
        nr_position_arg = len(arg_names) - len(arg_defaults)

    for k, v in enumerate(arg_names):
        if arg_defaults is None or k < nr_position_arg:
            param_dict[v] = '$dummy$'
        else:
            param_dict[v] = arg_defaults[k - nr_position_arg]

    # 填充路径内的参数（如/api/projects/(?P<project_name>\w+)/）
    param_dict.update(kwargs)

    # 填充http传入参数
    for arg_name in arg_names:
        param_value = views.BaseView.get_param(request, arg_name)
        if param_value is not None:
            param_dict[arg_name] = param_value

    # 检查所有参数是否传入
    for arg_name in arg_names:
        if param_dict[arg_name] == '$dummy$':
            arg_desc = f' ({param_desc.get(arg_name)})' if param_desc.get(arg_name) else ''
            err_msg = f'{arg_name}{arg_desc} 不能为空！'
            raise exception.BadRequestException(err_msg)

    return param_dict


def build_response(result):
    headers = {}
    status = 200

    if isinstance(result, django_response.HttpResponseBase):
        return result
    elif isinstance(result, tuple) and len(result) == 2:
        data, status = result
    elif isinstance(result, tuple) and len(result) == 3:
        data, status, headers = result
    elif isinstance(result, (str, int, float, list)):
        data = dict(data=result)
    else:
        data = result

    # indent = 4 if settings.DEBUG else None
    if 'code' not in data:
        data['code'] = 0
    if 'msg' not in data:
        data['msg'] = ''
    resp = response.JsonResponse(
        data, status=status, json_dumps_params={'indent': 4, 'ensure_ascii': False}
    )
    for k, v in headers.items():
        resp[k] = v

    return resp


class FunctionAsApiV2(object):
    def __init__(self, **param_desc_dict):
        self.param_desc_dict = param_desc_dict

    def __call__(self, func):
        param_desc = self.param_desc_dict

        def wrapper(self, request, **kwargs):
            param_dict = build_param_dict(func, request, param_desc, **kwargs)
            result = func(self, **param_dict)

            return build_response(result)

        return wrapper
