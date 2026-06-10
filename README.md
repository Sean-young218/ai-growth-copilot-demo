# AI Growth Copilot

AI Growth Copilot 是一个本地可运行的 Web Demo，用于辅助 B2B 营销和销售团队分析潜在客户线索。用户输入或选择一条线索后，系统会加载 `lead-scoring-followup` Skill，查询本地业务资料，并按 ReAct 风格生成线索评分、意向等级、痛点、缺失信息、风险点和跟进建议。

项目重点不在复杂 UI 或真实 CRM 集成，而在跑通一个可审计的最小 Agent 闭环：

```text
线索输入
  ↓
加载 lead-scoring-followup Skill
  ↓
Reasoning Summary / Route Decision
  ↓
Act: 调用 query_product
  ↓
Observe: 返回产品资料、销售 SOP、禁止承诺事项
  ↓
Answer: LLM 生成结构化分析
  ↓
前端展示分析结果和执行 Trace
```

## 功能概览

- 在 Web 页面中输入线索上下文，或选择内置示例线索。
- 使用 `skills/lead-scoring-followup/SKILL.md` 约束分析流程和输出章节。
- 通过 `query_product` Tool 查询本地 mock 业务资产。
- 调用 OpenAI-compatible Chat Completions 接口，默认示例配置为 DeepSeek。
- 在没有配置 API Key 或 LLM 调用失败时，返回本地兜底结果并提示人工复核。
- 前端展示最终 Markdown 分析结果和本次执行 Trace。

## 目录结构

```text
.
├── data/
│   ├── product_catalog.json      # 产品/服务 mock 资料
│   ├── sales_sop.md              # 销售跟进 SOP
│   └── forbidden_claims.md       # 禁止承诺事项
├── public/
│   ├── index.html                # 前端页面
│   ├── app.js                    # 示例线索、接口调用、结果和 Trace 渲染
│   └── styles.css                # 页面样式
├── skills/
│   └── lead-scoring-followup/
│       └── SKILL.md              # Agent Skill 定义
├── src/
│   ├── server.py                 # 标准库 HTTP 服务和 API 路由
│   ├── agent/
│   │   ├── skill_loader.py       # Skill frontmatter/body 加载
│   │   ├── runner.py             # ReAct 风格 Runner
│   │   ├── prompt_builder.py     # Prompt 组装
│   │   └── llm.py                # LLM 调用与兜底输出
│   └── tools/
│       └── query_product.py      # 本地业务资料查询工具
├── tests/                        # 单元测试
├── RUNNING.md                    # 简短运行说明
├── solution.md                   # 设计说明
└── .env.example                  # LLM 配置示例
```

## 环境要求

- Python 3.9+
- 无第三方 Python 依赖
- 可选：DeepSeek 或其他兼容 OpenAI Chat Completions 的 API Key

## 配置 LLM

复制 `.env.example` 为 `.env`，并填入 API Key：

```bash
cp .env.example .env
```

DeepSeek 示例配置：

```env
OPENAI_API_KEY=your_deepseek_api_key
OPENAI_BASE_URL=https://api.deepseek.com
OPENAI_MODEL=deepseek-chat
```

代码使用 OpenAI-compatible 接口格式，请求路径为：

```text
{OPENAI_BASE_URL}/chat/completions
```

如果不配置 `OPENAI_API_KEY`，系统仍可运行，但会返回本地兜底分析，并在结果中标明需要人工复核。

## 启动项目

```bash
python3 src/server.py
```

启动后打开：

```text
http://127.0.0.1:8000
```

服务默认监听 `127.0.0.1:8000`。

## 运行测试

```bash
python3 -m unittest discover -s tests
```

当前测试覆盖了 Runner 基本输出和 `query_product` 的资料匹配逻辑。

## API

### `POST /api/analyze-lead`

请求体：

```json
{
  "leadText": "来源：官网表单\n公司：某制造业企业\n行业：制造业\n感兴趣产品：AI 客服解决方案\n客户留言：希望降低售后咨询压力..."
}
```

