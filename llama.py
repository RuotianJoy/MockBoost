import json
import torch
from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
from langchain_community.llms import HuggingFacePipeline
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from sentence_transformers import SentenceTransformer





# 主函数
def main():


    # 加载模型和分词器
    model_path = "D:\\Project\\MockBoost\\Training\\Llama-3.2-1B"
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    model = AutoModelForCausalLM.from_pretrained(model_path).to("cuda")  # 移动到 GPU

    # 使用 transformers 的 pipeline 封装 LLM
    generator = pipeline(
        task="text-generation",
        model=model,
        tokenizer=tokenizer,
        device=0,  # GPU 设备编码
        do_sample=True,
        top_k=10,
        truncation=True,
    )

    # 将 pipeline 包装成 LangChain 的 LLM 接口
    llm = HuggingFacePipeline(pipeline=generator)

    # 创建对话链
    # 创建对话链
    prompt_template = PromptTemplate(
        input_variables=["user_input"],
        template="你问: {user_input}\n机器人回答: "  # 这里添加模板字符串
    )

    chain = LLMChain(
        llm=llm,
        prompt=prompt_template,
        verbose=False,
    )

    print("开始与机器人聊天（输入 'exit' 结束）!")
    while True:
        user_input = input("你: ").strip()
        if user_input.lower() == "exit":
            print("聊天结束，再见！")
            break

        # 知识库检索


        # 生成回复
        bot_response = chain.run({
            "user_input": user_input,

        })
        print(f"机器人: {bot_response}")


if __name__ == "__main__":
    main()