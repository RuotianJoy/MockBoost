from typing import List, Optional
from llama_index.vector_stores import MilvusVectorStore
from llama_index import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    Document,
    StorageContext,
    ServiceContext
)
from llama_index.schema import TextNode
from datetime import datetime
import os

class ChatMemoryManager:
    def __init__(
        self, 
        host: str = "localhost", 
        port: int = 19530,
        collection_name: str = "chat_memories"
    ):
        # 初始化 Milvus 向量存储
        self.vector_store = MilvusVectorStore(
            host=host,
            port=port,
            collection_name=collection_name,
            dim=1536  # 使用默认的OpenAI embedding维度
        )
        
        # 创建存储上下文
        storage_context = StorageContext.from_defaults(vector_store=self.vector_store)
        
        # 初始化索引
        self.index = VectorStoreIndex.from_documents(
            [], 
            storage_context=storage_context
        )

    def store_memory(
        self,
        user_id: str,
        message: str,
        metadata: Optional[dict] = None
    ) -> None:
        """
        存储一条对话记忆
        
        Args:
            user_id: 用户ID
            message: 对话内容
            metadata: 额外的元数据信息
        """
        if metadata is None:
            metadata = {}
            
        # 添加基础元数据
        base_metadata = {
            "user_id": user_id,
            "timestamp": datetime.now().isoformat(),
            "type": "chat_memory"
        }
        
        # 合并用户提供的元数据
        metadata.update(base_metadata)
        
        # 创建文本节点
        node = TextNode(
            text=message,
            metadata=metadata
        )
        
        # 将节点添加到索引中
        self.index.insert_nodes([node])

    def query_memories(
        self,
        query: str,
        user_id: Optional[str] = None,
        limit: int = 5
    ) -> List[dict]:
        """
        查询相关的对话记忆
        
        Args:
            query: 查询文本
            user_id: 可选的用户ID过滤
            limit: 返回结果的最大数量
        
        Returns:
            包含相关记忆的列表
        """
        # 创建查询引擎
        query_engine = self.index.as_query_engine()
        
        # 如果指定了用户ID，添加过滤条件
        if user_id:
            filter_condition = lambda node: node.metadata.get("user_id") == user_id
            query_engine = self.index.as_query_engine(
                filters=filter_condition
            )
        
        # 执行查询
        response = query_engine.query(query)
        
        # 提取结果
        results = []
        for node in response.source_nodes[:limit]:
            results.append({
                "text": node.text,
                "metadata": node.metadata,
                "score": node.score if hasattr(node, 'score') else None
            })
            
        return results

# 使用示例
def main():
    # 初始化记忆管理器
    memory_manager = ChatMemoryManager()
    
    # 存储一些示例对话
    memory_manager.store_memory(
        user_id="user123",
        message="我最喜欢的颜色是蓝色",
        metadata={"emotion": "positive", "topic": "preferences"}
    )
    
    memory_manager.store_memory(
        user_id="user123",
        message="今天天气真不错",
        metadata={"emotion": "positive", "topic": "weather"}
    )
    
    # 查询示例
    results = memory_manager.query_memories(
        query="颜色相关的对话",
        user_id="user123"
    )
    
    # 打印结果
    for result in results:
        print(f"找到的记忆: {result['text']}")
        print(f"元数据: {result['metadata']}")
        print(f"相关度分数: {result['score']}")
        print("---")

if __name__ == "__main__":
    main()
