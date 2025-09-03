#!/usr/bin/env python3
"""
并发处理模块
提供多线程并发推理功能
"""

import time
import threading
import queue
from concurrent.futures import ThreadPoolExecutor
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
        self.executor = ThreadPoolExecutor(max_workers=max_concurrent)
        self.request_queue = queue.Queue()
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
        self.executor.shutdown(wait=True)


class RequestQueue:
    """请求队列管理器"""
    
    def __init__(self, max_size: int = 10):
        self.queue = queue.Queue(maxsize=max_size)
        self.priority_queue = queue.PriorityQueue()
        self.processing_count = 0
        self.lock = threading.Lock()
    
    def add_request(self, request_data: Dict, priority: int = 5):
        """添加请求到队列"""
        try:
            if priority <= 3:  # 高优先级请求
                self.priority_queue.put((priority, request_data), timeout=1)
            else:  # 普通请求
                self.queue.put(request_data, timeout=1)
            return True
        except queue.Full:
            return False
    
    def get_next_request(self, timeout: float = 1.0):
        """获取下一个请求"""
        # 优先处理高优先级请求
        try:
            priority, request_data = self.priority_queue.get(block=False)
            return request_data
        except queue.Empty:
            pass
        
        # 处理普通请求
        try:
            return self.queue.get(timeout=timeout)
        except queue.Empty:
            return None
    
    def get_queue_status(self) -> Dict:
        """获取队列状态"""
        with self.lock:
            return {
                "普通队列长度": self.queue.qsize(),
                "优先队列长度": self.priority_queue.qsize(),
                "正在处理": self.processing_count,
                "队列总长度": self.queue.qsize() + self.priority_queue.qsize()
            }
    
    def mark_processing_start(self):
        """标记开始处理"""
        with self.lock:
            self.processing_count += 1
    
    def mark_processing_end(self):
        """标记处理结束"""
        with self.lock:
            self.processing_count = max(0, self.processing_count - 1)


class LoadBalancer:
    """负载均衡器"""
    
    def __init__(self, llm_instances: list):
        self.llm_instances = llm_instances
        self.current_index = 0
        self.request_counts = [0] * len(llm_instances)
        self.lock = threading.Lock()
    
    def get_next_instance(self):
        """获取下一个可用的LLM实例（轮询算法）"""
        with self.lock:
            # 选择请求数最少的实例
            min_requests = min(self.request_counts)
            for i, count in enumerate(self.request_counts):
                if count == min_requests:
                    self.request_counts[i] += 1
                    return self.llm_instances[i], i
            
            # 如果所有实例都很忙，使用轮询
            instance = self.llm_instances[self.current_index]
            instance_id = self.current_index
            self.current_index = (self.current_index + 1) % len(self.llm_instances)
            return instance, instance_id
    
    def mark_request_complete(self, instance_id: int):
        """标记请求完成"""
        with self.lock:
            if 0 <= instance_id < len(self.request_counts):
                self.request_counts[instance_id] = max(0, self.request_counts[instance_id] - 1)
    
    def get_status(self) -> Dict:
        """获取负载均衡状态"""
        with self.lock:
            return {
                "实例数量": len(self.llm_instances),
                "当前请求分布": self.request_counts.copy(),
                "总请求数": sum(self.request_counts)
            }