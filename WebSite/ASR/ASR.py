import websocket
import json
import time
import threading
import pyaudio
import keyboard  # 添加keyboard库
import uuid  # 添加uuid库生成唯一SN

# 替换为你的百度语音识别应用的APPID和API Key
APPID = 118057093
API_KEY = "8GKydTmb9V6iVlyMGk3BEmym"

# 音频参数
DEV_PID = 1737  # 识别模型，1737为中文普通话模型
CUID = "cuid-16546138324"  # 随机设备ID
FORMAT = "pcm"   # 音频格式
SAMPLE_RATE = 16000  # 采样率
CHUNK = 1024  # 每次读取的音频块大小

# 控制变量
is_recording = False
recording_thread = None
ws = None
audio_stream = None

# 初始化PyAudio
p = pyaudio.PyAudio()

# 打开麦克风音频流
def open_microphone_stream():
    global audio_stream
    audio_stream = p.open(format=pyaudio.paInt16,
                          channels=1,
                          rate=SAMPLE_RATE,
                          input=True,
                          frames_per_buffer=CHUNK)

# 创建新的WebSocket连接
def create_websocket_connection():
    global ws
    # 生成唯一的SN
    sn = str(uuid.uuid4())
    ws_url = f"wss://vop.baidu.com/realtime_asr?sn={sn}"
    
    # 初始化WebSocket - 禁用跟踪功能
    websocket.enableTrace(False)  # 修改为False，禁用详细的WebSocket调试输出
    ws = websocket.WebSocketApp(ws_url,
                              on_message=on_message,
                              on_open=on_open,
                              on_close=on_close,
                              on_error=on_error)
    
    # 运行WebSocket
    ws_thread = threading.Thread(target=ws.run_forever)
    ws_thread.daemon = True
    ws_thread.start()
    
    # 等待连接建立
    time.sleep(1)
    return ws

# 发送音频数据线程
def send_audio():
    global ws, audio_stream, is_recording
    try:
        # 确保WebSocket连接存在
        if ws is None or ws.sock is None:
            print("创建新的WebSocket连接...")
            ws = create_websocket_connection()
            time.sleep(1)  # 等待连接建立
        
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
        if ws and ws.sock:
            try:
                ws.send(json.dumps(start_data))
                print("发送开始参数帧")
                print("正在录音，请说话...")

                # 持续读取麦克风音频数据并发送
                while is_recording:
                    try:
                        data = audio_stream.read(CHUNK, exception_on_overflow=False)
                        if data and ws and ws.sock:
                            ws.send(data, websocket.ABNF.OPCODE_BINARY)
                            print("发送音频数据帧", end="\r")
                        else:
                            break
                    except websocket.WebSocketConnectionClosedException:
                        print("\n发送音频时连接已关闭")
                        break
                    except Exception as e:
                        print(f"\n发送音频数据时出错: {e}")
                        break
                    time.sleep(0.01)  # 添加短暂延迟，减轻服务器负担

                # 发送结束帧
                if ws and ws.sock:
                    end_data = {
                        "type": "END"
                    }
                    ws.send(json.dumps(end_data))
                    print("\n发送结束帧")
            except websocket.WebSocketConnectionClosedException:
                print("WebSocket连接已关闭")
            except Exception as e:
                print(f"发送数据异常: {e}")
        else:
            print("WebSocket连接不可用")
    except Exception as e:
        print(f"音频发送线程异常: {e}")

# WebSocket连接回调
def on_open(ws):
    print("连接已建立")
    print("按下空格键开始录音，再次按下空格键结束录音")

# 接收识别结果的回调函数
def on_message(ws, message):
    try:
        result_json = json.loads(message)
        if result_json["type"] == "FIN_TEXT":
            print("最终识别结果:", result_json.get("result", result_json.get("err_msg", "")))
        elif result_json["type"] == "MID_TEXT":
            print("临时识别结果:", result_json["result"])
    except json.JSONDecodeError:
        print("解析消息失败:", message)

# WebSocket关闭回调
def on_close(ws, close_status_code, close_msg):
    print("连接已关闭")

# WebSocket错误回调
def on_error(ws, error):
    print("发生错误:", error)

# 处理空格键按下事件
def on_space_press(e):
    global is_recording, recording_thread, ws
    
    if e.name == 'space':
        if not is_recording:
            # 开始录音
            is_recording = True
            # 创建新的WebSocket连接
            ws = create_websocket_connection()
            # 启动录音线程
            recording_thread = threading.Thread(target=send_audio)
            recording_thread.start()
        else:
            # 结束录音
            is_recording = False
            print("\n停止录音")
            # 关闭当前WebSocket连接
            if ws:
                try:
                    ws.close()
                except:
                    pass

# 打开麦克风音频流
open_microphone_stream()

# 注册空格键事件
keyboard.on_press(on_space_press)

# 主循环，保持程序运行
try:
    print("程序已启动，按下空格键开始/停止录音，按Ctrl+C退出")
    while True:
        time.sleep(0.1)
except KeyboardInterrupt:
    print("程序退出")
    is_recording = False
    if recording_thread and recording_thread.is_alive():
        recording_thread.join(1)
    if ws:
        ws.close()

# 关闭麦克风音频流
audio_stream.stop_stream()
audio_stream.close()
p.terminate()