响应体包含：

```json
{
  "skill": {
    "name": "lead-scoring-followup",
    "version": "0.1.0",
    "description": "..."
  },
  "answer": "Markdown 分析结果",
  "trace": [
    { "step": "Skill" },
    { "step": "Reasoning Summary" },
    { "step": "Act" },
    { "step": "Observe" },
    { "step": "Answer" }
  ],
  "context": {
    "leadText": "...",
    "interestedProduct": "...",
    "promptPreview": "..."
  },
  "toolObservation": {
    "toolName": "query_product",
    "matchedProducts": [],
    "salesSop": "...",
    "forbiddenClaims": [],
    "sources": []
  }
}
```

## Agent 流程

### 1. Skill 加载

`src/agent/skill_loader.py` 读取 `skills/lead-scoring-followup/SKILL.md`，解析 frontmatter 中的 `name`、`description` 和 `metadata.version`，并把正文作为约束注入 Prompt。

### 2. 路由判断

`src/agent/runner.py` 从线索文本中提取感兴趣产品。如果文本未明确产品名称，则使用原始线索做宽泛匹配，并在 Trace 中提示需要补充产品兴趣。

### 3. Tool 调用

Runner 在生成最终答案前调用 `query_product`。该 Tool 会读取：

- `data/product_catalog.json`
- `data/sales_sop.md`
- `data/forbidden_claims.md`

匹配策略以产品名、关键词和目标行业为主。如果没有命中，会返回部分产品作为宽泛上下文，并标记 `matchStrategy=broad_context`。

### 4. LLM 生成

`src/agent/prompt_builder.py` 将 Skill、线索上下文和 Tool 观察结果拼成 Prompt。`src/agent/llm.py` 调用兼容 OpenAI 的 Chat Completions 接口，系统提示要求模型只能基于提供资料生成建议。

### 5. Trace 展示

前端会展示关键执行过程，而不是完整模型内部思维链。Trace 包括：

- Skill 名称、版本和路径
- Reasoning Summary / Route Decision
- Tool 调用输入
- Tool 观察摘要
- Answer 输出预览

## 输出章节

LLM 输出要求包含以下 Markdown 标题：

- 线索评分
- 意向等级
- 客户痛点
- 缺失信息
- 风险点
- 下一步动作
- 跟进话术
- 是否需要人工复核

## 风险控制

项目通过三层方式减少幻觉和过度承诺：

1. `SKILL.md` 明确禁止编造价格、交付周期、客户案例或产品能力。
2. `query_product` 返回禁止承诺事项，并把资料来源放入 Trace。
3. Prompt 要求如果资料没有支持，必须写“需人工确认”。

当客户询问固定价格、固定周期、准确率、ROI、行业案例或合规承诺时，输出应提示人工复核。

## 本地兜底

如果出现以下情况，系统不会中断页面流程，而是返回兜底分析：

- 未配置 `OPENAI_API_KEY`
- LLM 请求超时
- LLM 响应格式异常
- 网络或接口调用失败

兜底结果会明确标注“需人工复核”，避免把静态结果误认为真实模型判断。

## 当前边界

- 业务资料来自本地 mock 文件，没有接入真实 CRM、数据库或搜索引擎。
- 产品匹配是关键词加权，不是向量检索。
- Trace 展示的是审计摘要，不展示完整模型内部推理链。
- 前端 Markdown 渲染只支持当前 demo 需要的基础格式。
- 服务使用 Python 标准库 HTTP Server，适合本地演示，不作为生产部署方案。

## 常用命令

```bash
# 启动
python3 src/server.py

# 测试
python3 -m unittest discover -s tests

# 直接调用接口
curl -X POST http://127.0.0.1:8000/api/analyze-lead \
  -H "Content-Type: application/json" \
  --data '{"leadText":"来源：官网表单\n公司：某制造业企业\n行业：制造业\n感兴趣产品：AI 客服解决方案\n客户留言：希望降低售后咨询压力，想先做小范围试点。"}'
```
