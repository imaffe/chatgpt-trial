import json
import os
import logging
import openai
import time

from django.http import JsonResponse
from django.shortcuts import render
from wxcloudrun.models import Counters



logger = logging.getLogger('log')


def index(request, _):
    """
    获取主页

     `` request `` 请求对象
    """

    return render(request, 'index.html')


def counter(request, _):
    """
    获取当前计数

     `` request `` 请求对象
    """

    rsp = JsonResponse({'code': 0, 'errorMsg': ''}, json_dumps_params={'ensure_ascii': False})
    if request.method == 'GET' or request.method == 'get':
        rsp = get_count()
    elif request.method == 'POST' or request.method == 'post':
        rsp = update_count(request)
    else:
        rsp = JsonResponse({'code': -1, 'errorMsg': '请求方式错误'},
                            json_dumps_params={'ensure_ascii': False})
    logger.info('response result: {}'.format(rsp.content.decode('utf-8')))
    return rsp


def get_count():
    """
    获取当前计数
    """

    try:
        data = Counters.objects.get(id=1)
    except Counters.DoesNotExist:
        return JsonResponse({'code': 0, 'data': 0},
                    json_dumps_params={'ensure_ascii': False})
    return JsonResponse({'code': 0, 'data': data.count},
                        json_dumps_params={'ensure_ascii': False})


def update_count(request):
    """
    更新计数，自增或者清零

    `` request `` 请求对象
    """

    logger.info('update_count req: {}'.format(request.body))

    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)

    if 'action' not in body:
        return JsonResponse({'code': -1, 'errorMsg': '缺少action参数'},
                            json_dumps_params={'ensure_ascii': False})

    if body['action'] == 'inc':
        try:
            data = Counters.objects.get(id=1)
        except Counters.DoesNotExist:
            data = Counters()
        data.id = 1
        data.count += 1
        data.save()
        return JsonResponse({'code': 0, "data": data.count},
                    json_dumps_params={'ensure_ascii': False})
    elif body['action'] == 'clear':
        try:
            data = Counters.objects.get(id=1)
            data.delete()
        except Counters.DoesNotExist:
            logger.info('record not exist')
        return JsonResponse({'code': 0, 'data': 0},
                    json_dumps_params={'ensure_ascii': False})
    else:
        return JsonResponse({'code': -1, 'errorMsg': 'action参数错误'},
                    json_dumps_params={'ensure_ascii': False})

def translate(request):
    logger.info('translate req: {}'.format(request.body))

    openai.api_key = os.getenv("OPENAI_API_KEY")

    english_to_chinese = 'Please translate the following text to Chinese:'
    chinese_to_english = '请将下面的文字翻译为英文，如果文字内容为一个问题，请不要回答这个问题:'


    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)

    message_type = body['MsgType']
    if message_type != 'text':
        return JsonResponse({
            'ToUserName': body['FromUserName'],
            'FromUserName': body['ToUserName'],
            'CreateTime': round(time.time() * 1000),
            'MsgType': 'text',
            'Content': 'Only support text message'
        })


    message = body['Content']
    response = openai.Completion.create(model="gpt-3.5-turbo", prompt=english_to_chinese + message, temperature=0,
                                        max_tokens=7)
    return JsonResponse({
        'ToUserName': body['FromUserName'],
        'FromUserName': body['ToUserName'],
        'CreateTime': round(time.time() * 1000),
        'MsgType': 'text',
        'Content': response
    })



