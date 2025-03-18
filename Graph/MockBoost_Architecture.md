# MockBoost 应用程序架构

## 概述

MockBoost是一个基于Python的PC端应用程序，主要用于模拟面试场景，结合了人工智能大语言模型、语音识别和合成技术。该应用提供交互式面试体验，能够根据用户的输入进行实时对话。

## 系统架构

应用程序采用多层架构设计，主要包括：

1. **用户界面层**：基于PyQt6实现的图形用户界面
2. **业务逻辑层**：包含模型交互、数据处理等核心功能
3. **数据访问层**：负责数据库操作和数据持久化
4. **外部服务层**：语音识别、语音合成和AI模型服务

## UML类图

```
+---------------------+        +----------------------+        +---------------------+
|     MainWindow      |<>----->|      ModelThread     |<>----->|     DataThread      |
+---------------------+        +----------------------+        +---------------------+
| - username          |        | - user_input         |        | - user_input        |
| - conversation_id   |        | - conversation_id    |        | - conversation_id   |
| - mode_combo        |        | - username           |        | - username          |
| - chat_history      |        | - mode               |        | - mode              |
| - status_label      |        | + run()              |        | - _redis_client     |
| + __init__(username)|        | + on_data_ready()    |        | - _tokenizer        |
| + start_interview() |        | + on_error()         |        | - _model            |
| + handle_input()    |<-------+----------------------+        | + run()             |
| + end_interview()   |                                        | + initialize_chatbot()|
| + on_tts_finished() |                                        | + chat_with_model() |
| + start_voice_rec() |                                        +---------------------+
+--------^------------+                                                  |
         |                                                               |
         |            +---------------------+                            |
         +----------->|      TTSThread      |                            |
         |            +---------------------+                            |
         |            | - text              |                            |
         |            | - tts               |                            |
         |            | + run()             |                            |
         |            +---------------------+                            |
         |                                                               |
         |            +---------------------+                            |
         +----------->|      ASRThread      |<---------------------------+
                      +---------------------+
                      | - model_path        |
                      | - sample_rate       |
                      | - max_duration      |
                      | + run()             |
                      +---------------------+
                               ^
                               |
+---------------------+        |        +----------------------+
|    ChatTTS          |        |        |    VoskRecognizer    |
+---------------------+        |        +----------------------+
| - model             |        |        | - _instance          |
| - sample_rate       |        |        | - model_path         |
| + play_text()       |        |        | - sample_rate        |
+---------------------+        |        | - model              |
                               |        | - recognizer         |
                               +------->| + recognize_speech() |
                                        | + _load_model()      |
                                        +----------------------+

+---------------------+        +----------------------+
|     BaseModel       |<-------| CommonDb             |
+---------------------+        +----------------------+
| - db                |        | - table              |
| - table             |        | + add()              |
| + __init__()        |        | + select()           |
+---------------------+        | + selectAll()        |
                               | + update()           |
                               | + delete_where()     |
                               +----------------------+
                                        ^
                                        |
                               +----------------------+
                               | UserServerController |
                               +----------------------+
                               | + getUid()           |
                               | + addUid()           |
                               +----------------------+

+---------------------+
|    ObjRenderer      |
+---------------------+
| - vertices          |
| - faces             |
| + initializeGL()    |
| + load_obj()        |
| + resizeGL()        |
| + paintGL()         |
+---------------------+
```

## 主要组件说明

### 1. 用户界面组件

#### MainWindow
- **职责**：应用程序的主窗口，负责管理用户界面和交互
- **主要属性**：
  - username：用户名
  - conversation_id：对话ID
  - mode_combo：面试模式选择框
  - chat_history：聊天历史记录
  - status_label：状态标签
- **主要方法**：
  - start_interview()：开始面试
  - handle_input()：处理用户输入
  - end_interview()：结束面试
  - start_voice_rec()：开始语音识别

