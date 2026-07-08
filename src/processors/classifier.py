import json
import os
from typing import List, Dict, Tuple
from datetime import datetime
from textblob import TextBlob

class ReviewClassifier:
    def __init__(self):
        self.categories = {
            "bug": ["crash", "bug", "error", "fail", "broken", "issue", "problem", 
                    "freeze", "glitch", "won't open", "not working", "stuck"],
            "feature": ["want", "need", "add", "feature", "would like", "please add",
                        "request", "suggest", "improve", "enhance"],
            "performance": ["slow", "lag", "battery", "performance", "loading",
                           "memory", "speed", "delay"],
            "usability": ["confusing", "hard to use", "difficult", "ui", "interface",
                          "navigation", "design", "layout", "menu"],
            "content": ["exercise", "workout", "routine", "plan", "video", "audio",
                        "coach", "program", "content", "guide"],
            "subscription": ["subscription", "price", "cost", "payment", "money",
                            "charge", "free trial", "premium"],
            "other": []
        }
        
        self.category_labels_zh = {
            "bug": "Bug缺陷",
            "feature": "功能建议",
            "performance": "性能问题",
            "usability": "易用性",
            "content": "内容相关",
            "subscription": "订阅付费",
            "other": "其他"
        }
        
        self.sentiment_labels_zh = {
            "positive": "正面",
            "negative": "负面",
            "neutral": "中性"
        }

    def get_sentiment(self, text: str) -> Tuple[float, str]:
        """分析情感"""
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity
        
        if polarity > 0.2:
            return polarity, "positive"
        elif polarity < -0.2:
            return polarity, "negative"
        else:
            return polarity, "neutral"

    def classify_category(self, text: str) -> str:
        """分类评论"""
        text_lower = text.lower()
        
        for category, keywords in self.categories.items():
            if category == "other":
                continue
            for keyword in keywords:
                if keyword in text_lower:
                    return category
        
        return "other"

    def classify_reviews(self, reviews: List[Dict]) -> List[Dict]:
        """对所有评论进行分类和情感分析"""
        classified = []
        
        for review in reviews:
            text = review.get("content", "") + " " + review.get("title", "")
            
            sentiment_score, sentiment_label = self.get_sentiment(text)
            category = self.classify_category(text)
            
            classified_review = review.copy()
            classified_review["sentiment_score"] = sentiment_score
            classified_review["sentiment_label"] = sentiment_label
            classified_review["sentiment_label_zh"] = self.sentiment_labels_zh.get(sentiment_label, sentiment_label)
            classified_review["category"] = category
            classified_review["category_zh"] = self.category_labels_zh.get(category, category)
            
            classified.append(classified_review)
        
        return classified

    def save_classified(self, reviews: List[Dict], app_id: str, output_dir: str = "data/cleaned") -> str:
        """保存分类结果"""
        os.makedirs(output_dir, exist_ok=True)
        filename = f"{output_dir}/classified_reviews_{app_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(reviews, f, ensure_ascii=False, indent=2)
        
        return filename

    def load_classified(self, filepath: str) -> List[Dict]:
        """加载分类结果"""
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
