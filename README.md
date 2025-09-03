# 🚀 增强版本地量化模型推理工具

基于 `llama-cpp-python` 的本地量化模型推理工具，支持流式对话输出和丰富的增强功能。

## ✨ 功能特色

### 🎯 核心功能
- 🤖 **本地量化模型推理** - 基于 llama-cpp-python，支持 GGUF 格式模型
- 💬 **流式对话输出** - 实时显示生成过程，边生成边打印
- 📝 **对话历史管理** - 自动维护上下文，支持多轮对话（最多保留6轮）
- ⚙️ **可配置参数** - 支持温度、最大长度、线程数等推理参数调整
- 🎨 **彩色输出** - 使用颜色区分用户和助手消息，提升交互体验

### 🚀 增强功能
- 📊 **性能监控仪表盘** - 实时系统资源监控和推理性能统计
- 🖥️ **多硬件后端支持** - CPU/CUDA/OpenCL/Metal多种计算后端
- ⚡ **并发请求处理** - 多线程并发推理，提升处理效率
- 🔧 **智能硬件检测** - 自动检测最优硬件配置
- 📈 **实时性能统计** - 生成速度、响应时间等性能指标

## 🏗️ 模块化架构

### 📁 项目结构
```
PythonCLI/
├── main.py                    # 🚀 主程序入口
├── performance_monitor.py     # 📊 性能监控模块
├── hardware_detector.py       # 🔧 硬件检测模块
├── llm_core.py                # 🤖 LLM核心推理模块
├── concurrent_handler.py      # ⚡ 并发处理模块
├── cli_interface.py           # 💬 CLI交互界面模块
├── requirements.txt           # 📦 依赖包列表
├── test_modules.py            # 🧪 模块测试脚本
└── README.md                  # 📚 项目说明文档
```

### 📖 模块功能详解

#### 1. main.py - 主程序入口 🚀
- **职责**: 命令行参数解析、模块导入初始化、程序流程控制
- **代码量**: ~134行，简洁的程序入口
- **核心代码**:
  ```python
  # 模块导入
  from hardware_detector import HardwareDetector
  from performance_monitor import PerformanceMonitor
  from cli_interface import ChatCLI, SimplePromptInterface
  
  # 主函数
  def main():
      # 参数解析和程序启动
  ```

#### 2. performance_monitor.py - 性能监控模块 📊  
- **主要类**: `PerformanceMetrics`、`PerformanceMonitor`
- **功能**: 实时系统资源监控、推理性能统计、可视化数据展示
- **特色**: 线程安全的数据收集、ASCII进度条可视化
- **学习重点**:
  ```python
  # 性能数据收集
  self.metrics.cpu_percent = psutil.cpu_percent(interval=1)
  
  # 线程安全的数据访问
  with self.lock:
      self.metrics.total_requests += 1
  
  # 可视化进度条生成
  def _get_bar(self, percentage: float, width: int = 20):
  ```

#### 3. hardware_detector.py - 硬件检测模块 🔧
- **主要类**: `HardwareDetector`
- **功能**: 自动检测硬件后端、配置参数优化、系统信息获取
- **支持**: CPU/CUDA/OpenCL/Metal多种后端
- **学习重点**:
  ```python
  # 硬件检测逻辑
  @staticmethod
  def detect_available_backends() -> Dict[str, bool]:
      # CUDA检测
      result = subprocess.run(['nvidia-smi'], capture_output=True)
  
  # 配置优化策略
  @staticmethod
  def get_optimal_config(backend: str) -> Dict:
  ```

#### 4. llm_core.py - LLM核心推理模块 🤖
- **主要类**: `SimpleLLM`
- **功能**: 多后端模型加载、流式文本生成、对话历史管理
- **特色**: 线程安全推理、智能后端选择
- **学习重点**:
  ```python
  # 模型初始化
  self.llm = Llama(
      model_path=self.model_path,
      n_ctx=self.config['n_ctx'],
      n_threads=self.config['n_threads'],
      n_gpu_layers=self.config['n_gpu_layers']
  )
  
  # 流式生成器
  def generate_response(self, user_input: str) -> Generator[str, None, None]:
  
  # 线程安全保护
  with self.lock:
      self.chat_history.append(message)
  ```

