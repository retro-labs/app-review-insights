import pytest
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.collectors.appstore import AppStoreReviewCollector
from src.processors.cleaner import ReviewCleaner
from src.processors.classifier import ReviewClassifier
from src.processors.analyzer import ReviewAnalyzer
from src.ai.prd_generator import PRDGenerator
from src.ai.test_generator import TestCaseGenerator
from src.ai.hallucination_check import HallucinationChecker

class TestAppStoreReviewCollector:
    def test_extract_app_id(self):
        collector = AppStoreReviewCollector()
        url = "https://apps.apple.com/us/app/workout-for-women-home-gym/id839285684"
        app_id = collector.extract_app_id(url)
        assert app_id == "839285684"
    
    def test_parse_entry(self):
        collector = AppStoreReviewCollector()
        entry = {
            "id": {"label": "12345"},
            "title": {"label": "Great app"},
            "content": {"label": "I love this app!"},
            "im:rating": {"label": "5"},
            "im:version": {"label": "1.0"},
            "author": {"name": {"label": "user123"}},
            "updated": {"label": "2024-01-01T00:00:00Z"}
        }
        review = collector._parse_entry(entry)
        assert review is not None
        assert review["review_id"] == "12345"
        assert review["rating"] == 5

class TestReviewCleaner:
    def test_clean_text(self):
        cleaner = ReviewCleaner()
        text = "  This is a test!  \n\nWith multiple lines.  "
        cleaned = cleaner.clean_text(text)
        assert cleaned == "This is a test! With multiple lines."
    
    def test_remove_duplicates(self):
        cleaner = ReviewCleaner()
        reviews = [
            {"content": "Same content", "title": "Same"},
            {"content": "Same content", "title": "Same"},
            {"content": "Different", "title": "Diff"}
        ]
        cleaned = cleaner.remove_duplicates(reviews)
        assert len(cleaned) == 2

class TestReviewClassifier:
    def test_get_sentiment(self):
        classifier = ReviewClassifier()
        score, label = classifier.get_sentiment("I love this app!")
        assert label == "positive"
        assert score > 0
    
    def test_classify_category(self):
        classifier = ReviewClassifier()
        category = classifier.classify_category("This app crashes all the time!")
        assert category == "bug"

class TestReviewAnalyzer:
    def test_analyze_distribution(self):
        analyzer = ReviewAnalyzer()
        reviews = [
            {"category": "bug", "sentiment_label": "negative", "rating": 1},
            {"category": "feature", "sentiment_label": "positive", "rating": 5},
            {"category": "bug", "sentiment_label": "negative", "rating": 2}
        ]
        distribution = analyzer.analyze_distribution(reviews)
        assert distribution["total_reviews"] == 3
        assert distribution["category_distribution"]["bug"] == 2

class TestPRDGenerator:
    def test_generate_prd(self):
        generator = PRDGenerator()
        analysis_summary = {
            "key_issues": [
                {"review_id": "1", "content": "App crashes", "rating": 1, "sentiment_score": -0.8}
            ],
            "feature_requests": [
                {"review_id": "2", "content": "Add dark mode", "rating": 4, "sentiment_score": 0.5}
            ],
            "distribution": {"total_reviews": 2}
        }
        reviews = [
            {"review_id": "1", "content": "App crashes"},
            {"review_id": "2", "content": "Add dark mode"}
        ]
        prd = generator.generate_prd(analysis_summary, reviews)
        assert prd["product_name"] == "Workout for Women: Home Gym"
        assert len(prd["requirements"]) >= 2

class TestTestCaseGenerator:
    def test_generate_test_cases(self):
        generator = TestCaseGenerator()
        prd = {
            "requirements": [
                {
                    "id": "REQ-001",
                    "title": "Fix crash",
                    "description": "App crashes",
                    "type": "bug_fix",
                    "priority": 5,
                    "related_review_ids": ["1"]
                }
            ]
        }
        reviews = [{"review_id": "1", "content": "App crashes"}]
        test_cases = generator.generate_test_cases(prd, reviews)
        assert len(test_cases) >= 1

class TestHallucinationChecker:
    def test_check_prd(self):
        checker = HallucinationChecker()
        prd = {
            "requirements": [
                {
                    "id": "REQ-001",
                    "title": "Fix crash",
                    "related_review_ids": ["1"]
                }
            ]
        }
        reviews = [{"review_id": "1", "content": "App crashes"}]
        result = checker.check_prd(prd, reviews)
        assert result["overall_confidence"] == 1.0

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
