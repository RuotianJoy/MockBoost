from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import sys
import os
import random

# Add parent directory to Python path for importing project modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.controller.UserServerController import UserServerController

from TTSandASR.ChatTTs import ChatTTS

from Email.get_email_api import send_email

app = Flask(__name__)
CORS(app)

# Initialize components
user_controller = UserServerController()
# deepseek = DeepSeek()
chat_tts = ChatTTS()
# vosk = VoskRecognition()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    login_data = {
        'username': data.get('username'),
        'password': data.get('password')
    }
    result = user_controller.findlogin_user_ServerStatus(login_data)
    if result:
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'message': '用户名或密码错误'})

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')
    job = data.get('job')
    major = data.get('major')
    verification_code = data.get('verification_code')
    
    # 验证验证码
    if not verification_code or int(verification_code) != int(data.get('stored_code', 0)):
        return jsonify({'success': False, 'message': '验证码错误'})
    
    # 创建用户数据
    userid = 'U' + str(random.randint(100001, 999999))
    user_data = {
        'Name': username,
        'Password': password,
        'Email': email,
        'Major': major,
        'Job': job,
        'UUID': userid
    }
    
    result = user_controller.adduser_user_ServerStatus(user_data)
    if result:
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'message': '用户名已存在或注册失败'})

@app.route('/send-verification', methods=['POST'])
def send_verification():
    data = request.json
    email = data.get('email')
    
    if not email:
        return jsonify({'success': False, 'message': '请输入邮箱地址'})
    
    try:
        verification_code = send_email(email)
        return jsonify({'success': True, 'code': verification_code})
    except Exception as e:
        return jsonify({'success': False, 'message': f'发送验证码失败: {str(e)}'})

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    message = data.get('message')
    # response = deepseek.get_response(message)
    return jsonify({'response': 1})

@app.route('/text-to-speech', methods=['POST'])
def text_to_speech():
    data = request.json
    text = data.get('text')
    audio_data = chat_tts.text_to_speech(text)
    return jsonify({'audio_data': audio_data})

@app.route('/speech-to-text', methods=['POST'])
def speech_to_text():
    audio_data = request.files['audio'].read()
    # text = vosk.recognize_speech(audio_data)
    return jsonify({'text': 1})

if __name__ == '__main__':
    app.run(debug=True)