# CLAUDE.md

本文件为 Claude Code (claude.ai/code) 在此代码库中工作时提供指导。

## 开发命令

### 安装和配置
```bash
# 安装所有可选依赖
uv pip install -e ".[gui,rag,code_interpreter,mcp]"

# 最小化安装
uv pip install -e .
```

### 测试
```bash
# 运行所有测试
python -m pytest tests/

# 运行特定测试文件
python -m pytest tests/agents/test_assistant.py

# 运行详细输出的测试
python -m pytest -v tests/

# 运行特定组件的测试
python -m pytest tests/llm/
python -m pytest tests/tools/
```

### 代码质量
```bash
# 运行所有 pre-commit 钩子
pre-commit run --all-files

# 单独运行代码检查工具
flake8 --max-line-length=300 .
yapf --style="{based_on_style: google, column_limit: 120}" -r .
isort --line-length 120 .
```

### 包构建
```bash
# 为 PyPI 构建包
python setup.py sdist bdist_wheel
```

## 架构概览

Qwen-Agent 是一个用于开发 LLM 应用程序的框架，具有三个核心架构层：

### 1. 基础组件
- **BaseChatModel** (`qwen_agent/llm/base.py`)：所有 LLM 实现的抽象基类，支持函数调用
- **BaseTool** (`qwen_agent/tools/base.py`)：所有工具的抽象基类，提供标准化接口
- **Agent** (`qwen_agent/agent.py`)：所有智能体实现的抽象基类

### 2. LLM 层 (`qwen_agent/llm/`)
- 多种 LLM 后端：DashScope、OpenAI 兼容 API、Azure、Transformers
- 内置函数调用，支持可配置模板（Nous、Qwen 格式）
- 支持推理内容和并行函数调用
- 自动消息截断和令牌管理

### 3. 工具层 (`qwen_agent/tools/`)
- **内置工具**：代码解释器、网络搜索、文档解析、图像生成
- **MCP 集成**：模型上下文协议支持外部工具
- **自定义工具**：使用 `@register_tool('tool_name')` 装饰器注册
- **工具注册表**：所有可用工具的中央注册表

### 4. 智能体层 (`qwen_agent/agents/`)
主要智能体实现：
- **Assistant**：支持文件处理和工具使用的多模态智能体
- **ReActChat**：推理和行动的 ReAct 模式
- **FnCallAgent**：纯函数调用，无对话功能
- **GroupChat**：具有路由功能的多智能体对话

### 5. 内存系统 (`qwen_agent/memory/`)
- 用于处理长上下文的虚拟内存
- 基于 RAG 的文档检索，支持超长文档（1M+ 令牌）
- 自动内存管理和上下文截断

## 关键模式

### 智能体创建模式
```python
# 标准智能体配置
llm_cfg = {
    'model': 'qwen-max-latest',
    'model_type': 'qwen_dashscope',
    'generate_cfg': {
        'top_p': 0.8,
        'fncall_prompt_type': 'nous'  # 或 'qwen'
    }
}

agent = Assistant(
    llm=llm_cfg,
    function_list=['tool1', 'tool2'],
    system_message="自定义指令",
    files=['path/to/document.pdf']
)
```

### 自定义工具注册
```python
@register_tool('custom_tool')
class CustomTool(BaseTool):
    description = "为 LLM 提供的工具描述"
    parameters = [{'name': 'param', 'type': 'string', 'required': True}]
    
    def call(self, params: str, **kwargs) -> str:
        # 工具实现
        return result
```

## 环境要求

### 必需的环境变量
- `DASHSCOPE_API_KEY`：用于 DashScope 模型服务
- `OPENAI_API_KEY`：用于 OpenAI 兼容服务（可选）

### 可选依赖
- `[gui]`：基于 Gradio 的网页界面（需要 Python 3.10+）
- `[rag]`：文档处理和检索
- `[code_interpreter]`：代码执行能力
- `[mcp]`：模型上下文协议支持

## 重要说明

- 测试需要外部服务的 API 密钥
- 代码解释器未进行沙箱化 - 请谨慎使用
- Pre-commit 钩子强制执行 120 字符行限制和 Google 样式格式
- 框架支持流式和非流式响应
- 所有智能体都继承基类的消息截断和令牌管理功能

## 代码规范

### 注释语言要求
- **所有代码注释必须使用英文**
- 包括但不限于：
  - 函数和类的文档字符串 (docstring)
  - 行内注释 (inline comments)
  - 变量名和函数名应使用英文描述性命名
  - 日志输出信息使用英文
- 目的：保持代码库的国际化和可维护性

### 示例
```python
# 好的示例 (Good example)
def init_agent_service():
    # Enable detailed logging
    logger.info("[INIT] Starting agent initialization...")
    
# 避免的示例 (Avoid)
def init_agent_service():
    # 启用详细日志
    logger.info("[INIT] 开始初始化Agent...")
```

## 回答要求
- 使用与问题相同的语言回答。
- 代码打印、日志、注释、代码块等使用英文。