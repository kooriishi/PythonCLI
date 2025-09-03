#!/usr/bin/env python3
"""
硬件检测模块
提供硬件后端检测和配置优化功能
"""

import subprocess
import platform
from typing import Dict

try:
    import psutil
except ImportError as e:
    print(f"请安装依赖: pip install psutil")
    raise e


class HardwareDetector:
    """硬件检测和配置类"""
    
    @staticmethod
    def detect_available_backends() -> Dict[str, bool]:
        """检测可用的硬件后端"""
        backends = {
            'cpu': True,  # CPU总是可用的
            'cuda': False,
            'opencl': False,
            'metal': False
        }
        
        try:
            # 检测CUDA
            result = subprocess.run(['nvidia-smi'], capture_output=True, timeout=5)
            if result.returncode == 0:
                backends['cuda'] = True
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass
        
        try:
            # 检测OpenCL（简化检测）
            if platform.system() in ['Linux', 'Windows']:
                backends['opencl'] = True
        except:
            pass
            
        try:
            # 检测Metal（macOS）
            if platform.system() == 'Darwin':
                backends['metal'] = True
        except:
            pass
        
        return backends
    
    @staticmethod
    def get_optimal_config(backend: str) -> Dict:
        """根据后端获取最优配置"""
        configs = {
            'cpu': {
                'n_gpu_layers': 0,
                'n_threads': min(8, psutil.cpu_count())
            },
            'cuda': {
                'n_gpu_layers': 32,  # 根据模型调整
                'n_threads': 1
            },
            'opencl': {
                'n_gpu_layers': 16,
                'n_threads': 2
            },
            'metal': {
                'n_gpu_layers': 32,
                'n_threads': 1
            }
        }
        return configs.get(backend, configs['cpu'])
    
    @staticmethod
    def get_system_info() -> Dict:
        """获取系统信息"""
        info = {
            'platform': platform.system(),
            'architecture': platform.machine(),
            'cpu_count': psutil.cpu_count(),
            'memory_total_gb': psutil.virtual_memory().total / (1024**3),
            'python_version': platform.python_version()
        }
        
        # 尝试获取GPU信息
        try:
            result = subprocess.run(['nvidia-smi', '--query-gpu=name,memory.total', '--format=csv,noheader,nounits'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                gpu_info = result.stdout.strip().split(',')
                if len(gpu_info) >= 2:
                    info['gpu_name'] = gpu_info[0].strip()
                    info['gpu_memory_mb'] = int(gpu_info[1].strip())
        except:
            info['gpu_name'] = 'Not available'
            info['gpu_memory_mb'] = 0
        
        return info
    
    @classmethod
    def print_system_info(cls):
        """打印系统信息"""
        try:
            from colorama import Fore, Style
        except ImportError:
            Fore = Style = type('', (), {'RED': '', 'GREEN': '', 'CYAN': '', 'YELLOW': '', 'RESET_ALL': ''})()
        
        info = cls.get_system_info()
        backends = cls.detect_available_backends()
        
        print(f"\n{Fore.CYAN}🔍 系统信息:{Style.RESET_ALL}")
        print(f"  • 操作系统: {info['platform']} ({info['architecture']})")
        print(f"  • CPU核心数: {info['cpu_count']}")
        print(f"  • 内存大小: {info['memory_total_gb']:.1f}GB")
        print(f"  • Python版本: {info['python_version']}")
        print(f"  • GPU: {info['gpu_name']}")
        if info['gpu_memory_mb'] > 0:
            print(f"  • GPU显存: {info['gpu_memory_mb']/1024:.1f}GB")
        
        print(f"\n{Fore.CYAN}🖥️ 可用后端:{Style.RESET_ALL}")
        for backend, available in backends.items():
            status = f"{Fore.GREEN}✓{Style.RESET_ALL}" if available else f"{Fore.RED}✗{Style.RESET_ALL}"
            config = cls.get_optimal_config(backend)
            print(f"  {status} {backend.upper()}: {config}")
        print()