# encoding: utf-8
import json

import requests
import socket


class ApiUtil:
    def __init__(self):
        pass

    @classmethod
    def get(cls, url):
        url = 'https://www.jenue.cn' + url
        header = {
            'token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6MjE0LCJpYXQiOjE2NTI2NjcwNTN9.rxAc2U0QvKYEfTFzpaVon55VzzcluXkSrXbfjLCrnxg',
            'Accept': 'application/json;charset=utf-8'}
        try:
            response = requests.get(url, headers=header, timeout=1000)
        except:
            print("网络无法连接get")
            return False

        return response

    @classmethod
    def getAllUri(cls, url, act="get"):
        # 测试改动
        url = 'https://www.jenue.cn' + url
        print(url)
        header = {
            'token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6MjE0LCJpYXQiOjE2NTI2NjcwNTN9.rxAc2U0QvKYEfTFzpaVon55VzzcluXkSrXbfjLCrnxg',
            'Accept': 'application/json;charset=utf-8'}
        try:
            if act == "get":
                response = requests.get(url, headers=header, timeout=1000)
            else:
                response = requests.post(url, headers=header, timeout=1000)
        except:
            print("网络无法连接get")
            return False

        return response

    @classmethod
    def post(cls, url, data, token):
        print(f'data:{data}')
        url = 'https://www.jenue.cn' + url
        header = {
            'token': token,
            'tokenType': 'api',
            'Content-Type': 'application/json;charset=UTF-8',
            'User-Agent': 'Mozilla/5.0(Windows NT 10.0;WOW64) AppleWebKit/537.36(KHTML, likeGecko) Chrome/77.0.3865.90Safari/537.36'}
        try:
            response = requests.post(url, headers=header, json=data, timeout=1000)
        except:
            print("网络无法连接post")
            return False
        return response

    @classmethod
    def put(cls, url, data):
        url = 'https://www.jenue.cn' + url
        print(url)
        header = {
            'token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6MjE0LCJpYXQiOjE2NTI2NjcwNTN9.rxAc2U0QvKYEfTFzpaVon55VzzcluXkSrXbfjLCrnxg',
            'Accept': 'application/json;charset=utf-8'}
        try:
            response = requests.put(url, headers=header, data=data, timeout=1000)
        except:
            print("网络无法连接put")
            return False
        return response

    @classmethod
    def upload(cls, url, filename, filepath, type):
        url = 'https://www.jenue.cn' + url
        header = {
            'token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6MjE0LCJpYXQiOjE2NTI2NjcwNTN9.rxAc2U0QvKYEfTFzpaVon55VzzcluXkSrXbfjLCrnxg',
            'Accept': 'application/json;charset=utf-8'}

        if type == "excel":
            files = [('file', (
                filename, open(filepath, 'rb'),
                'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'))]
        elif type == "image":
            files = [('file', (
                filename, open(filepath, 'rb'),
                'image/png'))]

        try:
            response = requests.post(url, headers=header, files=files, timeout=1000)
            # print(response.text)
        except:
            print("connect error")
            return {}

        return response

    @classmethod
    def uploadOld(cls, url, filename, filepath, type):
        url = 'https://www.jenue.cn' + url
        header = {
            'token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6MjE0LCJpYXQiOjE2NTI2NjcwNTN9.rxAc2U0QvKYEfTFzpaVon55VzzcluXkSrXbfjLCrnxg',
            'Accept': 'application/json;charset=utf-8'}

        if type == "excel":
            files = [('file', (
                filename, open(filepath, 'rb'),
                'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'))]
        elif type == "image":
            files = [('file', (
                filename, open(filepath, 'rb'),
                'image/png'))]

        try:
            response = requests.post(url, headers=header, files=files, timeout=1000)
            # print(response.text)
        except:
            print("connect error")
            return {}

        return response

    @classmethod
    def uploadMore(cls, url, filenames, filepaths, filekeys, type):
        url = 'https://www.jenue.cn' + url
        header = {
            'token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6MjE0LCJpYXQiOjE2NTI2NjcwNTN9.rxAc2U0QvKYEfTFzpaVon55VzzcluXkSrXbfjLCrnxg',
            'Accept': 'application/json;charset=utf-8'}

        files = []
        try:
            for i in range(0, len(filenames)):
                if type == "excel":
                    files.append((filekeys[i], (
                        filenames[i], open(filepaths[i], 'rb'),
                        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')))
                elif type == "image":
                    files.append((filekeys[i], (
                        filenames[i], open(filepaths[i], 'rb'),
                        'image/png')))
            try:
                response = requests.post(url, headers=header, files=files, timeout=3000)
            except:
                print("connect error")
                return {}
        except FileNotFoundError:
            print("file not find")
            return False

        return response

    @classmethod
    def download(cls, url, img_path):
        try:
            # 发送get请求图片url
            r = requests.get(url)
            # wb 以二进制打开文件并写入，文件名不存在会创建
            print(img_path)
            with open(img_path, 'wb') as f:
                f.write(r.content)  # 写入二进制内容
        except:
            return False
        return True

    @classmethod
    def uploaddata(cls, url, data):
        url = 'https://www.jenue.cn' + url
        header = {
            'token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6MjE0LCJpYXQiOjE2NTI2NjcwNTN9.rxAc2U0QvKYEfTFzpaVon55VzzcluXkSrXbfjLCrnxg',
            'Accept': 'application/json;charset=utf-8'}
        data = json.dumps(data, ensure_ascii=False)
        try:
            response = requests.post(url, headers=header, data=data.encode(encoding='utf-8'), timeout=1000)
        except:
            print("connect error")
            return {}
        return response

    @classmethod
    def upload15000(cls, url, filename, filepath, type):
        url = 'http://39.98.60.198:15000' + url
        header = {
            'token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6MjE0LCJpYXQiOjE2NTI2NjcwNTN9.rxAc2U0QvKYEfTFzpaVon55VzzcluXkSrXbfjLCrnxg',
            'Accept': 'application/json;charset=utf-8'}
        if type == "excel":
            files = [('file', (
                filename, open(filepath, 'rb'),
                'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'))]
            try:
                response = requests.post(url, headers=header, files=files, timeout=1000)
            except:
                print("connect error")
                return {}

        return response

    @classmethod
    def getOtherUri(cls, url, act="get"):
        header = {}
        try:
            if act == "get":
                response = requests.get(url, headers=header, timeout=1000)
            else:
                response = requests.post(url, headers=header, timeout=1000)
        except:
            print("网络无法连接get")
            return False

        return response