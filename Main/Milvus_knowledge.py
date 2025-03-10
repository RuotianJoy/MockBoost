from pymilvus import Collection, FieldSchema, CollectionSchema, DataType
from pymilvus import connections
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

class ChatMemoryManager:
    def __init__(self, model_path="d:/Project/MockBoost/Training/Llama-3.2-1B", host="127.0.0.1", port="19530"):
        # 初始化本地模型
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model = AutoModelForCausalLM.from_pretrained(model_path, torch_dtype=torch.float16, device_map='auto')

        # 连接到Milvus服务
        connections.connect("default", host=host, port=port)

        # 定义字段
        fields = [
            FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=384),  # MiniLM模型输出维度为384
            FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
            FieldSchema(name="role", dtype=DataType.VARCHAR, max_length=20),
            FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=10000)
        ]

        # 创建集合
        schema = CollectionSchema(fields, description="Chat Memory Collection")
        self.collection = Collection(name="chat_memory_collection", schema=schema)

        # 创建索引
        index_params = {
            "index_type": "IVF_FLAT",
            "metric_type": "L2",
            "params": {"nlist": 128}
        }
        self.collection.create_index(field_name="embedding", index_params=index_params)
        self.collection.load()

    def vectorize_text(self, text: str):
        """将文本转换为向量"""
        return self.embedding_model.encode(text).tolist()

    def store_message(self, text: str, role: str):
        """存储对话消息"""
        vector = self.vectorize_text(text)
        self.collection.insert([
            [vector],
            [role],
            [text]
        ])

    def search_similar_messages(self, query: str, top_k=5):
        """搜索相似的对话消息"""
        query_vector = self.vectorize_text(query)
        search_params = {"nprobe": 10}
        results = self.collection.search(
            data=[query_vector],
            anns_field="embedding",
            param=search_params,
            limit=top_k,
            output_fields=["role", "text"]
        )

        messages = []
        for hits in results[0]:
            messages.append({
                "role": hits.entity.get("role"),
                "text": hits.entity.get("text"),
                "similarity": hits.distance
            })
        return messages

    def chat(self, user_input: str):
        """与大模型对话并存储对话内容"""
        # 存储用户输入
        self.store_message(user_input, "user")

        # 获取相关的历史对话作为上下文
        similar_messages = self.search_similar_messages(user_input)
        context = "\n".join([f"{msg['role']}: {msg['text']}" for msg in similar_messages])

        # 构建输入文本
        input_text = f"System: 你是一个友好的AI助手。\n历史对话上下文：\n{context}\n\nUser: {user_input}\nAssistant:"

        # 使用本地模型生成回复
        inputs = self.tokenizer(input_text, return_tensors="pt").to(self.model.device)
        outputs = self.model.generate(
            **inputs,
            max_new_tokens=512,
            temperature=0.7,
            top_p=0.9,
            repetition_penalty=1.1
        )
        assistant_response = self.tokenizer.decode(outputs[0][inputs['input_ids'].shape[1]:], skip_special_tokens=True)

        # 存储助手的回复
        self.store_message(assistant_response, "assistant")

        return assistant_response

def main():
    # 初始化聊天记忆管理器
    memory_manager = ChatMemoryManager()

    print("开始与AI助手对话（输入'exit'结束对话）：")
    while True:
        user_input = input("\n用户: ")
        if user_input.lower() == "exit":
            print("\n对话结束，再见！")
            break

        response = memory_manager.chat(user_input)
        print(f"\nAI助手: {response}")

if __name__ == "__main__":
    main()
