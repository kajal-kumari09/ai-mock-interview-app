from django.test import Client, TestCase
from django.urls import reverse

from .services import ALLOWED_TOPICS, generate_questions, is_correct_answer


class QuizViewTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_home_page_loads(self):
        response = self.client.get(reverse("quiz:home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Voice Quiz Arena")

    def test_quiz_generation_returns_questions(self):
        response = self.client.post(
            reverse("quiz:quiz_session"),
            data='{"topic":"java","difficulty":"easy","count":5}',
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data["questions"]), 5)
        self.assertEqual(data["topic"], "java")
        self.assertEqual(len({item["question"] for item in data["questions"]}), 5)

    def test_invalid_topic_falls_back_to_python(self):
        response = self.client.post(
            reverse("quiz:quiz_session"),
            data='{"topic":"science","difficulty":"easy","count":5}',
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["topic"], "python")
        self.assertTrue(all(data["topic"] in ALLOWED_TOPICS for _ in data["questions"]))

    def test_answer_checking_accepts_loose_match(self):
        self.assertTrue(is_correct_answer("George Washington", "It was George Washington"))
        self.assertFalse(is_correct_answer("Mars", "Venus"))

    def test_review_scores_correctness_and_speed(self):
        response = self.client.post(
            reverse("quiz:quiz_session"),
            data='{"answers":[{"question":"Q1","correct_answer":"def","user_answer":"def","response_time_seconds":4.2},{"question":"Q2","correct_answer":"class","user_answer":"wrong","response_time_seconds":13.5}]}',
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["score"], 3)
        self.assertEqual(data["max_score"], 6)
        self.assertAlmostEqual(data["average_response_time"], 8.85, places=2)
        self.assertEqual(data["results"][0]["time_score"], 2)
        self.assertEqual(data["results"][0]["question_score"], 3)
        self.assertEqual(data["results"][1]["time_score"], 0)

    def test_easy_and_hard_fallback_questions_are_different(self):
        easy_questions, source_easy = generate_questions("python", "easy", 3)
        hard_questions, source_hard = generate_questions("python", "hard", 3)
        self.assertEqual(source_easy, "fallback")
        self.assertEqual(source_hard, "fallback")
        self.assertNotEqual(
            {item["question"] for item in easy_questions},
            {item["question"] for item in hard_questions},
        )
