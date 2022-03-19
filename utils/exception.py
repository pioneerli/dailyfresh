#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
#File: exception.py
#Time: 2022/3/19 6:41 下午
#Author: julius
"""

class ForbiddenException(Exception):
    """没有权限"""


class BadRequestException(Exception):
    """错误请求"""


class UnauthorizedException(Exception):
    """未认证"""


class NotFoundException(Exception):
    """404 Not Found"""