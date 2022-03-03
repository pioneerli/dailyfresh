from django.shortcuts import render

# Create your views here.
from django.views.generic import View


class orderView(View):
    def post(self, request):
        '''提交订单页面显示'''
        # 获取登录的用户
        user = request.user
        return "success"
