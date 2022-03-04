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
from apps.user.views import register,handler_register

urlpatterns = [
    path(r'^admin/', admin.site.urls),
    path(r'user/register',register,name='register'),
    path(r'user/handler_register',handler_register,name='handler_register')
    # path(r'^search', include('haystack.urls')),  # 全文检索框架
    # path('order/',views.orderView.as_view()),
]
