from datasets import load_dataset, Dataset
from transformers import AutoTokenizer, AutoModelForCausalLM, TrainingArguments, Trainer
import torch
import pandas as pd

# 加载本地CSV数据集
df = pd.read_csv('/Users/ruotianjoy/PycharmProjects/MockBoost/Training/data/interview_questions.csv')  # 请确保CSV文件包含'question'和'answer'列
# 确保question和answer列的数据类型为字符串
df['question'] = df['question'].astype(str)
df['answer'] = df['answer'].astype(str)
ds = Dataset.from_pandas(df)

# 加载tokenizer和模型
tokenizer = AutoTokenizer.from_pretrained("/Users/ruotianjoy/PycharmProjects/MockBoost/Training/Llama-3.2-1B")
model = AutoModelForCausalLM.from_pretrained("/Users/ruotianjoy/PycharmProjects/MockBoost/Training/Llama-3.2-1B")

# 设置padding token
tokenizer.pad_token = tokenizer.eos_token
model.config.pad_token_id = tokenizer.pad_token_id

# 数据预处理函数
def preprocess_function(examples):
    # 确保输入数据的格式正确
    if not all(isinstance(q, str) and isinstance(a, str) 
              for q, a in zip(examples['question'], examples['answer'])):
        raise ValueError("所有的问题和答案都必须是字符串类型")
    
    # 构建输入文本
    texts = []
    for q, a in zip(examples['question'], examples['answer']):
        # 移除可能的空白字符
        q = q.strip()
        a = a.strip()
        texts.append(f"Question: {q}\nAnswer: {a}")
    
    # 使用tokenizer处理文本
    tokenized = tokenizer(
        texts,
        truncation=True,
        padding='max_length',  # 使用固定长度padding
        max_length=512,
        return_tensors=None,  # 确保返回的是Python列表
        return_attention_mask=True  # 显式添加attention mask
    )
    
    # 确保所有的字段都是列表类型
    for key in tokenized.keys():
        if not isinstance(tokenized[key], list):
            tokenized[key] = tokenized[key].tolist()
    
    # 添加标签信息
    tokenized["labels"] = tokenized["input_ids"].copy()
    return tokenized

# 对数据集进行预处理
tokenized_ds = ds.map(preprocess_function, batched=True)

# 设置训练参数
training_args = TrainingArguments(
    output_dir="Training/trained_model",
    per_device_train_batch_size=2,  # 减小batch size以避免内存问题
    gradient_accumulation_steps=4,  # 添加梯度累积
    num_train_epochs=3,
    save_steps=1000,
    save_total_limit=2,
    logging_steps=100,
    learning_rate=1e-5,  # 降低学习率以提高稳定性
    warmup_steps=100,  # 添加预热步骤
    report_to=[],  # 禁用所有报告功能，包括wandb
    remove_unused_columns=False  # 防止移除labels列
)

# 初始化Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_ds,
    data_collator=None  # 移除tokenizer参数，使用默认的数据整理器
)

# 开始训练
trainer.train()

# 保存训练后的模型
trainer.save_model()