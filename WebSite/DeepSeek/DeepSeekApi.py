import re

from openai import OpenAI

import os

api_key = os.getenv("API_KEY")  # 读取环境变量
if not api_key:
    raise ValueError("API Key 未设置！")

print(f"API Key 已加载（长度：{len(api_key)}）")  # 不要直接打印 API Key


client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")


def get_llm_response(
        prompt: str,
        messages=None,
        position: str = None,  # 修改为可选参数
) -> str:
    """
    强化版面试官角色对话模型
    参数说明：
    - position: 目标职位（从用户输入获取，如果没有则使用默认值）
    - competencies: 核心能力要求（默认值可修改）
    """
    # 从消息中提取职位信息
    if position is None:
        position = extract_position_from_messages(messages) or "Senior Software Engineer"

    # 强化系统提示模板
    system_template = """[Role Settings]
You are a professional {position} interviewer. Strictly follow these rules:
1. Ask ONE question per response from:
   - Behavioral (STAR)
   - Technical Case Study
   - Scenario Simulation
2. Use formal business English
3. Provide brief feedback after answers
4. Never break character

[Position Requirements]
- Target Role: {position}
"""

    try:
        # 构建动态系统提示
        system_prompt = system_template.format(
            position=position,
        )

        # 角色锚定技术：在用户输入后追加提示
        anchored_prompt = f"{prompt}\n\n[Reminder: Maintain professional interviewer persona for {position}]"

        # 对话历史管理
        if messages is None:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": anchored_prompt}
            ]
            temp = 0.3  # 单次调用更低随机性
        else:
            # 确保系统提示始终在首位
            if messages[0]["role"] == "system":
                messages[0]["content"] = system_prompt  # 更新系统提示
            else:
                messages.insert(0, {"role": "system", "content": system_prompt})

            messages.append({"role": "user", "content": anchored_prompt})
            temp = 0.5  # 对话模式适度灵活

        # 带稳定性参数的API调用
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            temperature=temp,
            top_p=0.9,
            max_tokens=350,
            frequency_penalty=0.8,  # 抑制非专业内容
            presence_penalty=0.4
        )

        # 获取并验证响应内容
        response_content = response.choices[0].message.content

        # 响应过滤机制
        if not validate_response(response_content):
            return generate_fallback_question(position)

        return response_content

    except Exception as e:
        print(f"API Error: {str(e)}")
        return ""


def extract_position_from_messages(messages):
    """从消息历史中提取职位信息"""
    if not messages:
        return None

    # 查找包含"I want be the"的用户消息
    for msg in messages:
        if msg.get("role") == "user":
            content = msg.get("content", "")
            match = re.search(r"I want be the ([^\.]+)", content)
            if match:
                return match.group(1).strip()

    return None


def validate_response(text: str) -> bool:
    """响应内容验证"""
    required_patterns = [
        r"\?",  # 必须包含问题
        r"\b(describe|explain|how)\b"  # 包含专业动词
    ]
    prohibited_phrases = [
        "casual chat",
        "how can I help",
        "friend"
    ]

    # 检查必要特征
    if not all(re.search(p, text, re.I) for p in required_patterns):
        return False

    # 检查禁止短语
    if any(phrase in text.lower() for phrase in prohibited_phrases):
        return False

    return True


def generate_fallback_question(position: str) -> str:
    """生成应急问题"""
    return f"Let's focus on professional development. Could you elaborate on your most challenging experience as a {position}?"
