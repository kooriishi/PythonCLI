#!/usr/bin/env python3
"""
性能监控模块
提供系统资源监控和推理性能统计功能
"""

import time
import threading
from dataclasses import dataclass
from typing import List
import datetime

try:
    import psutil
    import colorama
    from colorama import Fore, Style
except ImportError as e:
    print(f"请安装依赖: pip install psutil colorama")
    raise e


@dataclass
class PerformanceMetrics:
    """性能指标数据结构"""
    cpu_percent: float = 0.0
    memory_percent: float = 0.0
    memory_used_gb: float = 0.0
    gpu_percent: float = 0.0
    gpu_memory_used_gb: float = 0.0
    total_requests: int = 0
    active_requests: int = 0
    avg_response_time: float = 0.0
    tokens_per_second: float = 0.0
    uptime_seconds: float = 0.0


class PerformanceMonitor:
    """性能监控类"""
    
    def __init__(self):
        self.metrics = PerformanceMetrics()
        self.start_time = time.time()
        self.response_times = []
        self.is_monitoring = False
        self.monitor_thread = None
        self.lock = threading.Lock()
        
        # 尝试导入GPU监控
        self.gpu_available = False
        try:
            import GPUtil
            self.gpu_available = True
            self.GPUtil = GPUtil
        except ImportError:
            pass
    
    def start_monitoring(self):
        """开始性能监控"""
        if not self.is_monitoring:
            self.is_monitoring = True
            self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self.monitor_thread.start()
    
    def stop_monitoring(self):
        """停止性能监控"""
        self.is_monitoring = False
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=1)
    
    def _monitor_loop(self):
        """监控循环"""
        while self.is_monitoring:
            try:
                with self.lock:
                    # 更新系统性能指标
                    self.metrics.cpu_percent = psutil.cpu_percent(interval=1)
                    memory = psutil.virtual_memory()
                    self.metrics.memory_percent = memory.percent
                    self.metrics.memory_used_gb = memory.used / (1024**3)
                    
                    # 更新GPU指标（如果可用）
                    if self.gpu_available:
                        try:
                            gpus = self.GPUtil.getGPUs()
                            if gpus:
                                gpu = gpus[0]
                                self.metrics.gpu_percent = gpu.load * 100
                                self.metrics.gpu_memory_used_gb = gpu.memoryUsed / 1024
                        except:
                            pass
                    
                    # 更新运行时间
                    self.metrics.uptime_seconds = time.time() - self.start_time
                    
                    # 计算平均响应时间
                    if self.response_times:
                        self.metrics.avg_response_time = sum(self.response_times) / len(self.response_times)
                        # 只保留最近100次的响应时间
                        if len(self.response_times) > 100:
                            self.response_times = self.response_times[-100:]
                
                time.sleep(1)  # 每秒更新一次
            except Exception as e:
                print(f"监控错误: {e}")
                time.sleep(5)
    
    def record_request_start(self):
        """记录请求开始"""
        with self.lock:
            self.metrics.active_requests += 1
            self.metrics.total_requests += 1
    
    def record_request_end(self, duration: float, tokens: int = 0):
        """记录请求结束"""
        with self.lock:
            self.metrics.active_requests = max(0, self.metrics.active_requests - 1)
            self.response_times.append(duration)
            if duration > 0 and tokens > 0:
                self.metrics.tokens_per_second = tokens / duration
    
    def get_metrics(self) -> PerformanceMetrics:
        """获取当前性能指标"""
        with self.lock:
            return self.metrics
    
    def format_metrics(self) -> str:
        """格式化性能指标显示"""
        m = self.get_metrics()
        uptime = str(datetime.timedelta(seconds=int(m.uptime_seconds)))
        
        output = f"""{Fore.CYAN}🖥️  性能监控仪表盘{Style.RESET_ALL}
{Fore.YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Style.RESET_ALL}
{Fore.GREEN}📊 系统资源:{Style.RESET_ALL}
  • CPU: {m.cpu_percent:5.1f}% {self._get_bar(m.cpu_percent)}
  • 内存: {m.memory_percent:5.1f}% ({m.memory_used_gb:.1f}GB) {self._get_bar(m.memory_percent)}"""
        
        if self.gpu_available and m.gpu_percent > 0:
            output += f"\n  • GPU: {m.gpu_percent:5.1f}% ({m.gpu_memory_used_gb:.1f}GB) {self._get_bar(m.gpu_percent)}"
        
        output += f"""
{Fore.BLUE}🚀 推理性能:{Style.RESET_ALL}
  • 总请求数: {m.total_requests}
  • 活跃请求: {m.active_requests}
  • 平均响应: {m.avg_response_time:.2f}s
  • 生成速度: {m.tokens_per_second:.1f} tokens/s
  • 运行时间: {uptime}
{Fore.YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Style.RESET_ALL}"""
        
        return output
    
    def _get_bar(self, percentage: float, width: int = 20) -> str:
        """生成进度条"""
        filled = int(percentage / 100 * width)
        bar = '█' * filled + '▒' * (width - filled)
        if percentage > 80:
            color = Fore.RED
        elif percentage > 60:
            color = Fore.YELLOW
        else:
            color = Fore.GREEN
        return f"{color}[{bar}]{Style.RESET_ALL}"