#### 5. concurrent_handler.py - 并发处理模块 ⚡
- **主要类**: `ConcurrentLLM`、`RequestQueue`、`LoadBalancer`
- **功能**: 多线程并发推理、请求队列管理、负载均衡
- **优势**: 提升处理效率、资源保护机制
- **学习重点**:
  ```python
  # 并发控制
  self.executor = ThreadPoolExecutor(max_workers=max_concurrent)
  
  # 队列管理
  self.request_queue = queue.Queue()
  
  # 异步处理
  def generate_response_async(self, user_input: str, callback=None):
  ```

#### 6. cli_interface.py - CLI交互界面模块 💬
- **主要类**: `ChatCLI`、`SimplePromptInterface`
- **功能**: 用户交互界面、命令解析处理、界面美化
- **体验**: 友好的用户界面、丰富的交互命令
- **学习重点**:
  ```python
  # 命令处理模式
  def handle_command(self, command: str) -> bool:
  
  # 界面展示
  def print_banner(self):
  
  # 用户输入处理
  user_input = input(f"\n{Fore.BLUE}你: {Style.RESET_ALL}")
  ```

## 🚀 快速开始

### 📦 安装依赖
```bash
pip install -r requirements.txt
```

**依赖包列表**:
- `llama-cpp-python==0.2.85` - 本地量化模型推理引擎
- `colorama==0.4.6` - 跨平台彩色终端输出
- `psutil==5.9.8` - 系统性能监控
- `aiohttp==3.9.1` - 异步HTTP支持

### 🎮 使用方法

#### 基础使用
```bash
# 交互模式（推荐）
python main.py

# 指定模型路径
python main.py --model path/to/your/model.gguf

# 单次问答模式
python main.py --prompt "你好，介绍一下你自己"
```

#### 增强功能使用
```bash
# 性能监控模式
python main.py --monitor --backend auto

# 高性能并发模式  
python main.py --concurrent 3 --monitor --backend cuda

# 查看系统信息
python main.py --system-info

# 查看可用硬件后端
python main.py --list-backends
```

## 📋 命令行参数

| 参数 | 缩写 | 默认值 | 说明 |
|------|------|--------|------|
| `--model` | `-m` | `models/qwen1_5-0_5b-chat-q4_0.gguf` | 模型文件路径 |
| `--backend` | `-b` | `auto` | 硬件后端选择 (auto/cpu/cuda/opencl/metal) |
| `--temperature` | `-t` | `0.7` | 温度参数 (0.1-2.0) |
| `--max-tokens` | `-l` | `512` | 最大生成长度 |
| `--threads` | `-j` | `0` | CPU线程数 (0=自动) |
| `--concurrent` | `-c` | `1` | 最大并发请求数 (1-8) |
| `--monitor` | - | `false` | 启用性能监控 |
| `--prompt` | `-p` | - | 单次问答模式 |
| `--list-backends` | - | - | 显示可用硬件后端 |
| `--system-info` | - | - | 显示系统信息 |

## 🎮 交互命令

| 命令 | 功能说明 |
|------|----------|
| `/help` | 显示帮助信息 |
| `/clear` | 清空聊天历史和屏幕 |
| `/stats` | 显示详细统计信息 |
| `/monitor` | 切换性能监控显示 |
| `/backends` | 显示硬件后端信息 |
| `/system` | 显示系统信息 |
| `/quit` | 退出程序 |

## 💡 增强功能详解

### 📊 性能监控仪表盘

#### 功能特性
- **实时系统资源监控**：CPU使用率、内存使用情况
- **GPU监控**：支持NVIDIA GPU使用率和显存监控（需安装GPUtil）
- **推理性能统计**：请求数量、响应时间、生成速度（tokens/s）
- **可视化显示**：ASCII进度条和彩色状态指示

