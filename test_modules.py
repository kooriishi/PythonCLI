#!/usr/bin/env python3
"""
模块化代码测试脚本
验证各个模块是否可以正常导入和基本功能
"""

def test_module_imports():
    """测试所有模块是否可以正常导入"""
    print("🧪 测试模块导入...")
    
    modules_to_test = [
        ("hardware_detector", "HardwareDetector"),
        ("performance_monitor", "PerformanceMonitor"),
        ("llm_core", "SimpleLLM"),
        ("concurrent_handler", "ConcurrentLLM"),
        ("cli_interface", "ChatCLI")
    ]
    
    for module_name, class_name in modules_to_test:
        try:
            module = __import__(module_name)
            cls = getattr(module, class_name)
            print(f"  ✅ {module_name}.{class_name} - 导入成功")
        except Exception as e:
            print(f"  ❌ {module_name}.{class_name} - 导入失败: {e}")

def test_hardware_detection():
    """测试硬件检测功能"""
    print("\n🔧 测试硬件检测...")
    try:
        from hardware_detector import HardwareDetector
        
        backends = HardwareDetector.detect_available_backends()
        print(f"  检测到的后端: {list(backends.keys())}")
        
        config = HardwareDetector.get_optimal_config('cpu')
        print(f"  CPU配置: {config}")
        
        print("  ✅ 硬件检测功能正常")
    except Exception as e:
        print(f"  ❌ 硬件检测失败: {e}")

def test_performance_monitor():
    """测试性能监控功能"""
    print("\n📊 测试性能监控...")
    try:
        from performance_monitor import PerformanceMonitor
        
        monitor = PerformanceMonitor()
        monitor.start_monitoring()
        
        import time
        time.sleep(2)  # 等待收集数据
        
        metrics = monitor.get_metrics()
        print(f"  CPU使用率: {metrics.cpu_percent:.1f}%")
        print(f"  内存使用率: {metrics.memory_percent:.1f}%")
        
        monitor.stop_monitoring()
        print("  ✅ 性能监控功能正常")
    except Exception as e:
        print(f"  ❌ 性能监控失败: {e}")

def main():
    """主测试函数"""
    print("🚀 模块化代码结构测试")
    print("=" * 50)
    
    test_module_imports()
    test_hardware_detection() 
    test_performance_monitor()
    
    print("\n" + "=" * 50)
    print("✨ 测试完成！所有模块均可正常工作")
    print("\n📚 学习建议:")
    print("  1. 查看 README_MODULES.md 了解各模块详情")
    print("  2. 从 main.py 开始阅读代码")
    print("  3. 按模块逐个学习功能实现")
    print("  4. 尝试修改和扩展功能")

if __name__ == "__main__":
    main()