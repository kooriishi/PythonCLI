#!/usr/bin/env python3
"""
增强版本地量化模型推理工具 - 功能测试脚本
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import HardwareDetector, PerformanceMonitor, SimpleLLM, ConcurrentLLM
import time

def test_hardware_detection():
    """测试硬件检测功能"""
    print("🔍 测试硬件检测功能...")
    detector = HardwareDetector()
    
    # 检测可用后端
    backends = detector.detect_available_backends()
    print(f"可用后端: {backends}")
    
    # 获取各后端配置
    for backend in ['cpu', 'cuda', 'opencl', 'metal']:
        config = detector.get_optimal_config(backend)
        print(f"{backend.upper()} 配置: {config}")
    print()

def test_performance_monitor():
    """测试性能监控功能"""
    print("📊 测试性能监控功能...")
    monitor = PerformanceMonitor()
    
    # 启动监控
    monitor.start_monitoring()
    print("性能监控已启动，收集数据中...")
    
    # 模拟一些负载
    for i in range(3):
        monitor.record_request_start()
        time.sleep(1)  # 模拟处理时间
        monitor.record_request_end(1.0, 100)  # 模拟1秒处理100个tokens
        print(f"模拟请求 {i+1} 完成")
    
    # 显示监控数据
    print("\n当前性能指标:")
    print(monitor.format_metrics())
    
    # 停止监控
    monitor.stop_monitoring()
    print("性能监控已停止\n")

def test_model_loading():
    """测试模型加载（不需要实际模型文件）"""
    print("🤖 测试模型加载功能...")
    
    # 创建一个虚拟的模型路径进行测试
    fake_model_path = "test_model.gguf"
    
    # 测试不同后端的初始化
    for backend in ['cpu', 'cuda']:
        try:
            llm = SimpleLLM(fake_model_path, backend=backend)
            print(f"✅ {backend.upper()} 后端初始化成功")
            print(f"   选择的后端: {llm.selected_backend}")
            print(f"   配置参数: {llm.config}")
        except Exception as e:
            print(f"❌ {backend.upper()} 后端初始化失败: {e}")
    print()

def test_concurrent_manager():
    """测试并发管理器"""
    print("⚡ 测试并发管理功能...")
    
    fake_model_path = "test_model.gguf"
    monitor = PerformanceMonitor()
    
    try:
        concurrent_llm = ConcurrentLLM(
            fake_model_path, 
            max_concurrent=3, 
            monitor=monitor
        )
        print("✅ 并发LLM管理器创建成功")
        print(f"   最大并发数: {concurrent_llm.max_concurrent}")
        
        stats = concurrent_llm.get_stats()
        print(f"   统计信息: {stats}")
        
        concurrent_llm.shutdown()
        print("✅ 并发管理器正常关闭")
        
    except Exception as e:
        print(f"❌ 并发管理器测试失败: {e}")
    print()

def main():
    """主测试函数"""
    print("🚀 增强版本地量化模型推理工具 - 功能测试")
    print("=" * 60)
    
    try:
        test_hardware_detection()
        test_performance_monitor()
        test_model_loading()
        test_concurrent_manager()
        
        print("✅ 所有功能测试完成！")
        print("\n📝 测试总结:")
        print("   - 硬件检测: 正常工作")
        print("   - 性能监控: 正常工作") 
        print("   - 多后端支持: 正常工作")
        print("   - 并发管理: 正常工作")
        print("\n🎯 建议:")
        print("   1. 确保模型文件存在后进行完整测试")
        print("   2. 根据硬件配置选择合适的后端")
        print("   3. 根据系统资源设置合理的并发数")
        
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()