#### 使用方法
```bash
# 启动时启用性能监控
python main.py --monitor

# 运行时查看性能仪表盘
/monitor

# 查看详细统计信息
/stats
```

### 🖥️ 多硬件后端支持

#### 支持的硬件后端
- **CPU**：通用CPU推理（默认）
- **CUDA**：NVIDIA GPU加速
- **OpenCL**：跨平台GPU加速
- **Metal**：Apple Silicon GPU加速（macOS）

#### 自动检测和优化
- 自动检测可用硬件后端
- 根据硬件类型优化配置参数
- 智能选择最佳后端

#### 使用方法
```bash
# 自动选择最佳后端
python main.py --backend auto

# 指定使用CUDA GPU
python main.py --backend cuda

# 指定使用CPU
python main.py --backend cpu

# 查看可用后端
python main.py --list-backends

# 运行时查看后端信息
/backends
```

### ⚡ 并发请求处理

#### 功能特性
- **多线程并发**：支持同时处理多个推理请求
- **请求队列管理**：智能排队和负载均衡
- **资源保护**：防止系统资源过载
- **线程安全**：确保模型访问的线程安全

#### 使用方法
```bash
# 启用3个并发线程
python main.py --concurrent 3

# 查看并发状态
/stats
```

## 📈 使用示例

### 基础对话示例
```bash
$ python main.py

🚀 增强版本地量化模型推理工具
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✨ 新增功能:
  • 🖥️  性能监控仪表盘
  • 🔧 多硬件后端支持 (CPU/CUDA/OpenCL/Metal)
  • ⚡ 并发请求处理

正在加载模型: qwen1_5-0_5b-chat-q4_0.gguf
使用后端: CUDA
✅ 模型加载成功!

💬 开始对话! (输入 /help 查看命令)

你: 你好，介绍一下你自己

助手: 你好！我是基于 Qwen1.5-0.5B 模型的 AI 助手，运行在你的本地设备上。我可以帮你解答问题、进行对话交流，支持中文对话。有什么我可以帮助你的吗？

📊 89 字符 | 1.23s | 72.4 字符/秒 | 67 tokens
```

### 性能监控示例
```bash
你: /monitor

🖥️  性能监控仪表盘
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 系统资源:
  • CPU:  15.2% [███▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒]
  • 内存: 68.4% (10.9GB) [█████████████▒▒▒▒▒▒▒]
  • GPU:  45.0% (0.9GB) [█████████▒▒▒▒▒▒▒▒▒▒▒]

🚀 推理性能:
  • 总请求数: 5
  • 活跃请求: 0
  • 平均响应: 1.45s
  • 生成速度: 68.9 tokens/s
  • 运行时间: 0:03:42
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## 🔧 配置优化建议

### CPU模式推荐配置
```bash
python main.py --backend cpu --threads 8 --concurrent 1
```
- **线程数**: CPU核心数的1-2倍
- **并发数**: 1-2个请求
- **适用场景**: 兼容性要求高的环境

### GPU模式推荐配置  
```bash
python main.py --backend cuda --concurrent 3 --monitor
```
- **线程数**: 1-2个（GPU模式下CPU线程较少）
- **并发数**: 根据显存大小，2-4个请求
- **适用场景**: 追求性能的高端设备

## 🧪 测试和验证

### 模块测试
```bash
# 测试所有模块
python test_modules.py

# 单独测试硬件检测
python -c "from hardware_detector import HardwareDetector; HardwareDetector.print_system_info()"

# 单独测试性能监控
python -c "from performance_monitor import PerformanceMonitor; m = PerformanceMonitor(); print('Monitor created')"
```

### 功能验证
```bash
# 查看系统信息
python main.py --system-info

# 查看可用后端
python main.py --list-backends

