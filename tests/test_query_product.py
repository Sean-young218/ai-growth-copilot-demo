import unittest

from src.tools.query_product import query_product


class QueryProductTest(unittest.TestCase):
    def test_returns_matching_product_assets_and_source_names(self):
        result = query_product(
            {
                "leadText": "制造业客户想了解 AI 客服，已有 FAQ，希望一个月内看到 Demo",
                "interestedProduct": "AI 客服解决方案",
            }
        )

        self.assertEqual(result["toolName"], "query_product")
        self.assertEqual(len(result["matchedProducts"]), 1)
        self.assertEqual(result["matchedProducts"][0]["name"], "AI 客服解决方案")
        self.assertIn("确认客户当前系统", result["salesSop"])
        self.assertTrue(any("不得承诺" in item for item in result["forbiddenClaims"]))
        self.assertEqual(
            sorted(result["sources"]),
            [
                "data/forbidden_claims.md",
                "data/product_catalog.json",
                "data/sales_sop.md",
            ],
        )

    def test_falls_back_to_broad_product_context_when_no_exact_product_matches(self):
        result = query_product(
            {
                "leadText": "客户只说想了解企业软件，没有提供行业、场景或具体产品",
                "interestedProduct": "企业软件",
            }
        )

        self.assertGreater(len(result["matchedProducts"]), 0)
        self.assertEqual(result["matchStrategy"], "broad_context")


if __name__ == "__main__":
    unittest.main()
