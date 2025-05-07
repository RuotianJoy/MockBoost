from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_cors import CORS
import sys
import os
import random
import json
import uuid
import redis
import time

import json
import os
import random
import json
import uuid
import redis
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.controller.UserServerController import UserServerController
from DeepSeek.DeepSeekApi import get_llm_response
from Email.get_email_api import send_email
from ASR.baidu_asr import BaiduASR
from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest
app = Flask(__name__)
CORS(app)

# Initialize components
user_controller = UserServerController()
# vosk = VoskRecognition()

# Redis 配置
REDIS_HOST = "r-bp162llfgqnxpesejnpd.redis.rds.aliyuncs.com"
REDIS_PORT = 6379
REDIS_PASSWORD = "Liao031221"

# 初始化 Redis 客户端
try:
    redis_client = redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        password=REDIS_PASSWORD,
        decode_responses=True,  # 自动解码为字符串
        socket_timeout=5,  # 添加超时设置
        socket_connect_timeout=5
    )
    # 测试连接
    redis_client.ping()
    print("Redis连接成功")
except Exception as redis_error:
    print(f"Redis连接失败: {str(redis_error)}")
    # 创建一个模拟的Redis客户端，避免应用崩溃
    class MockRedis:
        def get(self, key):
            return None
        def set(self, key, value):
            return True
        def ping(self):
            return True
    redis_client = MockRedis()

# 存储用户会话
user_sessions = {}
sqlflag = False

@app.route('/')
def index():
    return render_template('landing.html')

@app.route('/auth')
def auth():
    register = request.args.get('register', 'false').lower() == 'true'
    return render_template('auth.html', register=register)

@app.route('/chat')
def chat_page():
    # Check if user is authenticated via session or query parameter
    user_id = request.args.get('user_id')
    if not user_id:
        # Redirect to auth page if not authenticated
        return redirect(url_for('auth'))
    return render_template('chat.html')

@app.route('/how-it-works')
def how_it_works():
    return render_template('landing.html')

