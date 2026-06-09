from src.agent.llm import call_llm
from src.agent.prompt_builder import build_prompt
from src.agent.skill_loader import load_skill
from src.tools.query_product import query_product


def _extract_interested_product(lead_text):
    markers = ["感兴趣产品：", "感兴趣产品:", "产品：", "产品:"]
    for marker in markers:
        if marker in lead_text:
            after = lead_text.split(marker, 1)[1]
            return after.splitlines()[0].strip()
    if "AI 客服" in lead_text:
        return "AI 客服解决方案"
    if "线索" in lead_text or "增长" in lead_text:
        return "AI 增长线索 Copilot"
    return ""


def _summarize_route(lead_text, interested_product):
    reason = "线索包含客户需求或产品兴趣，需要查询产品资料、销售 SOP 和禁止承诺事项后再生成建议。"
    if not interested_product:
        reason = "线索没有明确产品名称，需要用原始文本进行宽泛产品资料匹配，并提示人工补充产品兴趣。"
    return reason


def run_lead_scoring_agent(payload):
    lead_text = payload.get("leadText", "").strip()
    if not lead_text:
        raise ValueError("leadText is required")

    llm_client = payload.get("llmClient") or call_llm
    skill = load_skill("lead-scoring-followup")
    interested_product = payload.get("interestedProduct") or _extract_interested_product(lead_text)
    reasoning_summary = _summarize_route(lead_text, interested_product)

    trace = [
        {
            "step": "Skill",
            "skillName": skill["name"],
            "skillVersion": skill["version"],
            "description": skill["description"],
            "path": skill["path"],
        },
        {
            "step": "Reasoning Summary",
            "summary": reasoning_summary,
            "routeDecision": "call_query_product",
        },
        {
            "step": "Act",
            "tool": "query_product",
            "input": {
                "leadText": lead_text,
                "interestedProduct": interested_product,
            },
        },
    ]

    observation = query_product(
        {
            "leadText": lead_text,
            "interestedProduct": interested_product,
        }
    )
    trace.append(
        {
            "step": "Observe",
            "tool": "query_product",
            "matchStrategy": observation["matchStrategy"],
            "matchedProducts": [item["name"] for item in observation["matchedProducts"]],
            "sources": observation["sources"],
            "forbiddenClaimsCount": len(observation["forbiddenClaims"]),
        }
    )

    prompt = build_prompt(skill, lead_text, observation)
    answer = llm_client(prompt)
    trace.append(
        {
            "step": "Answer",
            "format": "markdown",
            "outputPreview": answer[:500],
        }
    )

    return {
        "skill": {
            "name": skill["name"],
            "version": skill["version"],
            "description": skill["description"],
        },
        "answer": answer,
        "trace": trace,
        "context": {
            "leadText": lead_text,
            "interestedProduct": interested_product,
            "promptPreview": prompt[:1200],
        },
        "toolObservation": observation,
    }
