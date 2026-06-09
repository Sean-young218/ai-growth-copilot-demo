import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _read_text(relative_path):
    return (ROOT / relative_path).read_text(encoding="utf-8")


def _load_products():
    return json.loads(_read_text("data/product_catalog.json"))


def _split_forbidden_claims(text):
    return [
        line[2:].strip()
        for line in text.splitlines()
        if line.startswith("- ") and line[2:].strip()
    ]


def _score_product(product, searchable_text):
    score = 0
    if product["name"] in searchable_text:
        score += 8
    for keyword in product.get("keywords", []):
        if keyword and keyword in searchable_text:
            score += 2
    for industry in product.get("targetIndustries", []):
        if industry and industry in searchable_text:
            score += 1
    return score


def query_product(payload):
    lead_text = payload.get("leadText", "")
    interested_product = payload.get("interestedProduct", "")
    searchable_text = f"{lead_text}\n{interested_product}"

    products = _load_products()
    ranked = sorted(
        ((product, _score_product(product, searchable_text)) for product in products),
        key=lambda item: item[1],
        reverse=True,
    )
    matched = [product for product, score in ranked if score > 0]
    match_strategy = "keyword_match"

    if not matched:
        matched = products[:2]
        match_strategy = "broad_context"

    sales_sop = _read_text("data/sales_sop.md").strip()
    forbidden_claims_text = _read_text("data/forbidden_claims.md")

    return {
        "toolName": "query_product",
        "input": {
            "leadText": lead_text,
            "interestedProduct": interested_product,
        },
        "matchStrategy": match_strategy,
        "matchedProducts": matched[:2],
        "salesSop": sales_sop,
        "forbiddenClaims": _split_forbidden_claims(forbidden_claims_text),
        "sources": [
            "data/product_catalog.json",
            "data/sales_sop.md",
            "data/forbidden_claims.md",
        ],
    }
