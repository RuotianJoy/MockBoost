from PyQt6.QtCore import QThread, pyqtSignal
from db.controller.UserServerController import UserServerController
import time

class EndInterviewThread(QThread):
    """结束面试线程，用于处理结束面试时的耗时操作"""
    finished = pyqtSignal(bool, str)  # 完成信号，传递成功状态和消息
    error_occurred = pyqtSignal(str)  # 错误信号，传递错误信息
    
    def __init__(self, conversation_id=None, username=None, mode=None):
        super().__init__()
        self.conversation_id = conversation_id
        self.username = username
        self.mode = mode
        
    def run(self):
        try:
            # 记录结束时间
            end_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            
            # 如果有对话ID，则保存面试记录
            if self.conversation_id:
                # 这里可以添加保存面试记录到数据库的代码
                # 例如：调用UserServerController保存面试记录
                try:
                    user_controller = UserServerController()
                    # 假设有一个save_interview_record方法
                    # user_controller.save_interview_record(self.username, self.conversation_id, self.mode, end_time)
                    print(f"保存面试记录：用户={self.username}, 对话ID={self.conversation_id}, 模式={self.mode}")
                except Exception as e:
                    print(f"保存面试记录失败: {str(e)}")
                
                # 生成面试评估报告（这里只是示例，实际实现可能需要调用模型分析面试内容）
                try:
                    # 这里可以添加生成评估报告的代码
                    print(f"生成面试评估报告：对话ID={self.conversation_id}")
                except Exception as e:
                    print(f"生成评估报告失败: {str(e)}")
            
            # 发送完成信号
            self.finished.emit(True, "面试已成功结束，评估报告已生成")
            
        except Exception as e:
            # 捕获所有异常，发送错误信号
            error_msg = f"结束面试时发生错误: {str(e)}"
            print(error_msg)
            self.error_occurred.emit(error_msg)
            self.finished.emit(False, error_msg)