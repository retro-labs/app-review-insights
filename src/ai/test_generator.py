import json
import os
from typing import List, Dict
from datetime import datetime

class TestCaseGenerator:
    def __init__(self):
        self.test_counter = 1

    def generate_test_cases(self, prd: Dict, reviews: List[Dict]) -> List[Dict]:
        """根据PRD生成测试用例"""
        test_cases = []
        
        for requirement in prd.get("requirements", []):
            req_test_cases = self._generate_cases_for_requirement(requirement, reviews)
            test_cases.extend(req_test_cases)
        
        return test_cases

    def _generate_cases_for_requirement(self, requirement: Dict, reviews: List[Dict]) -> List[Dict]:
        """为单个需求生成测试用例"""
        cases = []
        
        related_reviews = self._find_related_reviews(requirement, reviews)
        
        cases.append({
            "test_id": f"TC-{self.test_counter:04d}",
            "requirement_id": requirement.get("id", ""),
            "title": f"验证: {requirement.get('title', '')}",
            "description": self._generate_test_description(requirement),
            "test_type": "functional",
            "priority": self._map_priority(requirement.get("priority", 0)),
            "steps": self._generate_test_steps(requirement),
            "expected_result": self._generate_expected_result(requirement),
            "related_review_ids": requirement.get("related_review_ids", []),
            "related_review_contents": [r.get("content", "") for r in related_reviews]
        })
        self.test_counter += 1
        
        if requirement.get("type") == "bug_fix":
            cases.append({
                "test_id": f"TC-{self.test_counter:04d}",
                "requirement_id": requirement.get("id", ""),
                "title": f"回归测试: {requirement.get('title', '')}",
                "description": f"确保修复后问题不再重现",
                "test_type": "regression",
                "priority": self._map_priority(requirement.get("priority", 0)),
                "steps": self._generate_regression_steps(requirement),
                "expected_result": f"问题不再出现，功能正常运行",
                "related_review_ids": requirement.get("related_review_ids", []),
                "related_review_contents": [r.get("content", "") for r in related_reviews]
            })
            self.test_counter += 1
        
        return cases

    def _find_related_reviews(self, requirement: Dict, reviews: List[Dict]) -> List[Dict]:
        """查找相关评论"""
        related_ids = requirement.get("related_review_ids", [])
        return [r for r in reviews if r.get("review_id") in related_ids]

    def _generate_test_description(self, requirement: Dict) -> str:
        """生成测试描述"""
        req_type = requirement.get("type", "")
        if req_type == "bug_fix":
            return f"验证Bug修复效果：{requirement.get('description', '')[:100]}..."
        elif req_type == "feature":
            return f"验证新功能实现：{requirement.get('description', '')[:100]}..."
        return f"验证需求：{requirement.get('description', '')[:100]}..."

    def _generate_test_steps(self, requirement: Dict) -> List[str]:
        """生成测试步骤"""
        req_type = requirement.get("type", "")
        
        if req_type == "bug_fix":
            return [
                "1. 进入相关功能页面",
                "2. 执行触发问题的操作",
                "3. 观察系统响应",
                "4. 验证问题是否已解决"
            ]
        elif req_type == "feature":
            return [
                "1. 进入新功能页面",
                "2. 验证功能入口是否存在",
                "3. 执行功能操作",
                "4. 验证功能是否正常工作",
                "5. 验证边界情况处理"
            ]
        return [
            "1. 进入相关功能页面",
            "2. 执行测试操作",
            "3. 验证系统响应",
            "4. 验证结果是否符合预期"
        ]

    def _generate_regression_steps(self, requirement: Dict) -> List[str]:
        """生成回归测试步骤"""
        return [
            "1. 重复原始问题的操作步骤",
            "2. 验证问题不再重现",
            "3. 验证相关功能不受影响",
            "4. 在不同环境下验证"
        ]

    def _generate_expected_result(self, requirement: Dict) -> str:
        """生成预期结果"""
        req_type = requirement.get("type", "")
        
        if req_type == "bug_fix":
            return "问题已修复，系统正常运行，无异常报错"
        elif req_type == "feature":
            return "新功能正常工作，界面友好，操作流畅"
        return "功能正常运行，符合需求描述"

    def _map_priority(self, priority: int) -> str:
        """映射优先级"""
        if priority >= 4:
            return "高"
        elif priority == 3:
            return "中"
        else:
            return "低"

    def save_test_cases(self, test_cases: List[Dict], app_id: str, output_dir: str = "data/cleaned") -> str:
        """保存测试用例"""
        os.makedirs(output_dir, exist_ok=True)
        filename = f"{output_dir}/test_cases_{app_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(test_cases, f, ensure_ascii=False, indent=2)
        
        return filename

    def load_test_cases(self, filepath: str) -> List[Dict]:
        """加载测试用例"""
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
