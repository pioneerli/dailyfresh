from django.shortcuts import render
from django.http.response import HttpResponse


# Create your views here.
# user/register
def register(request):
    return render(request, 'register.html')


def handler_register(request):
    # 接收数据
    user_name = request.POST.get('user_name')
    passwd = request.POST.get('pwd')
    # 校验数据
    if not all([user_name, passwd]):
        print(user_name, passwd)
    # 对数据进行处理

    # 返回处理结果
    return HttpResponse("success")