# 测试性能监控
python main.py --prompt "测试" --monitor
```

## 🎯 模块化设计优势

### 1. 职责分离 📋
- 每个模块专注于特定功能
- 降低代码复杂度，便于理解和维护
- 模块间低耦合，高内聚

### 2. 便于学习 📚
- 按功能模块逐个学习，学习曲线平缓
- 代码结构清晰明了，易于理解程序架构
- 每个模块100-300行，适合深入学习

### 3. 易于扩展 🔧
- 新功能可独立开发成新模块
- 支持功能插件化，灵活扩展
- 便于团队协作开发

### 4. 便于测试 🧪
- 可单独测试各模块功能
- 减少测试复杂度，提高测试覆盖率
- 便于问题定位和调试

## 📝 学习路径

### 初学者路径 🌱
1. **main.py** - 了解程序整体结构和参数处理
2. **hardware_detector.py** - 学习系统硬件检测技术
3. **performance_monitor.py** - 学习性能监控实现原理
4. **llm_core.py** - 理解AI模型推理核心过程
5. **cli_interface.py** - 学习用户界面设计模式
6. **concurrent_handler.py** - 学习并发编程技术

### 进阶学习 🚀
1. **设计模式**: 观察各模块中使用的设计模式
2. **性能优化**: 理解性能监控和优化策略
3. **并发编程**: 深入学习多线程处理技术
4. **模块化架构**: 理解模块间的依赖关系和接口设计

## 🔮 扩展建议

### 可添加的新模块
1. **config_manager.py** - 配置文件管理模块
2. **logging_system.py** - 完整的日志系统
3. **model_manager.py** - 多模型管理和切换
4. **api_server.py** - Web API接口模块
5. **data_processor.py** - 数据预处理模块

### 功能扩展方向
1. **Web界面** - 添加基于Web的用户界面
2. **API服务** - 提供RESTful API接口
3. **模型热切换** - 支持运行时动态切换模型
4. **插件系统** - 支持第三方功能插件扩展
5. **分布式推理** - 支持多节点分布式推理

## 📋 技术要求

### 系统要求
- **操作系统**: Windows/Linux/macOS
- **Python版本**: 3.8+
- **内存**: 至少 4GB（取决于模型大小）
- **CPU**: 支持多线程，推荐 4核+
- **GPU**: 可选，支持CUDA的NVIDIA显卡

### 模型要求
- **格式**: GGUF 量化格式模型
- **推荐模型**: Qwen、ChatGLM、Llama 等中文友好模型
- **大小**: 建议在 0.5B-7B 之间（根据硬件配置）

## 🚨 注意事项

1. **GPU监控**: 需要安装GPUtil包（`pip install GPUtil`）
2. **CUDA支持**: 需要NVIDIA驱动和CUDA工具包
3. **并发限制**: 建议根据系统资源设置合理的并发数
4. **内存管理**: 高并发模式下请注意内存使用情况
5. **模型兼容**: 确保使用GGUF格式的量化模型

## 🔄 兼容性说明

- ✅ **完全向后兼容**: 原有功能保持不变
- ✅ **可选新功能**: 所有增强功能都是可选的
- ✅ **渐进式升级**: 不影响现有的使用方式
- ✅ **模块化加载**: 可按需加载特定功能模块

## 🎉 项目亮点

✨ **架构优秀**: 模块化设计，代码结构清晰，易于学习和扩展
✨ **功能丰富**: 从基础推理到高级监控，覆盖本地AI推理全场景
✨ **性能优异**: 多后端支持、并发处理，充分发挥硬件性能
✨ **用户友好**: 彩色输出、实时统计、丰富交互，绝佳用户体验
✨ **技术先进**: 流式输出、线程安全、智能优化等现代化技术

## 📄 License

MIT License

---

**💡 提示**: 通过这种模块化的设计，代码变得更加清晰易懂，非常适合学习和后续的功能扩展！每个模块都可以独立理解和修改，是学习AI推理技术和Python模块化编程的绝佳项目。