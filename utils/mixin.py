#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from django.contrib.auth.decorators import login_required
"""
#File: mixin.py
#Time: 2022/3/6 11:11 上午
#Author: julius
"""


class LoginRequiredMixin(object):
    """
    封装View.as_view()方法,在调用之前view之前提前调用login_required
    """
    @classmethod
    def as_view(cls, **initkwargs):
        # 调用父类的as_view
        view = super(LoginRequiredMixin, cls).as_view(**initkwargs)
        return login_required(view)
