import requests
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.shortcuts import render, redirect,HttpResponse
from django_redis import get_redis_connection
from utils.response import BaseResponse
from utils import tencent
from web import models
from django.http import JsonResponse
from utils.encrypt import md5
import random
from django.conf import settings
from web.forms.account import LoginForm,SmsLoginForm,MobileForm




def login(request):
    if request.method == "GET":
        form = LoginForm()
        return render(request, "login.html",{'form':form})

    # 1.接收并获取数据(数据格式或是否为空验证 - Form组件 & ModelForm组件）

    form = LoginForm(data=request.POST)
    if not form.is_valid():
        return render(request, "login.html", {'form': form})
    print(form.cleaned_data)
    # role = request.POST.get("role")
    # username = request.POST.get("username")
    # password = request.POST.get("password")
    data_dict = form.cleaned_data
    role = data_dict.pop('role')

    # 2.去数据库校验  1管理员  2客户
    mapping = {"1": "ADMIN", "2": "CUSTOMER"}
    if role not in mapping:
        return render(request, "login.html", {'form':form,'error': "角色不存在"})

    if role == "1":
        user_object = models.Administrator.objects.filter(active=1).filter(**data_dict).first()
    else:
        user_object = models.Customer.objects.filter(active=1).filter(**data_dict).first()

    # 2.1 校验失败
    if not user_object:
        return render(request, "login.html", {'form':form,'error': "用户名或密码错误"})

    # 2.2 校验成功，用户信息写入session+进入项目后台
    request.session[settings.NB_SESSION_KEY] = {'role': mapping[role], 'name': user_object.username, 'id': user_object.id}

    return redirect("/home/")


def sms_login(request):

    if request.method == 'GET':
        form = SmsLoginForm()
        return render(request, "sms_login.html",{'form':form})

    res = BaseResponse()
    print(request.POST)
    #1.手机格式校验
    form = SmsLoginForm(data=request.POST)
    if not form.is_valid():
        res.detail = form.errors
        return JsonResponse(res.dict,json_dumps_params={"ensure_ascii":False})

    #2.短信验证码 + redis中的验证码 =》校验  #写在form的钩子方法中
    role = form.cleaned_data['role']
    mobile = form.cleaned_data['mobile']
    # code = form.cleaned_data['code']
    #
    # conn = get_redis_connection('default')
    # cache_code =  conn.get(mobile)
    # if not cache_code:
    #     res.detail = {"code":["短信验证码未发送或失效"]}
    #     return JsonResponse(res.dict)
    #
    # print(code,type(code))
    # print(cache_code,type(cache_code))
    # if code != cache_code.decode('utf-8'):
    #     res.detail = {"code":['短信验证码错误']}
    #     return JsonResponse(res.dict)
    #3.登录成功 +  检查手机号是否存在【不存在不给登录】
    if role == "1":
        user_object = models.Administrator.objects.filter(active=1, mobile=mobile).first()
    else:
        user_object = models.Customer.objects.filter(active=1, mobile=mobile).first()

    if not user_object:
        res.detail = {"mobile":["手机号不存在"]}
        return JsonResponse(res.dict)

    # 4. 校验成功，用户信息写入session+进入项目后台
    mapping = {"1": "ADMIN", "2": "CUSTOMER"}
    request.session[settings.NB_SESSION_KEY] = {'role': mapping[role], 'name': user_object.username, 'id': user_object.id}
    res.status = True
    return JsonResponse(res.dict)





def sms_send(request):
    # print(request.META.get('X_CSRFTOKEN'))
    # print(request.META.get('HTTP_X_CSRFTOKEN'))
    # print(request.META.get('HTTP_XXX'))
    res = BaseResponse()
    #1.校验数据合法性： 手机号的格式 + 角色
    print(request.GET)
    print(request.POST)
    request.POST.get('mobile')
    form = MobileForm(data=request.POST)
    if not form.is_valid():
        print(form.errors.as_data())
        res.detail = form.errors
        return JsonResponse(res.dict, json_dumps_params={'ensure_ascii': False})
        # return JsonResponse({'status': False, 'detail': form.errors}, json_dumps_params={'ensure_ascii': False})
    # #1-1 校验手机号在数据库中是否存在，如果不存在，不允许发送
    # mobile = form.cleaned_data['mobile']
    # role = form.cleaned_data['role']
    #
    # if role == "1":
    #     exists = models.Administrator.objects.filter(active=1, mobile=mobile).exists()
    # else:
    #     exists = models.Customer.objects.filter(active=1, mobile=mobile).exists()
    # if not exists:
    #     res.detail = {"mobile":["手机号不存在"]}
    #     return JsonResponse(res.dict,json_dumps_params={"ensure_ascii":False})



    res.status = True
    res.data = settings.LOGIN_HOME
    return JsonResponse(res.dict)


def logout(request):
    """ 注销 """
    request.session.clear()
    return redirect(settings.NB_LOGIN_URL)


def home(request):

    return render(request,'home.html')

def order(request):

    return HttpResponse('order')






