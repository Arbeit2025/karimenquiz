# -*- coding: utf-8 -*-
"""karimenquiz の単体テスト（問題データの検証とルート確認）。"""
import sys
import unittest
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import app as karimen


class TestQuestionData(unittest.TestCase):
    def test_exactly_100_questions(self):
        self.assertEqual(len(karimen.QUESTIONS), 100)

    def test_all_fields_non_empty(self):
        for q in karimen.QUESTIONS:
            self.assertIsInstance(q["q"], str)
            self.assertTrue(q["q"].strip())
            self.assertIsInstance(q["answer"], bool)
            self.assertIsInstance(q["explanation"], str)
            self.assertTrue(q["explanation"].strip())
            self.assertIsInstance(q["category"], str)
            self.assertTrue(q["category"].strip())

    def test_no_duplicate_questions(self):
        texts = [q["q"] for q in karimen.QUESTIONS]
        self.assertEqual(len(texts), len(set(texts)))

    def test_answer_balance(self):
        true_count = sum(1 for q in karimen.QUESTIONS if q["answer"])
        ratio = true_count / len(karimen.QUESTIONS)
        self.assertGreaterEqual(ratio, 0.40)
        self.assertLessEqual(ratio, 0.60)

    def test_each_category_exactly_25(self):
        counts = Counter(q["category"] for q in karimen.QUESTIONS)
        self.assertEqual(
            set(counts), {"交通ルールの基礎", "標識・標示", "運転の基本", "歩行者と安全"})
        for cat, n in counts.items():
            self.assertEqual(n, 25, cat)


class TestRoutes(unittest.TestCase):
    def setUp(self):
        self.client = karimen.app.test_client()

    def test_index_ok(self):
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)
        body = res.get_data(as_text=True)
        self.assertIn("仮免対策 ○×カード", body)
        self.assertIn("学習用の自作問題です", body)

    def test_healthz(self):
        res = self.client.get("/healthz")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.get_json(), {"status": "ok"})

    def test_api_questions(self):
        res = self.client.get("/api/questions")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 100)


if __name__ == "__main__":
    unittest.main()
