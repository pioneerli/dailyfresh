"""dailyfresh URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from apps.user.views import index,LoginView,RegisterView,ActiveView,\
    UserInfoView,UserAddressView,UserOrderView,LoginOutView
from apps.goods.views import IndexView, GoodsDetailView
from django.urls import re_path





urlpatterns = [
    path(r'admin/', admin.site.urls),
    path(r'user/register',RegisterView.as_view(),name='register'),
    re_path(r'user/active/(.*)',ActiveView.as_view(),name='active'),
    path(r'user/login',LoginView.as_view(),name='login'),
    path(r'user/logout',LoginOutView.as_view(),name='logout'),
    path(r'index',index,name='index'),
    path('user/info',UserInfoView.as_view(),name='UserInfo'),
    path('user/order',UserOrderView.as_view(),name='UserOrder'),
    path('user/address',UserAddressView.as_view(),name='UserAddress'),

    # path(r'^search', include('haystack.urls')),  # 全文检索框架

    # goods相关url
    path(r'goods/index',IndexView.as_view(),name='goodsIndex'),
    re_path(r'goods/details/(.*)',GoodsDetailView.as_view(),name='goodsDetail'),
]
