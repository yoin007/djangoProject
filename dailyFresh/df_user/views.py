# coding=utf-8
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponseRedirect
from .models import *
from . import user_decorator
from hashlib import sha1
from df_goods.models import GoodsInfo
from df_cart.models import CartInfo
from df_order.models import *
from django.core.paginator import Paginator


def register(request):
    return render(request, 'df_user/register.html')


def register_handle(request):
    # 接收用户收入
    post = request.POST
    uname = post.get('user_name')
    upwd = post.get('pwd')
    upwd2 = post.get('cpwd')
    uemail = post.get('email')
    # 判断两次密码
    if upwd != upwd2:
        return redirect('/user/register/')
    # 密码加密
    s1 = sha1()
    s1.update(upwd.encode('utf-8'))
    upwd3 = s1.hexdigest()
    # 创建用户对象
    user = UserInfo()
    user.uname = uname
    user.upwd = upwd3
    user.uemail = uemail
    user.save()
    # 注册成功，跳转登录页面
    return redirect('/user/login')


def register_exist(request):
    uname = request.GET.get('uname')
    count = UserInfo.objects.filter(uname=uname).count()
    return JsonResponse({'count': count})


def login(request):
    uname = request.COOKIES.get('uname', '')
    context = {'uname': uname, 'title': '用户登录', 'error_name': 0, 'error_pwd': 0}
    return render(request, 'df_user/login.html', context)


def login_check(request):
    post = request.POST
    uname = post.get('username')
    upwd = post.get('pwd')
    jizhu = post.get('jizhu', 0)
    # 根据用户名查询对象
    users = UserInfo.objects.filter(uname=uname)
    if len(users) == 1:
        s1 = sha1()
        s1.update(upwd.encode('utf-8'))
        if s1.hexdigest() == users[0].upwd:
            url = request.COOKIES.get('url', '/')
            red = HttpResponseRedirect(url)
            if jizhu != 0:
                red.set_cookie('uname', uname)
            else:
                red.set_cookie('uname', '', max_age=-1)
            request.session['user_id'] = users[0].id
            request.session['user_name'] = uname
            return red
        else:
            context = {'title': '用户登录', 'error_name': 0, 'error_pwd': 1, 'uname': uname, 'upwd': upwd}
            return render(request, 'df_user/login.html', context)
    else:
        context = {'title': '用户登录', 'error_name': 1, 'error_pwd': 0, 'uname': uname, 'upwd': upwd}
        return render(request, 'df_user/login.html', context)


@user_decorator.login
def info(request):
    uname = request.session.get('user_name')
    goods_list = []
    goods_ids = request.COOKIES.get('goods_ids', '')
    if goods_ids != '':
        goods_ids1 = goods_ids.split(',')
        for g in goods_ids1:
            goods_list.append(GoodsInfo.objects.get(id=int(g)))
    if uname:
        email = UserInfo.objects.get(id=request.session.get('user_id')).uemail
        address = UserInfo.objects.get(id=request.session.get('user_id')).uaddress
        return render(request, 'df_user/user_center_info.html', {'title': '用户中心', 'uname': uname, 'email': email,
                                                                 'address': address, 'page_name': 1, 'goods_list': goods_list})
    else:
        return redirect('/user/login')


@user_decorator.login
def order(request, index):
    if index == '':
        index = 1
    else:
        index = int(index)
    uid = request.session.get('user_id')
    order_list = OrderInfo.objects.filter(user_id=uid)
    for order1 in order_list:
        order1.odate = order1.odate.strftime("%Y-%m-%d %H:%M:%S")
        order1.detail = OrderDetailInfo.objects.filter(order_id=order1.oid)
        for good in order1.detail:
            good.good = GoodsInfo.objects.get(pk=good.id)

    order_list1 = Paginator(order_list, 2)
    order_list2 = order_list1.page(index)
    plist = order_list1.page_range

    context = {'uname': request.session.get('user_name'), 'title': '订单中心', 'page_name': 1,
               'order_list': order_list2, 'plist': plist, 'index': index}
    return render(request, 'df_user/user_center_order.html', context)


@user_decorator.login
def site(request):
    uid = request.session.get('user_id')
    if uid:
        user = UserInfo.objects.get(id=uid)
        if request.method == "POST":
            post = request.POST
            user.ushou = post.get('ushou')
            user.uyoubian = post.get('uyoubian')
            user.uaddress = post.get('uaddress')
            user.uphone = post.get('uphone')
            user.save()
        context = {'uname': request.session.get('user_name'), 'title': '收货地址', 'user': user, 'page_name': 1}
        return render(request, 'df_user/user_center_site.html', context)
    else:
        return redirect('/user/login/')


def logout(request):
    request.session.flush()
    return redirect('/')







