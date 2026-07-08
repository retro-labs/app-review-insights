import os

def create_test_case(prd_file, case_md_path):
    case_text = "# App功能测试用例\n## 稳定性测试\n1. 连续使用30分钟，验证无闪退\n## 性能测试\n1. 打开课程页面，加载耗时≤2秒\n## 付费&广告测试\n1. 验证订阅支付流程正常\n2. 关闭广告开关后不再弹出广告"
    with open(case_md_path, "w", encoding="utf-8") as f:
        f.write(case_text)
    return case_text