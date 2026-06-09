import unittest

from src.agent.runner import run_lead_scoring_agent


class RunnerTest(unittest.TestCase):
    def test_produces_react_trace_and_final_answer_with_injected_llm(self):
        captured = {}

        def fake_llm(prompt):
            captured["prompt"] = prompt
            return "## 线索评分\n82/100\n\n## 是否需要人工复核\n需要，交付周期和预算需确认。"

        result = run_lead_scoring_agent(
            {
                "leadText": "来源：官网表单\n行业：制造业\n感兴趣产品：AI 客服解决方案\n客户希望降低售后咨询压力，一个月内看到 Demo，但没有预算信息。",
                "llmClient": fake_llm,
            }
        )

        self.assertIn("不得编造价格、交付周期、客户案例或产品能力", captured["prompt"])
        self.assertEqual(result["skill"]["name"], "lead-scoring-followup")
        self.assertEqual(result["trace"][0]["step"], "Skill")
        self.assertEqual(result["trace"][1]["step"], "Reasoning Summary")
        self.assertEqual(result["trace"][2]["step"], "Act")
        self.assertEqual(result["trace"][2]["tool"], "query_product")
        self.assertEqual(result["trace"][3]["step"], "Observe")
        self.assertEqual(result["trace"][-1]["step"], "Answer")
        self.assertIn("线索评分", result["answer"])


if __name__ == "__main__":
    unittest.main()
