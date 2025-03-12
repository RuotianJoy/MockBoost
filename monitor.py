import os
import psutil
import time
import logging
from datetime import datetime

# 配置日志记录
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mockboost_monitor.log'),
        logging.StreamHandler()
    ]
)

class MockBoostMonitor:
    def __init__(self):
        self.exe_path = os.path.join('dist', 'MockBoost', 'MockBoost.exe')
        self.process = None
        self.start_time = None

    def start_process(self):
        """启动MockBoost.exe进程"""
        try:
            if not os.path.exists(self.exe_path):
                logging.error(f'MockBoost.exe不存在于路径: {self.exe_path}')
                return False

            self.process = psutil.Popen([self.exe_path])
            self.start_time = datetime.now()
            logging.info(f'MockBoost.exe已启动，进程ID: {self.process.pid}')
            return True
        except Exception as e:
            logging.error(f'启动MockBoost.exe时发生错误: {str(e)}')
            return False

    def monitor_performance(self):
        """监控进程的CPU和内存使用情况"""
        try:
            if not self.process:
                return

            process = psutil.Process(self.process.pid)
            cpu_percent = process.cpu_percent(interval=1)
            memory_info = process.memory_info()
            memory_mb = memory_info.rss / 1024 / 1024  # 转换为MB

            logging.info(f'CPU使用率: {cpu_percent}%')
            logging.info(f'内存使用: {memory_mb:.2f} MB')

            # 检查是否超过资源限制
            if cpu_percent > 90:  # CPU使用率超过90%
                logging.warning(f'CPU使用率过高: {cpu_percent}%')
            if memory_mb > 1024:  # 内存使用超过1GB
                logging.warning(f'内存使用过高: {memory_mb:.2f} MB')

        except psutil.NoSuchProcess:
            logging.error('进程已终止')
            self.process = None
        except Exception as e:
            logging.error(f'监控性能时发生错误: {str(e)}')

    def check_process_status(self):
        """检查进程状态"""
        if not self.process:
            return False

        try:
            if self.process.poll() is not None:
                logging.warning('MockBoost.exe已终止')
                return False
            return True
        except Exception as e:
            logging.error(f'检查进程状态时发生错误: {str(e)}')
            return False

    def run(self):
        """运行监控程序"""
        if not self.start_process():
            return

        try:
            while self.check_process_status():
                self.monitor_performance()
                time.sleep(5)  # 每5秒监控一次

        except KeyboardInterrupt:
            logging.info('监控程序被用户终止')
            if self.process:
                self.process.terminate()
                logging.info('MockBoost.exe已被终止')

if __name__ == '__main__':
    monitor = MockBoostMonitor()
    monitor.run()