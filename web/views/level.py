from django.shortcuts import render, redirect,HttpResponse
from django.urls import reverse
from django_redis import get_redis_connection

from utils.link import filter_reverse
from utils.response import BaseResponse
from utils import tencent
from web import models
from django import forms
from django.http import JsonResponse
from utils.encrypt import md5
import random
from django.conf import settings
from web.forms.account import LoginForm,SmsLoginForm,MobileForm
from utils.bootstrap import BootStrapForm


class LevelModelForm(BootStrapForm,forms.ModelForm):
    class Meta:
        model = models.Level
        fields = ['title','percent']




class LevelForm(forms.Form):
    title = forms.CharField(
        label='标题',
        required=True,
        widget=forms.TextInput(attrs={'class':'form-control','placeholder':'请输入标题'}),
    )

    percent = forms.CharField(
        label='折扣',
        required=True,
        widget=forms.TextInput(attrs={'class':'form-control','placeholder':'请输入折扣'}),
    )


def level_list(request):

    queryset = models.Level.objects.filter(active=1)
    return render(request,'level_list.html',{"queryset":queryset})


def level_add(request):
    if request.method == 'GET':
        form = LevelModelForm()

        return render(request,'form.html',{'form':form})

    form = LevelModelForm(data=request.POST)
    if not form.is_valid():

        return render(request, 'form.html', {'form':form})
    form.save()
    return redirect(reverse('level_list'))



def level_edit(request,pk):
    level_object = models.Level.objects.filter(id=pk,active=1).first()
    if request.method == 'GET':
        form = LevelModelForm(instance=level_object)
        return render(request, 'form.html', {'form': form})
    form = LevelModelForm(data=request.POST,instance=level_object)
    if not form.is_valid():
        return render(request, 'form.html', {'form': form})
    form.save()
    return redirect(filter_reverse(request,'/level/list/'))

def level_delete(request,pk):
    exists = models.Customer.objects.filter(level_id=pk).exists()
    if not exists:
        models.Level.objects.filter(id=pk).update(active=0)
    return redirect(reverse('level_list'))