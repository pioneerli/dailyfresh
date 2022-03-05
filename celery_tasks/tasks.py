#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
#File: tasks.py
#Time: 2022/3/5 5:10 下午
#Author: julius
"""
import time

from celery import Celery
from dailyfresh import settings
from django.core.mail import send_mail

import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dailyfresh.settings')
django.setup()
# 创建一个Celery类的实例对象
app = Celery('celery_tasks.tasks', broker='redis://:123456@124.221.137.216:6379/8')


@app.task
def send_register_active_email(email_to,user_from,user_token):
    subject = '【重要】天天生鲜激活邮件'
    message = f"<h1>{user_from}, 欢迎您成为天天生鲜注册会员</h1>请点击下面链接激活您的账户<br/>" \
              f"<a href='http://127.0.0.1:8000/user/active/{user_token}'>http://127.0.0.1:8000/user/active/{user_token}</a>"
    from_email = settings.EMAIL_FROM
    recipient_list = [email_to]
    try:
        send_mail(subject, message, from_email, recipient_list, html_message=message)
        # 模拟发邮件耗时
        time.sleep(5)
    except Exception as e:
        print(f'发送失败 {e}')