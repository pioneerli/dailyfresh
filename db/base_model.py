#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from django.db import models

"""
#File: base_model.py
#Time: 2022/3/3 9:55 下午
#Author: julius
"""


class BaseModel(models.Model):
    """
    基础BaseModel类
    """
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    is_delete = models.BooleanField(default=False, verbose_name='删除标记')

    class Meta:
        """
        说明是一个抽象类,不需要创建表
        """
        abstract = True