@app.route('/verify-auth', methods=['POST'])
def verify_auth():
    """Verify if a user is authenticated"""
    data = request.json
    user_id = data.get('user_id')
    
    if not user_id:
        return jsonify({'authenticated': False})
    
    try:
        # Check if the user exists in the database
        user_info = {'username': user_id}
        result = user_controller.find_user_by_name(user_id)
        
        # If user exists, they are authenticated
        if result and len(result) > 0:
            return jsonify({'authenticated': True})
        else:
            return jsonify({'authenticated': False})
    except Exception as e:
        print(f"Authentication verification error: {str(e)}")
        return jsonify({'authenticated': False})

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    login_data = {
        'username': data.get('username'),
        'password': data.get('password')
    }
    result = user_controller.findlogin_user_ServerStatus(login_data)
    if result:
        # 创建用户会话
        user_id = login_data['username']
        if user_id not in user_sessions:
            user_sessions[user_id] = {
                'messages': [
                    {"role": "system", "content": "You are an interviewer who use english and performs the duties of an interviewer according to different professional fields and the user's intended position, interviews users."}
                ],
                'conversation_id': None  # 初始化对话ID为None
            }
        return jsonify({'success': True, 'user_id': user_id})
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
    user_id = data.get('user_id', 'default_user')
    conversation_id = data.get('conversation_id')
    job = data.get('job', '')  # 获取职业参数
    major = data.get('major', '')  # 获取专业参数
    is_system_message = data.get('is_system_message', False)  # 是否是系统消息
    
    print(f"收到聊天请求: user_id={user_id}, message={message[:30]}..., conversation_id={conversation_id}")
    
    # 获取用户会话，如果不存在则创建
    if user_id not in user_sessions:
        user_sessions[user_id] = {
            'messages': [
                {"role": "system", "content": "You are an interviewer who use english and performs the duties of an interviewer according to different professional fields and the user's intended position, interviews users."}
            ],
            'conversation_id': None
        }
    
    # 获取用户的消息历史
    session = user_sessions[user_id]
    
    # 如果客户端明确要求创建新对话（conversation_id为null），则重置会话
    if conversation_id is None:
        print("客户端请求创建新对话")
        # 重置消息历史
        session['messages'] = [
            {"role": "system", "content": "You are an interviewer who use english and performs the duties of an interviewer according to different professional fields and the user's intended position, interviews users."}
        ]
        session['conversation_id'] = None
        conversation_id = None
    
    messages = session['messages']
    print(f"当前消息历史长度: {len(messages)}")
    
    # 如果没有对话ID或者是新对话，创建一个新的对话ID
    if not conversation_id and not session['conversation_id']:
        conversation_id = str(uuid.uuid4())
        session['conversation_id'] = conversation_id
        print(f"创建新对话ID: {conversation_id}")
        
        # 尝试将对话ID与用户关联并存储到数据库
        try:
            # 查询用户信息
            userinfo = {'username': user_id}
            uid = user_controller.getUid(userinfo)
            
            if uid and len(uid) > 0 and len(uid[0]) > 6:
                Uid = uid[0][6]
                info = {
                    'UUID': Uid,
                    'KIND': job or 'Interview',  # 使用传入的职业或默认值
                    'DIAKEY': conversation_id,
                }
                print(f"添加对话记录: {info}")
                
                # 调用数据库方法
                result = user_controller.addUid(info)
                print(f"数据库添加结果: {result}")
            else:
                print(f"无法获取用户ID，但会继续对话。Conversation ID: {conversation_id}")
        except Exception as db_error:
            print(f"数据库操作失败，但会继续对话: {str(db_error)}")
    elif not conversation_id:
        conversation_id = session['conversation_id']
        print(f"使用现有对话ID: {conversation_id}")
    
    try:
        # 从 Redis 中获取对话历史
        redis_history = None
        try:
            redis_history = redis_client.get(conversation_id)
            if redis_history:
                print(f"从Redis获取到历史记录，长度: {len(redis_history)}")
            else:
                print("Redis中没有找到历史记录")
        except Exception as redis_error:
            print(f"从Redis获取历史失败: {str(redis_error)}")
        
        if redis_history:
            # 如果 Redis 中有历史记录，使用 Redis 中的历史
            try:
                redis_messages = json.loads(redis_history)
                print(f"Redis历史消息数量: {len(redis_messages)}")
                
                # 检查是否已经包含当前消息
                message_already_exists = False
                for msg in redis_messages:
                    if msg.get('role') == 'user' and msg.get('content') == message:
                        message_already_exists = True
                        print("Redis历史中已包含当前消息，将使用现有历史")
                        break
                
                # 确保系统消息一致
                if redis_messages and len(redis_messages) > 0 and redis_messages[0]['role'] == 'system':
                    messages = redis_messages
                else:
                    # 如果 Redis 中的历史没有系统消息，添加系统消息
                    messages = [messages[0]] + redis_messages
                
                # 如果消息已存在，不再添加用户消息和生成回复
                if message_already_exists:
                    return jsonify({
                        'response': "消息已处理，请勿重复提交",
                        'conversation_id': conversation_id
                    })
            except json.JSONDecodeError:
                print(f"Redis数据解析失败: {redis_history}")
        
        # 打印当前消息列表中的所有用户消息，用于调试
        print("当前消息历史中的用户消息:")
        for i, msg in enumerate(messages):
            if msg.get('role') == 'user':
                print(f"  {i}: {msg.get('content')[:30]}...")
        
        # 检查是否已经存在相同的用户消息
        message_exists = False
        for msg in messages:
            if msg.get('role') == 'user' and msg.get('content') + " [Reminder: Maintain professional interviewer persona for Software Developer]" == message:
                message_exists = True
                print(f"检测到重复消息: {message[:30]}...")
                break
        
        if message_exists and not is_system_message:
            print("消息已存在，跳过处理")
            # 返回最后一条助手消息作为回复
            last_assistant_message = None
            for msg in reversed(messages):
                if msg.get('role') == 'assistant':
                    last_assistant_message = msg.get('content')
                    break
            
            return jsonify({
                'response': last_assistant_message or "消息已处理，请勿重复提交",
                'conversation_id': conversation_id
            })
        
        # 添加用户消息（如果不是系统消息）
        if not is_system_message:
            print(f"添加用户消息: {message[:30]}...")
            messages.append({"role": "user", "content": message})
        else:
            # 如果是系统消息，不添加到对话历史，但用于生成回复
            print("处理系统消息")
            temp_messages = messages.copy()
            temp_messages.append({"role": "user", "content": message})
            messages = temp_messages
        
        # 调用DeepSeek API获取回复
        print("调用LLM API获取回复")
        response = get_llm_response(message, messages, position=job)
        print(f"获取到回复: {response[:30]}...")
        
        # 添加AI回复
        messages.append({"role": "assistant", "content": response})
        
        # 更新会话历史
        session['messages'] = messages
        print(f"更新后的消息历史长度: {len(messages)}")
        
        # 将对话历史保存到 Redis
        try:
            # 确保消息格式正确
            messages_json = json.dumps(messages)
            
            # 尝试多次提交到Redis
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    # 保存到Redis
                    redis_result = redis_client.set(conversation_id, messages_json)
                    if redis_result:
                        print(f"Redis保存成功: {conversation_id}")
                        break
                    else:
                        print(f"Redis保存返回False，尝试重试 {attempt+1}/{max_retries}")
                except Exception as e:
                    print(f"Redis保存尝试 {attempt+1} 失败: {str(e)}")
                    if attempt == max_retries - 1:  # 最后一次尝试
                        raise
                    time.sleep(0.5)  # 短暂延迟后重试
        except Exception as redis_error:
            print(f"所有Redis保存尝试均失败: {str(redis_error)}")
        
        # 限制会话历史长度，防止过长
        if len(messages) > 20:  # 保留系统消息和最近的对话
            messages = [messages[0]] + messages[-19:]
            session['messages'] = messages
            try:
                redis_client.set(conversation_id, json.dumps(messages))
            except Exception as e:
                print(f"保存裁剪后的消息到Redis失败: {str(e)}")
        
        return jsonify({
            'response': response,
            'conversation_id': conversation_id
        })
    except Exception as e:
        print(f"聊天API错误: {str(e)}")
        return jsonify({
            'response': f"抱歉，我遇到了一些问题。错误信息: {str(e)}",
            'conversation_id': conversation_id
        })


