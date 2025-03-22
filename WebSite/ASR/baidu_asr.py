import websocket
import json
import time
import threading
import base64
import uuid
import requests
import os

# 百度语音识别API配置
APPID = 118057093
API_KEY = "8GKydTmb9V6iVlyMGk3BEmym"
SECRET_KEY = "你的百度语音识别Secret Key"  # 请替换为你的Secret Key

# 音频参数
DEV_PID = 1737  # 识别模型，1737为中文普通话模型
CUID = "cuid-mockboost"  # 设备ID
FORMAT = "pcm"   # 音频格式
SAMPLE_RATE = 16000  # 采样率

class BaiduASR:
    def __init__(self):
        self.token = None
        self.token_expiry = 0
        self.get_token()
    
    def get_token(self):
        """获取百度语音识别的token"""
        current_time = time.time()
        
        # 如果token未过期，直接返回
        if self.token and current_time < self.token_expiry:
            return self.token
            
        url = f"https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id={API_KEY}&client_secret={SECRET_KEY}"
        try:
            response = requests.post(url)
            result = response.json()
            self.token = result.get("access_token")
            # token有效期通常为30天，这里设置为29天以确保安全
            self.token_expiry = current_time + 29 * 24 * 3600
            return self.token
        except Exception as e:
            print(f"获取百度token失败: {str(e)}")
            return None
    
    def recognize_file(self, audio_file_path):
        """使用REST API识别音频文件"""
        token = self.get_token()
        if not token:
            return {"success": False, "message": "无法获取百度语音识别token"}
        
        try:
            # 读取音频文件
            with open(audio_file_path, 'rb') as f:
                audio_data = f.read()
            
            # 将音频数据转为base64编码
            speech_base64 = base64.b64encode(audio_data).decode('utf-8')
            
            # 调用百度语音识别API
            url = "https://vop.baidu.com/server_api"
            headers = {'Content-Type': 'application/json'}
            data = {
                "format": "wav",
                "rate": SAMPLE_RATE,
                "channel": 1,
                "cuid": CUID,
                "token": token,
                "speech": speech_base64,
                "len": len(audio_data)
            }
            
            response = requests.post(url, headers=headers, data=json.dumps(data))
            result = response.json()
            
            # 解析识别结果
            if result.get('err_no') == 0 and result.get('result'):
                recognized_text = result['result'][0]
                return {"success": True, "text": recognized_text}
            else:
                error_msg = result.get('err_msg', '未知错误')
                print(f"语音识别API返回错误: {error_msg}")
                return {"success": False, "message": f"语音识别失败: {error_msg}"}
                
        except Exception as e:
            print(f"语音识别异常: {str(e)}")
            return {"success": False, "message": f"语音识别失败: {str(e)}"}
    
    def create_websocket_connection(self, callback=None):
        """创建WebSocket连接用于实时语音识别"""
        # 生成唯一的SN
        sn = str(uuid.uuid4())
        ws_url = f"wss://vop.baidu.com/realtime_asr?sn={sn}"
        
        # 初始化WebSocket
        websocket.enableTrace(False)
        
        def on_message(ws, message):
            try:
                result_json = json.loads(message)
                if callback:
                    callback(result_json)
                else:
                    if result_json["type"] == "FIN_TEXT":
                        print("最终识别结果:", result_json.get("result", result_json.get("err_msg", "")))
                    elif result_json["type"] == "MID_TEXT":
                        print("临时识别结果:", result_json["result"])
            except json.JSONDecodeError:
                print("解析消息失败:", message)
        
        def on_error(ws, error):
            print("WebSocket错误:", error)
        
        def on_close(ws, close_status_code, close_msg):
            print("WebSocket连接关闭")
        
        def on_open(ws):
            print("WebSocket连接已建立")
            
            # 发送开始参数帧
            start_data = {
                "type": "START",
                "data": {
                    "appid": APPID,
                    "appkey": API_KEY,
                    "dev_pid": DEV_PID,
                    "lm_id": 0,
                    "cuid": CUID,
                    "format": FORMAT,
                    "sample": SAMPLE_RATE
                }
            }
            ws.send(json.dumps(start_data))
        
        ws = websocket.WebSocketApp(ws_url,
                                  on_message=on_message,
                                  on_error=on_error,
                                  on_close=on_close,
                                  on_open=on_open)
        
        # 在新线程中运行WebSocket
        ws_thread = threading.Thread(target=ws.run_forever)
        ws_thread.daemon = True
        ws_thread.start()
        
        # 等待连接建立
        time.sleep(1)
        return ws
    
    def send_audio_data(self, ws, audio_data):
        """发送音频数据到WebSocket"""
        if ws and ws.sock:
            try:
                ws.send(audio_data, websocket.ABNF.OPCODE_BINARY)
                return True
            except Exception as e:
                print(f"发送音频数据失败: {str(e)}")
                return False
        return False
    
    def end_recognition(self, ws):
        """结束语音识别"""
        if ws and ws.sock:
            try:
                end_data = {"type": "END"}
                ws.send(json.dumps(end_data))
                return True
            except Exception as e:
                print(f"发送结束帧失败: {str(e)}")
                return False
        return False