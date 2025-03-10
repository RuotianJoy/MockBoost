import torch
import redis
import uuid
import json
from transformers import AutoTokenizer, AutoModelForCausalLM, GenerationConfig
from db.controller.UserServerController import UserServerController
from TTSandASR.ChatTTs import ChatTTS
# 全局变量，用于存储已初始化的模型、分词器和Redis客户端
_redis_client = None
_tokenizer = None
_model = None

def initialize_chatbot(redis_host, redis_port, redis_password, model_path):
    """
    初始化聊天机器人，包括 Redis 连接和模型加载。

    Args:
        redis_host (str): Redis 主机地址
        redis_port (int): Redis 端口
        redis_password (str): Redis 密码
        model_path (str): 模型路径

    Returns:
        tuple: (redis_client, tokenizer, model)
    """
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

def chat_with_model(user_input, conversation_id=None, redis_client=None, tokenizer=None, model=None, username=None, mode=None):
    """
    与模型进行对话，并返回模型的回复和对话 ID。

    Args:
        user_input (str): 用户输入
        conversation_id (str, optional): 对话 ID. Defaults to None.
        redis_client (redis.Redis, optional): Redis 客户端. Defaults to None.
        tokenizer (AutoTokenizer, optional): 分词器. Defaults to None.
        model (AutoModelForCausalLM, optional): 模型. Defaults to None.
        username (str, optional): 用户名. Defaults to None.

    Returns:
        tuple: (model_response, conversation_id)
    """
    # 如果 conversation_id 不存在，生成一个新的
    if conversation_id is None:
        conversation_id = str(uuid.uuid4())  # 生成唯一 ID
        # 从数据库加载历史对话ID
        con = UserServerController()
        userinfo = {
            'username': username,
        }
        uid = con.getUid(userinfo)
        print(uid)
        Uid = uid[0][6]
        info = {
            'UUID': Uid,
            'KIND': mode,
            'DIAKEY': conversation_id,
        }
        con.addUid(info)
        print(f"New conversation started. Conversation ID: {conversation_id}")

    # 从 Redis 中获取对话历史
    history = redis_client.get(conversation_id)
    if history:
        messages = json.loads(history)  # 反序列化为列表
    else:
        # 如果有用户名，在系统提示中包含用户名
        system_content = "You are an interviewer who use english and performs the duties of an interviewer according to different professional fields and the user's intended position, interviews users."
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

def run_chatbot(redis_host, redis_port, redis_password, model_path, user_input):
    """
    运行聊天机器人，进行多轮对话。

    Args:
        redis_host (str): Redis 主机地址
        redis_port (int): Redis 端口
        redis_password (str): Redis 密码
        model_path (str): 模型路径
    """
    # 初始化 Redis 连接和模型
    redis_client, tokenizer, model = initialize_chatbot(redis_host, redis_port, redis_password, model_path)

    # 多轮对话示例
    conversation_id = None  # 初始化对话 ID
    while True:
        user_input = user_input
        if user_input.lower() in ["exit", "quit"]:
            print("Exiting chat...")
            break
        response, conversation_id = chat_with_model(user_input, conversation_id, redis_client, tokenizer, model)

        print(f"AI: {response}")
        return response, conversation_id

# 示例调用
def start_interview_ds(user_input, conversation_id=None, username=None, mode = None):
    global _redis_client, _tokenizer, _model
    
    REDIS_HOST = "r-bp162llfgqnxpesejnpd.redis.rds.aliyuncs.com"  # 阿里云 Redis 地址
    REDIS_PORT = 6379               # Redis 端口
    REDIS_PASSWORD = "Liao031221"  # Redis 密码
    MODEL_PATH = "D:\\Project\\MockBoost\\Training\\Deepseek"  # 模型路径
    
    # 如果模型尚未初始化，则进行初始化
    if _redis_client is None or _tokenizer is None or _model is None:
        print("初始化模型中...")
        _redis_client, _tokenizer, _model = initialize_chatbot(REDIS_HOST, REDIS_PORT, REDIS_PASSWORD, MODEL_PATH)
        print("模型初始化完成")
    
    # 直接使用已初始化的模型进行对话
    response, conversation_id = chat_with_model(user_input, conversation_id, _redis_client, _tokenizer, _model, username, mode)
    return response, conversation_id