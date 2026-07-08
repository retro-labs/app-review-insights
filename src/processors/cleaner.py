import re
import json
import os
from typing import List, Dict
from datetime import datetime

class ReviewCleaner:
    def __init__(self):
        self.min_length = 10

    def clean_text(self, text: str) -> str:
        """清洗文本内容"""
        if not text:
            return ""
        
        text = text.strip()
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'[^\w\s\.\,\!\?\-\'\"]', '', text)
        text = re.sub(r'http[s]?://\S+', '', text)
        text = re.sub(r'www\.\S+', '', text)
        
        return text

    def remove_duplicates(self, reviews: List[Dict]) -> List[Dict]:
        """移除重复评论"""
        seen = set()
        unique_reviews = []
        
        for review in reviews:
            content = review.get("content", "") + review.get("title", "")
            content_hash = hash(content)
            
            if content_hash not in seen:
                seen.add(content_hash)
                unique_reviews.append(review)
        
        return unique_reviews

    def filter_short_reviews(self, reviews: List[Dict]) -> List[Dict]:
        """过滤过短评论"""
        return [
            review for review in reviews 
            if len(review.get("content", "")) >= self.min_length
        ]

    def normalize_version(self, version: str) -> str:
        """标准化版本号"""
        if not version:
            return "unknown"
        
        version = version.strip().lower()
        version = re.sub(r'[^\d\.]', '', version)
        
        if version:
            return version
        return "unknown"

    def clean_reviews(self, reviews: List[Dict]) -> List[Dict]:
        """完整清洗流程"""
        cleaned = []
        
        for review in reviews:
            cleaned_review = review.copy()
            
            cleaned_review["title"] = self.clean_text(review.get("title", ""))
            cleaned_review["content"] = self.clean_text(review.get("content", ""))
            cleaned_review["version"] = self.normalize_version(review.get("version", ""))
            cleaned_review["username"] = self.clean_text(review.get("username", ""))
            
            cleaned.append(cleaned_review)
        
        cleaned = self.remove_duplicates(cleaned)
        cleaned = self.filter_short_reviews(cleaned)
        
        return cleaned

    def save_cleaned(self, reviews: List[Dict], app_id: str, output_dir: str = "data/cleaned") -> str:
        """保存清洗后的数据"""
        os.makedirs(output_dir, exist_ok=True)
        filename = f"{output_dir}/cleaned_reviews_{app_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(reviews, f, ensure_ascii=False, indent=2)
        
        return filename

    def load_cleaned(self, filepath: str) -> List[Dict]:
        """加载清洗后的数据"""
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
