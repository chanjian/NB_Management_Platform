from datetime import datetime
import os
from django.conf import settings
from django.shortcuts import render, HttpResponse
from web import models
from django import forms
from utils.bootstrap import BootStrapForm,BootStrapModelForm
from utils.qr_code_to_link import qr_code_to_link

def upload_list1(request):
    """上传文件1"""
    if request.method == "GET":
        return render(request, 'upload/upload_list.html')

    # # 'username': ['big666']
    # print(request.POST)  # 请求体中数据
    # # {'avatar': [<InMemoryUploadedFile: 图片 1.png (image/png)>]}>
    # print(request.FILES)  # 请求发过来的文件 {}

    file_object = request.FILES.get("avatar")
    # print(file_object.name)  # 文件名：WX20211117-222041@2x.png

    f = open(file_object.name, mode='wb')
    for chunk in file_object.chunks():
        f.write(chunk)
    f.close()
    return HttpResponse("...")


class UpForm(BootStrapForm,forms.Form):
    exclude_field_list = ['img']

    name = forms.CharField(label="姓名")
    age = forms.IntegerField(label="年龄")
    img = forms.FileField(label="头像")



def get_upload_path(request,instance):
    # 获取当前月份
    current_month = datetime.now().strftime('%Y-%m')

    #获取当前用户名
    name = request.nb_user.name

    # 构建路径：media/用户名/月份/文件名
    upload_path = os.path.join("media", name, current_month, instance.name)
    print('upload_path:',upload_path)

    # 将路径中的 \ 替换为 /
    # upload_path = upload_path.replace("\\", "/")
    # print('os.path',os.path)

    # 如果目录不存在，则创建
    os.makedirs(os.path.dirname(upload_path), exist_ok=True)
    # os.makedirs(upload_path, exist_ok=True)


    return upload_path


def upload_list2(request):
    """
    上传文件2
    使用Form
    """
    title = 'Form上传'
    if request.method == 'GET':
        form = UpForm()
        return render(request,'upload/upload_form.html',{'form':form,'title':title})

    form = UpForm(data=request.POST,files=request.FILES)
    if not form.is_valid():

        return render(request, 'upload/upload_form.html', {'form': form, 'title': title})
    print(form.cleaned_data)
    # 1.读取图片内容，写入到文件夹中并获取文件的路径。
    image_object = form.cleaned_data.get("img")

    # media_path = os.path.join(settings.MEDIA_ROOT, image_object.name) #这种返回的是绝对路径
    # media_path = os.path.join("media",request.nb_user.name, image_object.name)

    media_path = get_upload_path(request,image_object)

    f = open(media_path, mode='wb+')
    for chunk in image_object.chunks():
        f.write(chunk)
    f.close()

    # 2.将图片文件路径写入到数据库
    models.Boss.objects.create(
        name=form.cleaned_data['name'],
        age=form.cleaned_data['age'],
        img=media_path,
    )
    return HttpResponse("...")




class UpModelForm(BootStrapModelForm):
    exclude_field_list = ['img']

    class Meta:
        model = models.CityModelFrom
        fields = '__all__'


def upload_list3(request):
    """
    上传文件3
    使用ModelForm
    """
    title="ModelForm上传文件"
    if request.method == 'GET':
        form = UpModelForm()
        return render(request, 'upload/upload_form.html', {'form': form, 'title': title})

    form = UpModelForm(data=request.POST,files=request.FILES)
    if form.is_valid():
        form.save()
        return HttpResponse('success')

    return render(request, 'upload/upload_form.html', {'form': form, 'title': title})

# from django import forms
# from utils.bootstrap import BootStrapModelForm
#
#
# class UpModelForm(BootStrapModelForm):
#     bootstrap_exclude_fields = ['img']
#
#     class Meta:
#         model = models.City
#         fields = "__all__"
#
#
# def upload_modal_form(request):
#     """ 上传文件和数据（modelForm）"""
#     title = "ModelForm上传文件"
#     if request.method == "GET":
#         form = UpModelForm()
#         return render(request, 'upload_form.html', {"form": form, 'title': title})
#
#     form = UpModelForm(data=request.POST, files=request.FILES)
#     if form.is_valid():
#         # 对于文件：自动保存；
#         # 字段 + 上传路径写入到数据库
#         form.save()
#
#         return HttpResponse("成功")
#     return render(request, 'upload_form.html', {"form": form, 'title': title})


def city_list(request):
    queryset = models.CityModelFrom.objects.all()
    return render(request,'upload/city_list.html',{'queryset':queryset})


class CityUpForm(BootStrapForm,forms.Form):
    exclude_field_list = ['img']

    name = forms.CharField(label="城市")
    count = forms.IntegerField(label="人口")
    img = forms.FileField(label="Logo")


def upload_list4(request):
    """
    上传文件4
    模型使用City，类型使用Form
    """
    title = "Form上传文件--city"
    if request.method == 'GET':
        form = CityUpForm()
        return render(request, 'upload/upload_form.html', {'form': form, 'title': title})

    form = CityUpForm(data=request.POST, files=request.FILES)
    if not form.is_valid():
        print(form.errors)  # 打印错误信息
        return render(request, 'upload/upload_form.html', {'form': form, 'title': title})
    print(form.cleaned_data)
    # 1.读取图片内容，写入到文件夹中并获取文件的路径。
    image_object = form.cleaned_data.get("img")
    if not image_object:
        print("文件字段为空")
        return HttpResponse("文件字段为空")
    # media_path = os.path.join(settings.MEDIA_ROOT, image_object.name) #这种返回的是绝对路径
    # media_path = os.path.join("media",request.nb_user.name, image_object.name)

    media_path = get_upload_path(request, image_object)

    try:
        f = open(media_path, mode='wb+')
        for chunk in image_object.chunks():
            f.write(chunk)
        f.close()
        print("文件写入成功")
    except Exception as e:
        print("文件写入失败:", e)

    url_link = qr_code_to_link(media_path)
    print('url_link:',url_link)

    # 2.将图片文件路径写入到数据库
    models.CityForm.objects.create(
        name=form.cleaned_data['name'],
        count=form.cleaned_data['count'],
        img=media_path,
        url = url_link,
    )
    return HttpResponse("...")




def city_list2(request):
    queryset = models.CityForm.objects.all()
    return render(request,'upload/city_list.html',{'queryset':queryset})