from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

# 加载模型和tokenizer
model_path = "D:\\Project\\MockBoost\\Training\\Llama-3.2-1B"  # 模型的本地路径
tokenizer = AutoTokenizer.from_pretrained(model_path)
model = AutoModelForCausalLM.from_pretrained(model_path)

# 设置模型为评估模式
model.eval()


# 生成模型回答的函数
def chat_with_model(user_input):
    # 将用户输入编码成模型输入
    inputs = tokenizer(user_input, return_tensors="pt", padding=True, truncation=True)

    # 使用模型生成输出
    with torch.no_grad():
        outputs = model.generate(inputs.input_ids, max_length=1000, pad_token_id=tokenizer.eos_token_id, do_sample=True,
                                 top_p=0.95, top_k=60)

    # 返回生成的文本
    return tokenizer.decode(outputs[0], skip_special_tokens=True)


# 单轮对话
while True:
    user_input = input("你: ")

    # 调用模型生成回答
    model_response = chat_with_model(user_input)
    print(f"模型: {model_response}")

    # 判断是否退出
    if user_input.lower() in ['退出', '再见']:
        print("对话结束")

