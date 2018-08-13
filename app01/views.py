from django.shortcuts import render,redirect
from app01 import models
from django.http import JsonResponse, HttpResponse
from django.conf import settings

# Create your views here.
def login(request):
    """
    用户登陆
    :param request:
    :return:
    """
    if request.method == 'GET':
        return render(request, 'login.html')
    user = request.POST.get('user')
    pwd = request.POST.get('pwd')

    obj = models.UserInfo.objects.filter(name=user, pwd=pwd).first()
    if obj:
        request.session['user_info'] = {'id': obj.id, 'name': obj.name}
        return redirect('/index/')

    return render(request, 'login.html', {'msg': '用户名或密码错误'})

def index(request):
    """
    首页
    :param request:
    :return:
    """
    return render(request,"index.html")

def get_qrcode(request):
    """
    访问获取用户基本信息接口
    需要接收3个参数
    :param request:
    :return:
    """
    ret = {'status': True, 'data': None}
    # appid 是自己的appid
    # redirect_uri 是回调地址,腾讯服务器会访问它
    # state是自定义的,变量名可以随意
    access_url = "https://open.weixin.qq.com/connect/oauth2/authorize?appid={appid}&redirect_uri={redirect_uri}&response_type=code&scope=snsapi_userinfo&state={state}#wechat_redirect"
    url = access_url.format(
        appid=settings.WECHAT_PUBLIC.get('appid'),
        redirect_uri=settings.WECHAT_PUBLIC.get('redirect_uri'),  # 跳转会我的网站
        state=request.session['user_info']['id']  # 用户ID
    )
    ret['data'] = url  # 生成url

    return JsonResponse(ret)  # 返回给ajax

def get_wx_id(request):
    """
    获取微信ID，并更新到数据库
    :param request:
    :return:
    """
    import requests

    code = request.GET.get("code")
    state = request.GET.get("state")

    # 获取该用户openId(用户唯一，用于给用户发送消息)
    r1 = requests.get(
        url="https://api.weixin.qq.com/sns/oauth2/access_token",
        params={
            "appid": settings.WECHAT_PUBLIC.get('appid'),
            "secret": settings.WECHAT_PUBLIC.get('secret'),
            "code": code,
            "grant_type": 'authorization_code',
        }
    ).json()
    # 获取的到openid表示用户授权成功
    wx_id = r1.get("openid")
    user = models.UserInfo.objects.filter(id=state).first()
    # 判断用户id不为空
    if not user.wx_id:
        user.wx_id = wx_id
        user.save()  # 修改微信id

    return HttpResponse('授权成功')

def send(request):
    """
    发送消息
    :param request:
    :return:
    """
    user_list = models.UserInfo.objects.all()

    return render(request, 'send.html', {'user_list': user_list})

def send_msg(request):
    """
    发送消息
    :param request:
    :return:
    """
    id = request.session['user_info']['id']
    obj = models.UserInfo.objects.filter(id=id).first()

    import json
    import requests
    # 1. 伪造浏览器向 https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential... 发送GET请求，并获取token
    r1 = requests.get(
        url="https://api.weixin.qq.com/cgi-bin/token",
        params={
            "grant_type": "client_credential",
            "appid": settings.WECHAT_PUBLIC.get('appid'),
            "secret": settings.WECHAT_PUBLIC.get('secret'),
        }
    )

    access_token = r1.json().get('access_token')

    body = {
        "touser": obj.wx_id,
        "template_id": 'OxCBr-98eVMkTLKb0ZGpLGK5mNnLMLoEZG2MsmR3Q_Q',
        "data": {
            "user": {
                "value": "Hello Kitty",
                "color": "#173177"
            }
        }
    }

    r2 = requests.post(
        url="https://api.weixin.qq.com/cgi-bin/message/template/send",
        params={
            'access_token': access_token
        },
        data=json.dumps(body)
    )
    print(r2.text)
    return HttpResponse('发送成功')