@app.route('/clear-chat', methods=['POST'])
def clear_chat():
    data = request.json
    user_id = data.get('user_id', 'default_user')
    
    if user_id in user_sessions:
        # 获取当前对话ID
        conversation_id = user_sessions[user_id].get('conversation_id')
        
        # 保留系统消息，清除其他对话
        system_message = user_sessions[user_id]['messages'][0]
        user_sessions[user_id]['messages'] = [system_message]

        # 创建新的对话ID
        new_conversation_id = str(uuid.uuid4())
        user_sessions[user_id]['conversation_id'] = new_conversation_id
        
        return jsonify({'success': True, 'conversation_id': new_conversation_id})
    
    return jsonify({'success': False, 'message': '未找到用户会话'})

@app.route('/user-profile', methods=['POST'])
def user_profile():
    data = request.json
    user_name = data.get('user_id')
    print(user_name)
    if not user_name:
        return jsonify({'success': False, 'message': '未提供用户ID'})
    
    try:
        # 查询用户信息
        user_info = user_controller.find_user_by_name(user_name)
        user_info = user_info[0]
        if user_info:
            # 移除敏感信息
            if 'Password' in user_info:
                del user_info['Password']
            user_info = {
                'Name': user_info[1],
                'Email': user_info[3],
                'Major': user_info[4],
                'Job': user_info[5],
                'UUID': user_info[6],
            }
            return jsonify({'success': True, 'user_info': user_info})
        else:
            return jsonify({'success': False, 'message': '未找到用户信息'})
    except Exception as e:
        print(f"获取用户信息错误: {str(e)}")
        return jsonify({'success': False, 'message': f'获取用户信息失败: {str(e)}'})

@app.route('/user-history', methods=['POST'])
def user_history():
    data = request.json
    user_id = data.get('user_id')
    
    if not user_id:
        return jsonify({'success': False, 'message': '未提供用户ID'})
    
    try:
        # 查询用户信息
        userinfo = {'username': user_id}
        uid_result = user_controller.getUid(userinfo)
        
        if uid_result and len(uid_result) > 0 and len(uid_result[0]) > 6:
            Uid = uid_result[0][6]
            userdata = {"Uid": Uid}
            
            # 获取对话历史
            history_data = user_controller.find_dialog_info(userdata)
            
            if history_data:
                # 格式化历史数据
                formatted_history = []
                for item in history_data:
                    formatted_history.append({
                        'uuid': item[0],
                        'mode': item[1],
                        'dialog_id': item[2]
                    })
                
                return jsonify({'success': True, 'history': formatted_history})
            else:
                return jsonify({'success': True, 'history': []})
        else:
            return jsonify({'success': False, 'message': '未找到用户ID'})
    except Exception as e:
        print(f"获取用户历史对话错误: {str(e)}")
        return jsonify({'success': False, 'message': f'获取历史对话失败: {str(e)}'})

