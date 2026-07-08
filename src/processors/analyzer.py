import json
import os
from typing import List, Dict
from datetime import datetime
from collections import Counter

class ReviewAnalyzer:
    def __init__(self):
        self.category_names = {
            "bug": "Bug报告",
            "feature": "功能需求",
            "performance": "性能问题",
            "usability": "易用性",
            "content": "内容相关",
            "subscription": "订阅付费",
            "other": "其他"
        }

    def analyze_distribution(self, reviews: List[Dict]) -> Dict:
        """分析评论分布"""
        categories = [r.get("category", "other") for r in reviews]
        sentiments = [r.get("sentiment_label", "neutral") for r in reviews]
        ratings = [r.get("rating", 0) for r in reviews]
        
        return {
            "category_distribution": dict(Counter(categories)),
            "sentiment_distribution": dict(Counter(sentiments)),
            "rating_distribution": dict(Counter(ratings)),
            "total_reviews": len(reviews)
        }

    def extract_key_issues(self, reviews: List[Dict], top_n: int = 10) -> List[Dict]:
        """提取关键问题"""
        issues = []
        
        for review in reviews:
            if review.get("sentiment_label") == "negative" or review.get("rating") <= 2:
                issues.append({
                    "review_id": review.get("review_id", ""),
                    "content": review.get("content", ""),
                    "content_zh": review.get("content_zh", ""),
                    "rating": review.get("rating", 0),
                    "category": review.get("category", "other"),
                    "category_zh": review.get("category_zh", ""),
                    "sentiment_score": review.get("sentiment_score", 0),
                    "date": review.get("date", "")
                })
        
        issues.sort(key=lambda x: x["sentiment_score"])
        
        return issues[:top_n]

    def extract_feature_requests(self, reviews: List[Dict], top_n: int = 10) -> List[Dict]:
        """提取功能需求"""
        requests = []
        
        for review in reviews:
            if review.get("category") == "feature":
                requests.append({
                    "review_id": review.get("review_id", ""),
                    "content": review.get("content", ""),
                    "content_zh": review.get("content_zh", ""),
                    "rating": review.get("rating", 0),
                    "date": review.get("date", "")
                })
        
        return requests[:top_n]

    def analyze_trends(self, reviews: List[Dict]) -> Dict:
        """分析趋势"""
        monthly_data = {}
        
        for review in reviews:
            date_str = review.get("date", "")
            if date_str:
                month = date_str[:7]
                if month not in monthly_data:
                    monthly_data[month] = {"count": 0, "avg_rating": 0, "total_rating": 0}
                
                monthly_data[month]["count"] += 1
                monthly_data[month]["total_rating"] += review.get("rating", 0)
        
        for month in monthly_data:
            if monthly_data[month]["count"] > 0:
                monthly_data[month]["avg_rating"] = monthly_data[month]["total_rating"] / monthly_data[month]["count"]
        
        return dict(sorted(monthly_data.items()))

    def generate_summary(self, reviews: List[Dict]) -> Dict:
        """生成分析摘要"""
        distribution = self.analyze_distribution(reviews)
        key_issues = self.extract_key_issues(reviews)
        feature_requests = self.extract_feature_requests(reviews)
        trends = self.analyze_trends(reviews)
        
        return {
            "distribution": distribution,
            "key_issues": key_issues,
            "feature_requests": feature_requests,
            "trends": trends,
            "analysis_time": datetime.now().isoformat()
        }

    def save_summary(self, summary: Dict, app_id: str, output_dir: str = "data/cleaned") -> str:
        """保存分析摘要"""
        os.makedirs(output_dir, exist_ok=True)
        filename = f"{output_dir}/analysis_summary_{app_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        
        return filename

    def load_summary(self, filepath: str) -> Dict:
        """加载分析摘要"""
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
