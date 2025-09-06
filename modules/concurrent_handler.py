#!/usr/bin/env python3
"""
并发处理模块
提供多线程并发推理功能
"""

import time
import threading
import queue

from typing import Generator, Dict, Optional

try:
    import colorama
    from colorama import Fore, Style
except ImportError as e:
    print(f"请安装依赖: pip install colorama")
    raise e

from llm_core import SimpleLLM
from performance_monitor import PerformanceMonitor


class ConcurrentLLM:
    """支持并发请求处理的LLM包装器"""
    
    def __init__(self, model_path: str, max_concurrent: int = 3, monitor: Optional[PerformanceMonitor] = None, **kwargs):
        self.base_llm = SimpleLLM(model_path, monitor=monitor, **kwargs)
        self.max_concurrent = max_concurrent
        self.monitor = monitor


        self.active_requests = 0
        self.lock = threading.Lock()
    
    def load_model(self) -> bool:
        """加载模型"""
        return self.base_llm.load_model()
    
    def generate_response_async(self, user_input: str, callback=None) -> threading.Thread:
        """异步生成回复"""
        def worker():
            try:
                result = list(self.base_llm.generate_response(user_input))
                if callback:
                    callback(result)
                return result
            except Exception as e:
                error_msg = f"并发请求错误: {e}"
                if callback:
                    callback([error_msg])
                return [error_msg]
        
        thread = threading.Thread(target=worker)
        thread.start()
        return thread
    
    def generate_response(self, user_input: str) -> Generator[str, None, None]:
        """同步生成回复（与原接口兼容）"""
        with self.lock:
            if self.active_requests >= self.max_concurrent:
                yield f"{Fore.YELLOW}⚠️  请求队列已满，等待中...{Style.RESET_ALL}\n"
        
        # 等待空闲槽位
        while True:
            with self.lock:
                if self.active_requests < self.max_concurrent:
                    self.active_requests += 1
                    break
            time.sleep(0.1)
        
        try:
            for token in self.base_llm.generate_response(user_input):
                yield token
        finally:
            with self.lock:
                self.active_requests = max(0, self.active_requests - 1)
    
    def clear_history(self):
        """清空聊天历史"""
        self.base_llm.clear_history()
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        stats = self.base_llm.get_stats()
        stats["最大并发数"] = self.max_concurrent
        stats["当前活跃请求"] = self.active_requests
        return stats
    
    def shutdown(self):
        """关闭并发处理器"""
        # 线程会在任务完成后自动结束
        pass