@app.route('/chat-history', methods=['POST'])
def chat_history():
    data = request.json
    dialog_id = data.get('dialog_id')
    
    if not dialog_id:
        return jsonify({'success': False, 'message': '未提供对话ID'})
    
    try:
        # 测试Redis连接
        if not test_redis_connection():
            return jsonify({'success': False, 'message': 'Redis连接失败'})
        
        # 从Redis获取对话历史，添加重试机制
        max_retries = 3
        chat_history = None
        
        for attempt in range(max_retries):
            try:
                chat_history = redis_client.get(dialog_id)
                if chat_history:
                    break
                print(f"Redis获取历史返回空，尝试重试 {attempt+1}/{max_retries}")
            except Exception as e:
                print(f"Redis获取历史尝试 {attempt+1} 失败: {str(e)}")
                if attempt == max_retries - 1:  # 最后一次尝试
                    raise
                time.sleep(0.5)  # 短暂延迟后重试
        
        if chat_history:
            try:
                # 解析JSON
                messages = json.loads(chat_history)
                return jsonify({'success': True, 'messages': messages})
            except json.JSONDecodeError as json_error:
                print(f"解析Redis数据失败: {str(json_error)}")
                return jsonify({'success': False, 'message': f'解析对话历史失败: {str(json_error)}'})
        else:
            # 如果Redis中没有找到，尝试从用户会话中查找
            for user_id, session in user_sessions.items():
                if session.get('conversation_id') == dialog_id:
                    return jsonify({'success': True, 'messages': session.get('messages', [])})
            
            return jsonify({'success': False, 'message': '未找到对话历史'})
    except Exception as e:
        print(f"获取对话历史错误: {str(e)}")
        return jsonify({'success': False, 'message': f'获取对话历史失败: {str(e)}'})

@app.route('/test-db', methods=['GET'])
def test_db():
    """测试数据库连接"""
    results = {
        'mysql': False,
        'redis': False,
        'mysql_error': None,
        'redis_error': None
    }
    
    # 测试MySQL连接
    try:
        # 简单查询
        result = user_controller.test_connection()
        results['mysql'] = True
        results['mysql_result'] = result
    except Exception as e:
        results['mysql_error'] = str(e)
    
    # 测试Redis连接
    try:
        # 设置测试值
        test_key = 'test_connection'
        test_value = 'success'
        redis_client.set(test_key, test_value)
        # 读取测试值
        read_value = redis_client.get(test_key)
        results['redis'] = (read_value == test_value)
        results['redis_result'] = read_value
    except Exception as e:
        results['redis_error'] = str(e)
    
    return jsonify(results)

# Redis 连接测试和重连机制
def test_redis_connection():
    """测试Redis连接，如果失败则尝试重连"""
    global redis_client
    
    try:
        # 测试连接
        redis_client.ping()
        return True
    except Exception as e:
        print(f"Redis连接测试失败: {str(e)}")
        
        # 尝试重新连接
        try:
            redis_client = redis.Redis(
                host=REDIS_HOST,
                port=REDIS_PORT,
                password=REDIS_PASSWORD,
                decode_responses=True,
                socket_timeout=5,
                socket_connect_timeout=5
            )
            redis_client.ping()
            print("Redis重连成功")
            return True
        except Exception as reconnect_error:
            print(f"Redis重连失败: {str(reconnect_error)}")
            return False

# 定期测试Redis连接
@app.before_request
def check_redis_connection():
    """在每个请求前检查Redis连接"""
    if request.endpoint in ['chat', 'chat_history']:  # 只在需要Redis的路由中检查
        test_redis_connection()

@app.route('/get-tts-token', methods=['GET'])
def get_tts_token():
    try:
        print("Getting TTS token from Aliyun...")
        # 创建AcsClient实例
        api_key = os.getenv("API_KEY_ali")
        if not api_key:
            raise ValueError("API_KEY is not set")
        client = AcsClient(
            "LTAI5tNTwR6WS7wQuRV7LJ6X",
            api_key,
            "cn-shanghai"
        )

        # 创建request，并设置参数
        request = CommonRequest()
        request.set_method('POST')
        request.set_domain('nls-meta.cn-shanghai.aliyuncs.com')
        request.set_version('2019-02-28')
        request.set_action_name('CreateToken')

        print("Sending token request to Aliyun...")
        response = client.do_action_with_exception(request)
        response_str = response.decode('utf-8')
        print(f"Aliyun response: {response_str}")
        
        response_json = json.loads(response_str)
        
        if 'Token' in response_json and 'Id' in response_json['Token']:
            token = response_json['Token']['Id']
            expire_time = response_json['Token']['ExpireTime']
            
            print(f"Successfully obtained token: {token} (expires: {expire_time})")
            return jsonify({
                'success': True,
                'token': token,
                'expire_time': expire_time,
                'appkey': 'Fs8yrx1nEz5CQJEr'  # Return the app key as well
            })
        else:
            print(f"Failed to get token, response does not contain Token/Id: {response_json}")
            return jsonify({
                'success': False,
                'message': 'Failed to get token from Aliyun',
                'response': response_json
            })
    except Exception as e:
        error_msg = str(e)
        print(f"Error getting TTS token: {error_msg}")
        return jsonify({
            'success': False,
            'message': error_msg,
            'error_type': type(e).__name__
        })

if __name__ == '__main__':
    app.run(debug=True, port=8080)
