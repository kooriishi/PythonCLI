#!/usr/bin/env python3
"""
增强版本地量化模型推理 CLI 工具
基于 llama-cpp-python 的 Qwen1.5-0.5B 对话系统

模块化架构：
- performance_monitor.py: 性能监控模块
- hardware_detector.py: 硬件检测模块
- llm_core.py: LLM核心推理模块
- concurrent_handler.py: 并发处理模块
- cli_interface.py: CLI交互界面模块
- main.py: 主程序入口
"""

import os
import sys
sys.path.append("./modules")
import argparse

# 导入模块
try:
    import colorama
    from colorama import Fore, Style
    import psutil
    
    # 导入自定义模块
    from hardware_detector import HardwareDetector
    from performance_monitor import PerformanceMonitor
    from cli_interface import ChatCLI, SimplePromptInterface
    
except ImportError as e:
    print(f"请安装依赖: pip install llama-cpp-python colorama psutil aiohttp")
    print(f"缺少模块: {e}")
    sys.exit(1)

# 初始化颜色输出
colorama.init()


def print_welcome():
    """打印欢迎信息"""
    welcome = f"""
{Fore.CYAN}🚀 增强版本地量化模型推理工具{Style.RESET_ALL}
{Fore.YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Style.RESET_ALL}
{Fore.GREEN}✨ 新增功能:{Style.RESET_ALL}
  • 🖥️  性能监控仪表盘
  • 🔧 多硬件后端支持 (CPU/CUDA/OpenCL/Metal)
  • ⚡ 并发请求处理
  • 📊 实时性能统计
  • 🎨 增强的用户界面

{Fore.BLUE}📚 模块化设计:{Style.RESET_ALL}
  • performance_monitor.py - 性能监控
  • hardware_detector.py - 硬件检测
  • llm_core.py - 核心推理
  • concurrent_handler.py - 并发处理
  • cli_interface.py - 用户界面
{Fore.YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Style.RESET_ALL}
"""
    print(welcome)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="增强版本地量化模型推理工具")
    parser.add_argument("--model", "-m", default="models/qwen1_5-0_5b-chat-q4_0.gguf",
                       help="模型文件路径")
    parser.add_argument("--backend", "-b", default="auto",
                       choices=["auto", "cpu", "cuda", "opencl", "metal"],
                       help="硬件后端选择 (auto/cpu/cuda/opencl/metal)")
    parser.add_argument("--temperature", "-t", type=float, default=0.7,
                       help="温度参数 (0.1-2.0)")
    parser.add_argument("--max-tokens", "-l", type=int, default=512,
                       help="最大生成长度")
    parser.add_argument("--threads", "-j", type=int, default=0,
                       help="CPU线程数 (0=自动)")
    parser.add_argument("--concurrent", "-c", type=int, default=1,
                       help="最大并发请求数 (1-8)")
    parser.add_argument("--monitor", action="store_true",
                       help="启用性能监控")
    parser.add_argument("--prompt", "-p", type=str,
                       help="单次问答模式")
    parser.add_argument("--list-backends", action="store_true",
                       help="显示可用硬件后端")
    parser.add_argument("--system-info", action="store_true",
                       help="显示系统信息")
    
    args = parser.parse_args()
    
    # 显示欢迎信息
    if not args.prompt and not args.list_backends and not args.system_info:
        print_welcome()
    
    # 参数验证
    if args.concurrent < 1 or args.concurrent > 8:
        print(f"{Fore.RED}❌ 并发数必须在1-8之间{Style.RESET_ALL}")
        sys.exit(1)
    
    # 显示系统信息
    if args.system_info:
        HardwareDetector.print_system_info()
        return
    
    # 显示可用后端
    if args.list_backends:
        detector = HardwareDetector()
        backends = detector.detect_available_backends()
        print(f"\n{Fore.CYAN}🖥️ 可用硬件后端:{Style.RESET_ALL}")
        for backend, available in backends.items():
            status = f"{Fore.GREEN}✓{Style.RESET_ALL}" if available else f"{Fore.RED}✗{Style.RESET_ALL}"
            config = detector.get_optimal_config(backend)
            print(f"  {status} {backend.upper()}: {config}")
        print()
        return
    
    # 检查模型文件
    if not os.path.exists(args.model):
        print(f"{Fore.RED}❌ 模型文件不存在: {args.model}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}请确保模型文件路径正确{Style.RESET_ALL}")
        sys.exit(1)
    
    # 自动设置线程数
    if args.threads == 0:
        args.threads = min(8, psutil.cpu_count())
    
    config = {
        'temperature': args.temperature,
        'max_tokens': args.max_tokens,
        'n_threads': args.threads
    }
    
    # 单次问答模式
    if args.prompt:
        SimplePromptInterface.run_single_prompt(
            args.model, 
            args.prompt, 
            backend=args.backend,
            monitor=args.monitor,
            **config
        )
        return
    
    # 交互模式
    cli = ChatCLI(enable_monitoring=args.monitor, max_concurrent=args.concurrent)
    cli.run(args.model, backend=args.backend, **config)


if __name__ == "__main__":
    main()