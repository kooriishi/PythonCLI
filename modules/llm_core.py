#!/usr/bin/env python3
"""
LLM核心推理模块
提供本地量化模型推理功能
"""

import os
import time
import threading
from datetime import datetime
from typing import Generator, List, Dict, Optional

try:
    import colorama
    from colorama import Fore, Style
    from llama_cpp import Llama
except ImportError as e:
    print(f"请安装依赖: pip install llama-cpp-python colorama")
    raise e

from hardware_detector import HardwareDetector
from performance_monitor import PerformanceMonitor


class SimpleLLM:
    """简化的本地 LLM 推理器（支持多硬件后端和性能监控）"""
    
    def __init__(self, model_path: str, backend: str = 'auto', monitor: Optional[PerformanceMonitor] = None, **kwargs):
        self.model_path = model_path
        self.backend = backend
        self.monitor = monitor
        self.llm = None
        self.chat_history = []
        self.total_chars = 0
        self.total_time = 0.0
        self.start_time = datetime.now()
        self.lock = threading.Lock()  # 线程安全
        
        # 检测可用后端
        self.available_backends = HardwareDetector.detect_available_backends()
        
        # 选择后端
        if backend == 'auto':
            self.selected_backend = self._select_best_backend()
        else:
            self.selected_backend = backend if self.available_backends.get(backend, False) else 'cpu'
        
        # 获取后端优化配置
        backend_config = HardwareDetector.get_optimal_config(self.selected_backend)
        
        # 默认参数，结合后端优化
        self.config = {
            'n_ctx': kwargs.get('n_ctx', 2048),
            'n_threads': kwargs.get('n_threads', backend_config['n_threads']),
            'n_gpu_layers': kwargs.get('n_gpu_layers', backend_config.get('n_gpu_layers', 0)),
            'temperature': kwargs.get('temperature', 0.7),
            'top_p': kwargs.get('top_p', 0.9),
            'max_tokens': kwargs.get('max_tokens', 512),
            'verbose': kwargs.get('verbose', False)
        }
    
    def _select_best_backend(self) -> str:
        """自动选择最优后端"""
        if self.available_backends.get('cuda', False):
            return 'cuda'
        elif self.available_backends.get('metal', False):
            return 'metal'
        elif self.available_backends.get('opencl', False):
            return 'opencl'
        else:
            return 'cpu'
    
    def load_model(self) -> bool:
        """加载模型"""
        print(f"{Fore.YELLOW}正在加载模型: {os.path.basename(self.model_path)}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}使用后端: {self.selected_backend.upper()}{Style.RESET_ALL}")
        
        if not os.path.exists(self.model_path):
            print(f"{Fore.RED}❌ 模型文件不存在: {self.model_path}{Style.RESET_ALL}")
            return False
        
        try:
            self.llm = Llama(
                model_path=self.model_path,
                n_ctx=self.config['n_ctx'],
                n_threads=self.config['n_threads'],
                n_gpu_layers=self.config['n_gpu_layers'],
                verbose=self.config['verbose']
            )
            print(f"{Fore.GREEN}✅ 模型加载成功!{Style.RESET_ALL}")
            
            # 显示配置信息
            print(f"{Fore.CYAN}配置信息:{Style.RESET_ALL}")
            print(f"  • 上下文长度: {self.config['n_ctx']}")
            print(f"  • CPU线程数: {self.config['n_threads']}")
            print(f"  • GPU层数: {self.config['n_gpu_layers']}")
            
            return True
        except Exception as e:
            print(f"{Fore.RED}❌ 模型加载失败: {e}{Style.RESET_ALL}")
            return False
    
    def generate_response(self, user_input: str) -> Generator[str, None, None]:
        """流式生成回复（线程安全）"""
        if not self.llm:
            yield "模型未加载"
            return
        
        # 性能监控
        if self.monitor:
            self.monitor.record_request_start()
        
        with self.lock:  # 保证线程安全
            # 记录用户输入
            self.chat_history.append({"role": "user", "content": user_input})
            
            # 构建提示词
            prompt = self._build_prompt(user_input)
        
        try:
            start_time = time.time()
            response_text = ""
            token_count = 0
            
            # 流式生成
            stream = self.llm(
                prompt,
                max_tokens=self.config['max_tokens'],
                temperature=self.config['temperature'],
                top_p=self.config['top_p'],
                repeat_penalty=1.1,
                stream=True,
                stop=["<|im_end|>", "<|im_start|>", "\n\n<|im_start|>"]
            )
            
            for output in stream:
                if 'choices' in output and len(output['choices']) > 0:
                    token = output['choices'][0]['text']
                    response_text += token
                    token_count += 1
                    yield token
            
            # 记录统计
            generation_time = time.time() - start_time
            self.total_chars += len(response_text)
            self.total_time += generation_time
            
            # 性能监控
            if self.monitor:
                self.monitor.record_request_end(generation_time, token_count)
            
            with self.lock:
                # 记录助手回复
                clean_response = response_text.strip()
                self.chat_history.append({"role": "assistant", "content": clean_response})
            
            # 输出统计信息
            chars_per_sec = len(response_text) / generation_time if generation_time > 0 else 0
            yield f"\n{Fore.CYAN}📊 {len(response_text)} 字符 | {generation_time:.2f}s | {chars_per_sec:.1f} 字符/秒 | {token_count} tokens{Style.RESET_ALL}"
            
        except Exception as e:
            if self.monitor:
                self.monitor.record_request_end(0, 0)
            yield f"\n{Fore.RED}❌ 生成错误: {e}{Style.RESET_ALL}"
    
    def _build_prompt(self, user_input: str) -> str:
        """构建对话提示词"""
        # 使用更适合Qwen模型的对话格式
        conversation = ["<|im_start|>system\n你是一个有用的AI助手，请用中文简洁地回答用户的问题。<|im_end|>"]
        
        # 添加最近的对话历史 (最多6轮)
        recent_history = self.chat_history[-6:]
        for msg in recent_history:
            if msg["role"] == "user":
                conversation.append(f"<|im_start|>user\n{msg['content']}<|im_end|>")
            else:
                conversation.append(f"<|im_start|>assistant\n{msg['content']}<|im_end|>")
        
        # 添加当前用户输入
        conversation.append(f"<|im_start|>user\n{user_input}<|im_end|>")
        conversation.append("<|im_start|>assistant\n")
        
        return "\n".join(conversation)
    
    def clear_history(self):
        """清空聊天历史"""
        with self.lock:
            self.chat_history.clear()
        print(f"{Fore.GREEN}✅ 聊天历史已清空{Style.RESET_ALL}")
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        uptime = datetime.now() - self.start_time
        user_msgs = sum(1 for msg in self.chat_history if msg["role"] == "user")
        ai_msgs = sum(1 for msg in self.chat_history if msg["role"] == "assistant")
        avg_speed = self.total_chars / self.total_time if self.total_time > 0 else 0
        
        return {
            "运行时间": str(uptime).split('.')[0],
            "对话轮数": user_msgs,
            "总字符数": self.total_chars,
            "平均速度": f"{avg_speed:.1f} 字符/秒",
            "模型文件": os.path.basename(self.model_path),
            "后端类型": self.selected_backend.upper(),
            "允许后端": ", ".join([k.upper() for k, v in self.available_backends.items() if v])
        }