---
name: lead-scoring-followup
description: Analyze B2B marketing and sales leads, query product or service assets, score lead quality, identify risks and missing information, and produce follow-up guidance with an auditable ReAct trace.
metadata:
  version: "0.1.0"
---

# Lead Scoring Follow-up Skill

Use this skill when a user provides a potential customer lead that needs sales prioritization, pain point analysis, missing-information discovery, risk review, and follow-up suggestions.

## Required Process

1. Read the lead context and summarize the route decision in a short reasoning summary.
2. Call `query_product` before producing the final answer.
3. Observe matched product assets, sales SOP, forbidden claims, and source names.
4. Generate the final answer using only the lead context and observed business assets.

## Output Sections

Return a clear Markdown answer with these sections:

- 线索评分
- 意向等级
- 客户痛点
- 缺失信息
- 风险点
- 下一步动作
- 跟进话术
- 是否需要人工复核

## Guardrails

- 不得编造价格、交付周期、客户案例或产品能力。
- 如果资料中没有支持信息，必须标为“需人工确认”。
- 如果客户要求固定价格、固定周期、准确率、ROI、行业案例或合规承诺，必须提示人工复核。
- Follow-up suggestions should be specific enough for a salesperson to use, but must not over-promise.
