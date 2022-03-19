#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
#File: serializer.py
#Time: 2022/3/19 6:39 下午
#Author: julius
"""

import json
from django.core.serializers.json import DjangoJSONEncoder
from django.utils import timezone


def json_encode(o):
    """将对象使用json编码，支持datetime格式"""
    return json.dumps(o, cls=UtilsJSONEncoder)


def json_decode(s):
    """将字符串使用json解码"""
    return json.loads(s)


class UtilsJSONEncoder(DjangoJSONEncoder):
    """DjangoJSONEncoder wrapper
    日期按YYYY-mm-dd HH:MM:SS格式序列化
    集合按列表格式序列化
    """

    def default(self, o):
        if isinstance(o, timezone.datetime):
            r = o.strftime('%Y-%m-%d %H:%M:%S')
            return r

        if isinstance(o, set):
            return list(o)

        try:
            return super(UtilsJSONEncoder, self).default(o)
        except TypeError as e:
            if 'is not JSON serializable' in str(e):
                if hasattr(o, '__dict__'):
                    return o.__dict__
                else:
                    raise e


class PrettyJSONEncoder(UtilsJSONEncoder):
    def encode(self, o) -> str:
        return json.dumps(o, indent=4, ensure_ascii=False)