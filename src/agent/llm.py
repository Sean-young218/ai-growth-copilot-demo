import json
import os
import urllib.error
import urllib.request


def call_llm(prompt):
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return _fallback_answer()

    base_url = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
    model = os.environ.get("OPENAI_MODEL", "gpt-4.1-mini")
    request = urllib.request.Request(
        f"{base_url.rstrip('/')}/chat/completions",
        data=json.dumps(
            {
                "model": model,
                "messages": [
                    {
                        "role": "system",
                        "content": "你是谨慎的 B2B 销售运营分析助手，只能基于提供资料生成建议。",
                    },
                    {"role": "user", "content": prompt},
                ],
                "temperature": 0.2,
            }
        ).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=45) as response:
            payload = json.loads(response.read().decode("utf-8"))
            return payload["choices"][0]["message"]["content"]
    except (KeyError, urllib.error.URLError, TimeoutError) as error:
        return _fallback_answer(error=str(error))


def _fallback_answer(error=None):
    prefix = ""
    if error:
        prefix = f"> LLM 调用失败，以下为本地兜底分析，需人工复核。错误：{error}\n\n"
    else:
        prefix = "> 未配置 OPENAI_API_KEY，以下为本地兜底分析，需人工复核。\n\n"

    return (
        prefix
        + "## 线索评分\n"
        + "70/100。客户表达了明确业务痛点，但预算、决策链、当前系统和试点范围仍需确认。\n\n"
        + "## 意向等级\n"
        + "中高意向。已有业务目标和产品兴趣，但采购条件不完整。\n\n"
        + "## 客户痛点\n"
        + "希望降低人工处理压力，提升销售或客服跟进效率，并把资料沉淀为可复用流程。\n\n"
        + "## 缺失信息\n"
        + "预算范围、决策人、当前系统、数据质量、试点范围、期望成功指标。\n\n"
        + "## 风险点\n"
        + "不能承诺固定价格、固定交付周期、准确率、ROI 或客户案例；相关内容需人工确认。\n\n"
        + "## 下一步动作\n"
        + "24 小时内跟进，先澄清当前系统、数据来源、业务目标和试点边界，再判断是否安排 Demo。\n\n"
        + "## 跟进话术\n"
        + "您好，我们看到您希望先验证 AI 方案的实际效果。为了判断是否适合小范围试点，想先确认当前系统、可用资料、预计试点渠道和成功指标。\n\n"
        + "## 是否需要人工复核\n"
        + "需要。涉及周期、预算、客户案例、准确率或合规承诺时必须人工复核。"
    )
