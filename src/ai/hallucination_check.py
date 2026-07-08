import json
import os
from typing import List, Dict
from datetime import datetime

class HallucinationChecker:
    def __init__(self):
        self.confidence_threshold = 0.6

    def check_prd(self, prd: Dict, reviews: List[Dict]) -> Dict:
        results = {
            "valid_requirements": [],
            "invalid_requirements": [],
            "warnings": [],
            "overall_confidence": 0.0,
            "check_time": datetime.now().isoformat()
        }
        
        total_requirements = len(prd.get("requirements", []))
        valid_count = 0
        
        for requirement in prd.get("requirements", []):
            review_ids = requirement.get("related_review_ids", [])
            related_reviews = [r for r in reviews if r.get("review_id") in review_ids]
            
            if not review_ids:
                results["invalid_requirements"].append({
                    "requirement_id": requirement.get("id", ""),
                    "title": requirement.get("title", ""),
                    "issue": "缺少关联评论ID",
                    "confidence": 0.0
                })
            elif not related_reviews:
                results["invalid_requirements"].append({
                    "requirement_id": requirement.get("id", ""),
                    "title": requirement.get("title", ""),
                    "issue": "关联评论不存在于数据集",
                    "confidence": 0.0
                })
            else:
                confidence = self._calculate_confidence(requirement, related_reviews)
                if confidence >= self.confidence_threshold:
                    results["valid_requirements"].append({
                        "requirement_id": requirement.get("id", ""),
                        "title": requirement.get("title", ""),
                        "related_reviews": len(related_reviews),
                        "confidence": confidence
                    })
                    valid_count += 1
                else:
                    results["warnings"].append({
                        "requirement_id": requirement.get("id", ""),
                        "title": requirement.get("title", ""),
                        "issue": "关联度较低，建议人工审核",
                        "confidence": confidence
                    })
        
        if total_requirements > 0:
            results["overall_confidence"] = valid_count / total_requirements
        
        return results

    def _calculate_confidence(self, requirement: Dict, reviews: List[Dict]) -> float:
        req_text = requirement.get("title", "") + " " + requirement.get("description", "")
        req_text = req_text.lower()
        
        match_count = 0
        for review in reviews:
            review_text = review.get("content", "") + " " + review.get("title", "")
            review_text = review_text.lower()
            
            keywords = set(req_text.split())
            found_keywords = 0
            for keyword in keywords:
                if len(keyword) > 3 and keyword in review_text:
                    found_keywords += 1
            
            if found_keywords >= max(1, len(keywords) // 3):
                match_count += 1
        
        base_confidence = match_count / len(reviews)
        
        if len(reviews) < 2:
            base_confidence *= 0.7
        
        return min(1.0, base_confidence)

    def check_test_cases(self, test_cases: List[Dict], reviews: List[Dict]) -> Dict:
        results = {
            "valid_test_cases": [],
            "invalid_test_cases": [],
            "warnings": [],
            "overall_confidence": 0.0,
            "check_time": datetime.now().isoformat()
        }
        
        total_tests = len(test_cases)
        valid_count = 0
        
        for test_case in test_cases:
            review_ids = test_case.get("related_review_ids", [])
            related_reviews = [r for r in reviews if r.get("review_id") in review_ids]
            
            if not review_ids:
                results["invalid_test_cases"].append({
                    "test_id": test_case.get("test_id", ""),
                    "title": test_case.get("title", ""),
                    "issue": "缺少关联评论ID"
                })
            elif not related_reviews:
                results["invalid_test_cases"].append({
                    "test_id": test_case.get("test_id", ""),
                    "title": test_case.get("title", ""),
                    "issue": "关联评论不存在于数据集"
                })
            else:
                confidence = self._calculate_test_confidence(test_case, related_reviews)
                if confidence >= self.confidence_threshold:
                    results["valid_test_cases"].append({
                        "test_id": test_case.get("test_id", ""),
                        "title": test_case.get("title", ""),
                        "related_reviews": len(related_reviews),
                        "confidence": confidence
                    })
                    valid_count += 1
                else:
                    results["warnings"].append({
                        "test_id": test_case.get("test_id", ""),
                        "title": test_case.get("title", ""),
                        "issue": "关联度较低，建议人工审核",
                        "confidence": confidence
                    })
        
        if total_tests > 0:
            results["overall_confidence"] = valid_count / total_tests
        
        return results

    def _calculate_test_confidence(self, test_case: Dict, reviews: List[Dict]) -> float:
        test_text = test_case.get("title", "") + " " + test_case.get("description", "") + " " + " ".join(test_case.get("steps", [])) + " " + test_case.get("expected_result", "")
        test_text = test_text.lower()
        
        match_count = 0
        for review in reviews:
            review_text = review.get("content", "") + " " + review.get("title", "")
            review_text = review_text.lower()
            
            keywords = set(test_text.split())
            found_keywords = 0
            for keyword in keywords:
                if len(keyword) > 3 and keyword in review_text:
                    found_keywords += 1
            
            if found_keywords >= max(1, len(keywords) // 4):
                match_count += 1
        
        base_confidence = match_count / len(reviews)
        
        if len(reviews) < 2:
            base_confidence *= 0.6
        
        return min(1.0, base_confidence)

    def generate_report(self, prd_check: Dict, test_check: Dict) -> Dict:
        prd_confidence = prd_check.get("overall_confidence", 0.0)
        test_confidence = test_check.get("overall_confidence", 0.0)
        
        overall_status = "WARNING"
        if prd_confidence >= 0.7 and test_confidence >= 0.7:
            overall_status = "PASS"
        elif prd_confidence >= 0.5 and test_confidence >= 0.5:
            overall_status = "WARNING"
        else:
            overall_status = "FAIL"
        
        return {
            "prd_validation": prd_check,
            "test_case_validation": test_check,
            "summary": {
                "prd_valid_count": len(prd_check.get("valid_requirements", [])),
                "prd_invalid_count": len(prd_check.get("invalid_requirements", [])),
                "prd_warning_count": len(prd_check.get("warnings", [])),
                "prd_confidence": prd_confidence,
                "test_valid_count": len(test_check.get("valid_test_cases", [])),
                "test_invalid_count": len(test_check.get("invalid_test_cases", [])),
                "test_confidence": test_confidence,
                "overall_status": overall_status
            },
            "generated_at": datetime.now().isoformat()
        }

    def save_report(self, report: Dict, app_id: str, output_dir: str = "data/cleaned") -> str:
        os.makedirs(output_dir, exist_ok=True)
        filename = f"{output_dir}/hallucination_report_{app_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        return filename

    def load_report(self, filepath: str) -> Dict:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)