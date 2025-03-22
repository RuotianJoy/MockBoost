#! /usr/bin/env python
# coding=utf-8
import os
import time
import json
from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest


api_key = os.getenv("API_KEY_ali")
if not api_key:
    raise ValueError("API_KEY is not set")


# 创建AcsClient实例
client = AcsClient(
   "LTAI5tNTwR6WS7wQuRV7LJ6X",
   api_key,
   "cn-shanghai"
);

# 创建request，并设置参数。
request = CommonRequest()
request.set_method('POST')
request.set_domain('nls-meta.cn-shanghai.aliyuncs.com')
request.set_version('2019-02-28')
request.set_action_name('CreateToken')

try : 
   response = client.do_action_with_exception(request)
   print(response)

   jss = json.loads(response)
   if 'Token' in jss and 'Id' in jss['Token']:
      token = jss['Token']['Id']
      expireTime = jss['Token']['ExpireTime']
      print("token = " + token)
      print("expireTime = " + str(expireTime))
except Exception as e:
   print(e)