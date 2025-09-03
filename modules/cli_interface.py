#!/usr/bin/env python3
"""
CLI交互界面模块
提供命令行用户界面和交互功能
"""

import os
from typing import Dict, Optional

try:
    import colorama
    from colorama import Fore, Style
except ImportError as e:
    print(f"请安装依赖: pip install colorama")
    raise e

from llm_core import SimpleLLM
from concurrent_handler import ConcurrentLLM
from performance_monitor import PerformanceMonitor
from hardware_detector import HardwareDetector


class ChatCLI:
    """增强的聊天 CLI（支持性能监控和并发处理）"""
    
    def __init__(self, enable_monitoring: bool = False, max_concurrent: int = 1):
        self.llm = None
        self.monitor = PerformanceMonitor() if enable_monitoring else None
        self.max_concurrent = max_concurrent
        self.enable_monitoring = enable_monitoring
        self.monitor_display_active = False
    
    def print_banner(self):
        """打印欢迎信息"""
        banner = f"""
{Fore.CYAN}╭──────────────────────────────────────────────────────────────╮
│                🤖 升级版本地量化模型推理工具                │
│              基于 llama-cpp-python + Qwen1.5-0.5B            │
│                                                              │
│  新增功能: 性能监控 | 多硬件后端 | 并发处理               │
│  本地推理 | 流式输出 | 对话历史 | 性能统计               │
│  命令: /help /clear /stats /monitor /backends /quit         │
╰──────────────────────────────────────────────────────────────╯{Style.RESET_ALL}
"""
        print(banner)
    
    def run(self, model_path: str, backend: str = 'auto', **config):
        """运行聊天程序"""
        # 初始化模型
        if self.max_concurrent > 1:
            self.llm = ConcurrentLLM(model_path, self.max_concurrent, self.monitor, backend=backend, **config)
        else:
            self.llm = SimpleLLM(model_path, backend=backend, monitor=self.monitor, **config)
        
        if not self.llm.load_model():
            return
        
        # 启动性能监控
        if self.monitor:
            self.monitor.start_monitoring()
            print(f"{Fore.GREEN}🖥️ 性能监控已启动 (输入 /monitor 查看){Style.RESET_ALL}")
        
        self.print_banner()
        print(f"{Fore.GREEN}💬 开始对话! (输入 /help 查看命令){Style.RESET_ALL}")
        if self.max_concurrent > 1:
            print(f"{Fore.CYAN}🚀 并发模式已启用，最大并发数: {self.max_concurrent}{Style.RESET_ALL}")
        print("=" * 60)
        
        # 主聊天循环
        try:
            while True:
                try:
                    # 获取用户输入
                    user_input = input(f"\n{Fore.BLUE}你: {Style.RESET_ALL}").strip()
                    
                    if not user_input:
                        continue
                    
                    # 处理命令
                    if user_input.startswith('/'):
                        if self.handle_command(user_input):
                            break
                        continue
                    
                    # 生成回复
                    print(f"{Fore.GREEN}助手: {Style.RESET_ALL}", end="", flush=True)
                    
                    for token in self.llm.generate_response(user_input):
                        print(token, end="", flush=True)
                    print()  # 换行
                    
                except KeyboardInterrupt:
                    print(f"\n\n{Fore.YELLOW}👋 再见!{Style.RESET_ALL}")
                    break
                except Exception as e:
                    print(f"\n{Fore.RED}❌ 错误: {e}{Style.RESET_ALL}")
        finally:
            # 清理资源
            if self.monitor:
                self.monitor.stop_monitoring()
            if hasattr(self.llm, 'shutdown'):
                self.llm.shutdown()
    
    def handle_command(self, command: str) -> bool:
        """处理命令，返回True表示退出"""
        cmd = command.lower()
        
        if cmd in ['/quit', '/exit', '/q']:
            print(f"{Fore.YELLOW}👋 再见!{Style.RESET_ALL}")
            return True
        
        elif cmd in ['/help', '/h']:
            self.show_help()
        
        elif cmd in ['/clear', '/c']:
            if self.llm:
                self.llm.clear_history()
            self._clear_screen()
        
        elif cmd in ['/stats', '/s']:
            self.show_stats()
        
        elif cmd in ['/monitor', '/m']:
            self.toggle_monitor_display()
        
        elif cmd in ['/backends', '/b']:
            self.show_backends()
        
        elif cmd in ['/system', '/sys']:
            self.show_system_info()
        
        else:
            print(f"{Fore.RED}未知命令: {command}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}输入 /help 查看可用命令{Style.RESET_ALL}")
        
        return False
    
    def show_help(self):
        """显示帮助信息"""
        help_text = f"""
{Fore.CYAN}💡 可用命令:{Style.RESET_ALL}
  {Fore.YELLOW}/help{Style.RESET_ALL}     - 显示此帮助
  {Fore.YELLOW}/clear{Style.RESET_ALL}    - 清空聊天历史和屏幕
  {Fore.YELLOW}/stats{Style.RESET_ALL}    - 显示统计信息
  {Fore.YELLOW}/monitor{Style.RESET_ALL}  - 切换性能监控显示
  {Fore.YELLOW}/backends{Style.RESET_ALL} - 显示硬件后端信息
  {Fore.YELLOW}/system{Style.RESET_ALL}   - 显示系统信息
  {Fore.YELLOW}/quit{Style.RESET_ALL}     - 退出程序
"""
        print(help_text)
    
    def show_stats(self):
        """显示统计信息"""
        if not self.llm:
            print(f"{Fore.RED}模型未加载{Style.RESET_ALL}")
            return
        
        stats = self.llm.get_stats()
        print(f"\n{Fore.CYAN}📊 统计信息:{Style.RESET_ALL}")
        for key, value in stats.items():
            print(f"  {key}: {value}")
    
    def toggle_monitor_display(self):
        """切换性能监控显示"""
        if not self.monitor:
            print(f"{Fore.RED}性能监控未启用{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}请使用 --monitor 参数启动程序{Style.RESET_ALL}")
            return
        
        self.monitor_display_active = not self.monitor_display_active
        if self.monitor_display_active:
            print(self.monitor.format_metrics())
            print(f"{Fore.GREEN}🖥️ 性能监控显示已开启{Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}🖥️ 性能监控显示已关闭{Style.RESET_ALL}")
    
    def show_backends(self):
        """显示硬件后端信息"""
        if not hasattr(self.llm, 'available_backends'):
            print(f"{Fore.RED}无法获取后端信息{Style.RESET_ALL}")
            return
        
        backends = self.llm.available_backends
        current_backend = getattr(self.llm, 'selected_backend', 'unknown')
        
        print(f"\n{Fore.CYAN}🖥️ 硬件后端信息:{Style.RESET_ALL}")
        print(f"{Fore.GREEN}当前使用: {current_backend.upper()}{Style.RESET_ALL}")
        print(f"\n可用后端:")
        
        for backend, available in backends.items():
            status = f"{Fore.GREEN}✓{Style.RESET_ALL}" if available else f"{Fore.RED}✗{Style.RESET_ALL}"
            current = f" {Fore.YELLOW}(当前){Style.RESET_ALL}" if backend == current_backend else ""
            config = HardwareDetector.get_optimal_config(backend)
            print(f"  {status} {backend.upper()}{current}: {config}")
    
    def show_system_info(self):
        """显示系统信息"""
        HardwareDetector.print_system_info()
    
    def _clear_screen(self):
        """清屏"""
        os.system('cls' if os.name == 'nt' else 'clear')


class SimplePromptInterface:
    """简单的单次问答界面"""
    
    @staticmethod
    def run_single_prompt(model_path: str, prompt: str, backend: str = 'auto', 
                         monitor: bool = False, **config):
        """运行单次问答"""
        print(f"{Fore.CYAN}🤖 单次问答模式{Style.RESET_ALL}")
        
        # 初始化性能监控
        performance_monitor = PerformanceMonitor() if monitor else None
        if performance_monitor:
            performance_monitor.start_monitoring()
        
        # 初始化模型
        llm = SimpleLLM(model_path, backend=backend, monitor=performance_monitor, **config)
        
        if llm.load_model():
            print(f"\n{Fore.BLUE}问题: {prompt}{Style.RESET_ALL}")
            print(f"{Fore.GREEN}回答: {Style.RESET_ALL}", end="", flush=True)
            
            for token in llm.generate_response(prompt):
                if not token.startswith('\n📊'):
                    print(token, end="", flush=True)
            print()
            
            # 显示性能监控结果
            if performance_monitor:
                print("\n" + performance_monitor.format_metrics())
                performance_monitor.stop_monitoring()
        
        return True