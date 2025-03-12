import os

from PyQt6.QtCore import QThread, pyqtSignal
import torch
import redis
import uuid
import json
import traceback
from transformers import AutoTokenizer, AutoModelForCausalLM, GenerationConfig
from db.controller.UserServerController import UserServerController

class DataThread(QThread):
    """数据获取线程，用于处理与模型和数据库的交互"""
    data_ready = pyqtSignal(str, str)  # 数据准备好信号，传递回答内容和对话ID
    error_occurred = pyqtSignal(str)   # 错误信号，传递错误信息
    
    # 全局变量，用于存储已初始化的模型、分词器和Redis客户端
    _redis_client = None
    _tokenizer = None
    _model = None
    
    def __init__(self, user_input, conversation_id=None, username=None, mode=None):
        super().__init__()
        self.user_input = user_input
        self.conversation_id = conversation_id
        self.username = username
        self.mode = mode
        
        # Redis配置
        self.REDIS_HOST = "r-bp162llfgqnxpesejnpd.redis.rds.aliyuncs.com"  # 阿里云 Redis 地址
        self.REDIS_PORT = 6379               # Redis 端口
        self.REDIS_PASSWORD = "Liao031221"  # Redis 密码
        self.MODEL_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "Training", "Deepseek")

  # 模型路径
        
    def run(self):
        try:
            # 如果模型尚未初始化，则进行初始化
            if DataThread._redis_client is None or DataThread._tokenizer is None or DataThread._model is None:
                print("初始化模型中...")
                DataThread._redis_client, DataThread._tokenizer, DataThread._model = self.initialize_chatbot(
                    self.REDIS_HOST, self.REDIS_PORT, self.REDIS_PASSWORD, self.MODEL_PATH)
                print("模型初始化完成")
            
            # 直接使用已初始化的模型进行对话
            response, conversation_id = self.chat_with_model(
                self.user_input, self.conversation_id, 
                DataThread._redis_client, DataThread._tokenizer, DataThread._model, self.username, self.mode)
                
            # 发送数据准备好的信号
            self.data_ready.emit(response, conversation_id)
            
        except Exception as e:
            # 捕获所有异常，发送错误信号
            error_msg = f"数据处理错误: {str(e)}"
            print(error_msg)
            traceback.print_exc()  # 打印详细的堆栈跟踪
            self.error_occurred.emit(error_msg)
    
    def initialize_chatbot(self, redis_host, redis_port, redis_password, model_path):
        """初始化聊天机器人，包括 Redis 连接和模型加载"""
        try:
            # 连接到 Redis
            redis_client = redis.Redis(
                host=redis_host,
                port=redis_port,
                password=redis_password,
                decode_responses=True  # 自动解码为字符串
            )

            # 加载模型和分词器
            tokenizer = AutoTokenizer.from_pretrained(model_path)
            model = AutoModelForCausalLM.from_pretrained(model_path, torch_dtype=torch.bfloat16, device_map="cuda")
            model.generation_config = GenerationConfig.from_pretrained(model_path)
            model.generation_config.pad_token_id = model.generation_config.eos_token_id

            return redis_client, tokenizer, model
        except Exception as e:
            # 捕获初始化过程中的异常
            error_msg = f"初始化错误: {str(e)}"
            print(error_msg)
            traceback.print_exc()  # 打印详细的堆栈跟踪
            self.error_occurred.emit(error_msg)
            raise  # 重新抛出异常，以便在run方法中捕获
    
    def chat_with_model(self, user_input, conversation_id=None, redis_client=None, tokenizer=None, model=None, username=None, mode=None):
        """与模型进行对话，并返回模型的回复和对话 ID"""
        try:
            # 如果 conversation_id 不存在，生成一个新的
            if conversation_id is None:
                conversation_id = str(uuid.uuid4())  # 生成唯一 ID
                try:
                    con = UserServerController()
                    userinfo = {
                        'username': username,
                    }
                    uid = con.getUid(userinfo)
                    print(uid)
                    if uid and len(uid) > 0 and len(uid[0]) > 6:
                        Uid = uid[0][6]
                        info = {
                            'UUID': Uid,
                            'KIND': mode,
                            'DIAKEY': conversation_id,
                        }
                        con.addUid(info)
                        print(f"New conversation started. Conversation ID: {conversation_id}")
                    else:
                        print(f"无法获取用户ID，但会继续对话。Conversation ID: {conversation_id}")
                except Exception as db_error:
                    print(f"数据库操作失败，但会继续对话: {str(db_error)}")
                    traceback.print_exc()

            # 从 Redis 中获取对话历史
            history = redis_client.get(conversation_id)
            if history:
                messages = json.loads(history)  # 反序列化为列表
            else:
                # 如果有用户名，在系统提示中包含用户名
                system_content = "You are an interviewer who use english, who are mean and use simple question to figure out the user's ability and performs the duties of an interviewer according to different professional fields and the user's intended position, interviews users."
                if username:
                    system_content += f" The interviewee's name is {username}."
                
                messages = [
                    {"role": "system",
                    "content": system_content},
                ]

            # 添加用户输入到对话历史
            messages.append({"role": "user", "content": user_input})

            # 应用聊天模板并生成输出
            input_tensor = tokenizer.apply_chat_template(messages, add_generation_prompt=True, return_tensors="pt")
            outputs = model.generate(input_tensor.to(model.device), max_new_tokens=500)

            # 解码模型输出
            model_response = tokenizer.decode(outputs[0][input_tensor.shape[1]:], skip_special_tokens=True)

            # 添加模型回复到对话历史
            messages.append({"role": "assistant", "content": model_response})

            # 将更新后的对话历史存储到 Redis
            redis_client.set(conversation_id, json.dumps(messages))  # 序列化为 JSON 字符串

            return model_response, conversation_id
        except Exception as e:
            # 捕获对话过程中的异常
            error_msg = f"对话错误: {str(e)}"
            print(error_msg)
            traceback.print_exc()  # 打印详细的堆栈跟踪
            self.error_occurred.emit(error_msg)
            # 返回错误信息和对话ID，确保UI能够显示错误
            return f"对话过程中出错: {str(e)}", conversation_id