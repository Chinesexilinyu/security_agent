# 项目介绍
本仓库包含两个独立的实用工具项目，分别为基于LangGraph的通用Agent服务框架和PDF论文知识库生成工具，可帮助开发者快速构建智能应用和知识库系统。
---
## 📋 项目概述
### 1. 通用Agent服务框架
基于FastAPI + LangGraph构建的高性能Agent服务框架，支持工作流编排、异步执行、流式输出、任务取消等企业级特性，同时兼容OpenAI API标准，可直接对接各类OpenAI生态工具。
### 2. PDF论文处理器
专门为网络安全科研论文设计的智能文本处理工具，能够将PDF论文自动转换为Dify知识库可直接导入的高质量结构化数据，支持语义感知分割、元数据自动提取、多格式输出等功能。
---
## ✨ 核心功能
### Agent服务框架核心功能
✅ **多运行模式支持**：HTTP服务模式、本地工作流运行模式、单节点调试模式
✅ **异步流式输出**：支持SSE流式响应，实时推送执行过程和结果
✅ **任务生命周期管理**：支持任务查询、主动取消、超时控制等完整生命周期管理
✅ **OpenAI API兼容**：提供`/v1/chat/completions`接口，可直接对接OpenAI生态工具
✅ **工作流编排**：基于LangGraph灵活编排复杂Agent工作流
✅ **可观测性**：内置完善的日志、错误分类和追踪能力
✅ **健康检查**：提供健康检查接口，方便K8s等容器环境部署
### PDF论文处理器核心功能
✅ **智能PDF文本提取**：基于PyMuPDF高精度提取PDF文本内容
✅ **语义感知分割**：基于论文章节结构进行智能分块，保持语义完整性
✅ **元数据自动提取**：从目录结构和PDF内容自动提取分类、年份、章节等元数据
✅ **Dify兼容输出**：直接生成CSV/JSON格式，可一键导入Dify知识库
✅ **灵活配置**：支持自定义分块大小、重叠率、输出格式等参数
✅ **批量处理**：支持批量处理整个目录的PDF文件
✅ **统计分析**：自动生成处理统计报告，便于数据分析
---
## 🏗️ 技术架构
### Agent服务架构
```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   HTTP接口层    │────▶│   服务编排层    │────▶│   工作流执行层   │
│  (FastAPI)      │     │ (GraphService)  │     │  (LangGraph)    │
└─────────────────┘     └─────────────────┘     └─────────────────┘
         ▲                        ▲                        ▲
         │                        │                        │
         ▼                        ▼                        ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  OpenAI兼容层   │     │  任务管理层     │     │  工具调用层     │
│(OpenAIChatHandler)│   │(running_tasks)  │     │(自定义工具集)   │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```
**技术栈**：
- Web框架：FastAPI + Uvicorn
- 工作流引擎：LangGraph
- 异步处理：Asyncio + 多线程
- 日志系统：结构化JSON日志
- 序列化：Pydantic
### PDF处理器架构
```
PDF文件 → PDF文本提取器 → 文本清洗器 → 章节识别器 → 语义分割器 → 元数据注入器 → 输出管理器 → Dify知识库
```
**技术栈**：
- PDF处理：PyMuPDF (fitz)
- 数据处理：Pandas
- 进度显示：tqdm
- 输出格式：CSV / JSON
---
## 📦 环境依赖
### 基础环境要求
- Python 3.8+
- pip 20.0+
### 依赖包列表
| 包名 | 版本 | 用途 |
|------|------|------|
| PyMuPDF | 1.24.5 | PDF文本提取 |
| tqdm | 4.66.1 | 进度条显示 |
| pandas | 2.2.0 | 数据处理 |
| fastapi | 最新 | Web服务框架 |
| uvicorn | 最新 | ASGI服务器 |
| langgraph | 最新 | 工作流引擎 |
| langchain-core | 最新 | LangChain核心库 |
---
## 🚀 安装部署
### 1. 克隆项目
```bash
git clone <仓库地址>
```
### 2. 安装依赖
```bash
pip install -r requirements.txt
```
---
## 📖 使用指南
### 一、Agent服务框架使用
#### 1. 启动HTTP服务
```bash
# 默认端口5000
python src/main.py -m http
# 指定端口
python src/main.py -m http -p 8080
```
#### 2. 本地运行工作流
```bash
python src/main.py -m flow -i '{"text": "你的问题"}'
```
#### 3. 运行单个节点（调试用）
```bash
python src/main.py -m node -n <节点ID> -i '{"输入参数": "值"}'
```
---
### 二、PDF论文处理器使用
#### 1. 准备论文数据
按照以下目录结构组织PDF论文：
```
papers/
├── 漏洞挖掘/
│   ├── 2024/
│   │   └── paper1.pdf
│   └── 2023/
├── 漏洞修复/
│   └── 2024/
├── LLM安全/
│   └── 2024/
└── 其他/
    └── 2024/
```
> 注意：文件夹名称使用中文便于自动识别论文分类。
#### 2. 运行处理脚本
##### 基本用法
```bash
python process_papers.py --input ./papers
```
##### 完整参数示例
```bash
python process_papers.py \
  --input ./papers \
  --output ./dify_data \
  --chunk-size 800 \
  --overlap 200 \
  --format csv \
  --output-name cyber_security_papers
```
##### 处理单个文件
```bash
python process_papers.py --input ./paper.pdf --single-file
```
#### 3. 参数说明
| 参数 | 简写 | 默认值 | 说明 |
|------|------|--------|------|
| `--input` | `-i` | 必需 | 输入目录或PDF文件路径 |
| `--output` | `-o` | `output` | 输出目录 |
| `--chunk-size` | - | `700` | 分块大小（字符数） |
| `--overlap` | - | `150` | 分块重叠大小（字符数） |
| `--format` | - | `csv` | 输出格式（csv/json） |
| `--single-file` | - | `False` | 处理单个文件 |
| `--output-name` | - | `dify_knowledge_base` | 输出文件名 |
---
## 🔌 API接口说明（Agent服务）
### 1. 同步执行接口
```http
POST /run
Content-Type: application/json
{
  "your": "input_data"
}
```
### 2. 流式执行接口
```http
POST /stream_run
Content-Type: application/json
{
  "your": "input_data"
}
```
> 返回SSE流式响应，实时推送执行结果
### 3. 取消任务接口
```http
POST /cancel/{run_id}
```
### 4. 单节点执行接口
```http
POST /node_run/{node_id}
Content-Type: application/json
{
  "node_input": "data"
}
```
### 5. OpenAI兼容接口
```http
POST /v1/chat/completions
Content-Type: application/json
{
  "model": "your-model",
  "messages": [{"role": "user", "content": "你好"}]
}
```
### 6. 健康检查接口
```http
GET /health
```
### 7. 工作流Schema接口
```http
GET /graph_parameter
```
> 返回工作流的输入输出Schema
---
## 📊 输出说明
### PDF处理器输出
处理完成后会生成两个文件：
1. **主数据文件**（CSV/JSON）：包含分块后的文本内容、元数据和来源信息
2. **统计文件**（JSON）：包含处理总chunk数、按分类/年份/章节的统计信息
**元数据结构**：
```json
{
  "category": "vulnerability_mining",
  "category_cn": "漏洞挖掘",
  "year": "2024",
  "section": "Abstract",
  "chunk_id": 1,
  "source_file": "paper1.pdf",
  "char_count": 685,
  "title": "论文标题"
}
```
---
## 💡 最佳实践
### Agent服务部署建议
- 生产环境使用多worker部署，推荐2-4个worker
- 配置合理的超时时间，默认15分钟可根据业务调整
- 日志文件默认保存在`logs/`目录，建议定期清理
- 生产环境关闭reload模式
### PDF分块参数建议
| 场景 | Chunk大小 | 重叠率 |
|------|-----------|--------|
| 精确检索 | 300-500 | 10-15% |
| 通用场景 | 500-800 | 20-30% |
| 长文理解 | 800-1200 | 25-35% |
| 复杂推理 | 1200+ | 30-40% |
---
## ⚠️ 常见问题
### Agent服务相关
**Q：服务启动失败提示端口被占用？**
A：使用`-p`参数指定其他端口，或关闭占用端口的程序。
**Q：流式响应中断怎么办？**
A：检查网络连接，或调整超时时间配置。
### PDF处理相关
**Q：PDF无法提取文本？**
A：扫描版PDF需要先使用OCR工具识别文本层。
**Q：Dify导入失败？**
A：检查CSV文件编码是否为UTF-8，确保没有特殊字符。
**Q：元数据识别不准确？**
A：确保目录结构符合要求，文件夹名称使用标准分类名称。

---
**祝您使用愉快！🚀**