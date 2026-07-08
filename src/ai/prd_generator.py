import json
import os
from typing import List, Dict
from datetime import datetime

class PRDGenerator:
    def __init__(self):
        self.version_counter = 1

    def generate_prd(self, analysis_summary: Dict, reviews: List[Dict]) -> Dict:
        """生成PRD文档"""
        key_issues = analysis_summary.get("key_issues", [])
        feature_requests = analysis_summary.get("feature_requests", [])
        distribution = analysis_summary.get("distribution", {})
        
        requirements = []
        
        for issue in key_issues:
            requirements.append({
                "id": f"REQ-{self.version_counter:03d}",
                "title": self._extract_requirement_title(issue),
                "description": issue.get("content", ""),
                "type": "bug_fix",
                "priority": self._calculate_priority(issue),
                "related_review_ids": [issue.get("review_id", "")],
                "impact": self._estimate_impact(issue),
                "effort": self._estimate_effort(issue)
            })
        
        for request in feature_requests:
            requirements.append({
                "id": f"REQ-{self.version_counter:03d}",
                "title": self._extract_feature_title(request),
                "description": request.get("content", ""),
                "type": "feature",
                "priority": self._calculate_priority(request),
                "related_review_ids": [request.get("review_id", "")],
                "impact": self._estimate_impact(request),
                "effort": self._estimate_effort(request)
            })
        
        requirements.sort(key=lambda x: x["priority"], reverse=True)
        
        version_plans = self._split_into_versions(requirements)
        
        prd = {
            "product_name": "Workout for Women: Home Gym",
            "app_id": "839285684",
            "prd_version": "1.0",
            "created_date": datetime.now().isoformat(),
            "analysis_summary": {
                "total_reviews": distribution.get("total_reviews", 0),
                "sentiment_distribution": distribution.get("sentiment_distribution", {}),
                "category_distribution": distribution.get("category_distribution", {})
            },
            "requirements": requirements,
            "version_plans": version_plans
        }
        
        return prd

    def _extract_requirement_title(self, issue: Dict) -> str:
        """提取需求标题"""
        content = issue.get("content", "")[:50]
        return f"修复问题: {content}..." if len(content) >= 50 else f"修复问题: {content}"

    def _extract_feature_title(self, request: Dict) -> str:
        """提取功能标题"""
        content = request.get("content", "")[:50]
        return f"新增功能: {content}..." if len(content) >= 50 else f"新增功能: {content}"

    def _calculate_priority(self, item: Dict) -> int:
        """计算优先级"""
        rating = item.get("rating", 0)
        sentiment = item.get("sentiment_score", 0)
        
        if rating <= 1:
            return 5
        elif rating <= 2:
            return 4
        elif sentiment < -0.5:
            return 3
        else:
            return 2

    def _estimate_impact(self, item: Dict) -> str:
        """估计影响范围"""
        rating = item.get("rating", 0)
        
        if rating <= 1:
            return "高"
        elif rating <= 2:
            return "中"
        else:
            return "低"

    def _estimate_effort(self, item: Dict) -> str:
        """估计工作量"""
        content = item.get("content", "")
        
        if len(content) < 50:
            return "低"
        elif len(content) < 150:
            return "中"
        else:
            return "高"

    def _split_into_versions(self, requirements: List[Dict]) -> List[Dict]:
        """拆分为多版本计划"""
        versions = []
        current_version = {"version": "v1.0", "requirements": [], "focus": "紧急Bug修复"}
        
        for req in requirements:
            if req["type"] == "bug_fix" and req["priority"] >= 4:
                current_version["requirements"].append(req)
        
        if current_version["requirements"]:
            versions.append(current_version)
        
        version2 = {"version": "v1.1", "requirements": [], "focus": "重要功能优化"}
        for req in requirements:
            if req["type"] == "feature" and req["priority"] >= 3:
                version2["requirements"].append(req)
        
        if version2["requirements"]:
            versions.append(version2)
        
        version3 = {"version": "v1.2", "requirements": [], "focus": "体验提升与次要功能"}
        for req in requirements:
            if req not in current_version["requirements"] and req not in version2["requirements"]:
                version3["requirements"].append(req)
        
        if version3["requirements"]:
            versions.append(version3)
        
        return versions

    def save_prd(self, prd: Dict, app_id: str, output_dir: str = "data/cleaned") -> str:
        """保存PRD"""
        os.makedirs(output_dir, exist_ok=True)
        filename = f"{output_dir}/prd_{app_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(prd, f, ensure_ascii=False, indent=2)
        
        return filename

    def load_prd(self, filepath: str) -> Dict:
        """加载PRD"""
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