#### ObjRenderer
- **职责**：3D模型渲染器，用于渲染OBJ文件（可能用于显示虚拟面试官）
- **主要属性**：
  - vertices：顶点数据
  - faces：面数据
- **主要方法**：
  - load_obj()：加载OBJ文件
  - paintGL()：绘制OpenGL场景

### 2. 线程组件

#### ModelThread
- **职责**：模型交互线程，负责调用大模型获取回答
- **主要属性**：
  - user_input：用户输入
  - conversation_id：对话ID
  - username：用户名
  - mode：面试模式
- **主要方法**：
  - run()：线程运行方法
  - on_data_ready()：数据准备好时的回调
  - on_error()：错误处理

#### DataThread
- **职责**：数据获取线程，处理与模型和数据库的交互
- **主要属性**：
  - user_input：用户输入
  - conversation_id：对话ID
  - username：用户名
  - mode：面试模式
  - _redis_client：Redis客户端
  - _tokenizer：分词器
  - _model：模型
- **主要方法**：
  - run()：线程运行方法
  - initialize_chatbot()：初始化聊天机器人
  - chat_with_model()：与模型对话

#### TTSThread
- **职责**：TTS语音合成线程，将文本转换为语音
- **主要属性**：
  - text：要合成的文本
  - tts：TTS实例
- **主要方法**：
  - run()：执行语音合成

#### ASRThread
- **职责**：语音识别线程，将语音转换为文本
- **主要属性**：
  - model_path：模型路径
  - sample_rate：采样率
  - max_duration：最大录音时长
- **主要方法**：
  - run()：执行语音识别

### 3. 语音处理组件

#### ChatTTS
- **职责**：文本到语音转换组件
- **主要属性**：
  - model：TTS模型
  - sample_rate：采样率
- **主要方法**：
  - play_text()：播放文本对应的语音

#### VoskRecognizer
- **职责**：语音识别组件，使用Vosk引擎
- **主要属性**：
  - model_path：模型路径
  - sample_rate：采样率
  - model：Vosk模型
  - recognizer：识别器
- **主要方法**：
  - recognize_speech()：执行语音识别
  - _load_model()：加载模型

### 4. 数据库组件

#### BaseModel
- **职责**：数据库基础模型类
- **主要属性**：
  - db：数据库连接
  - table：表名
- **主要方法**：
  - __init__()：初始化数据库连接

#### CommonDb
- **职责**：通用数据库操作类
- **主要属性**：
  - table：表名
- **主要方法**：
  - add()：添加数据
  - select()：查询数据
  - selectAll()：查询所有数据
  - update()：更新数据
  - delete_where()：删除数据

#### UserServerController
- **职责**：用户服务控制器
- **主要方法**：
  - getUid()：获取用户ID
  - addUid()：添加用户ID

## 数据流程

1. 用户在MainWindow界面输入文本或通过语音输入
2. 用户输入通过ASRThread转换为文本（如果是语音输入）
3. MainWindow创建ModelThread处理用户输入
4. ModelThread创建DataThread与AI模型进行交互
5. DataThread获取AI模型的回复并返回给ModelThread
6. ModelThread将回复发送回MainWindow
7. MainWindow创建TTSThread将AI回复转换为语音（如果启用了语音输出）
8. 对话历史通过Redis存储，用户信息通过数据库存储

## 技术栈

- **UI框架**：PyQt6
- **语音识别**：Vosk
- **语音合成**：TTS
- **AI模型**：使用transformers库加载和调用大型语言模型
- **数据存储**：Redis用于对话历史，关系型数据库用于用户信息
- **3D渲染**：OpenGL用于3D模型渲染

## 设计模式

- **单例模式**：VoskRecognizer使用单例模式确保只有一个实例
- **观察者模式**：使用PyQt的信号和槽机制实现组件间通信
- **多线程模式**：使用QThread进行并发处理，避免UI阻塞 