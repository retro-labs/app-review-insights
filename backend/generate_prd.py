import pandas as pd
import os

def build_prd(classify_file, prd_md_path):
    df = pd.read_csv(classify_file, encoding="utf-8-sig")
    pain_count = df["pain_point_tag"].value_counts()
    md = "# iOS健身App PRD需求文档\n## 用户痛点统计\n| 痛点类型 | 评论数量 |\n|----|----|\n"
    for tag, num in pain_count.items():
        md += f"| {tag} | {num} |\n"
    md += "\n## 优化需求\n1. 修复闪退崩溃bug\n2. 优化页面加载卡顿\n3. 简化付费弹窗提示\n4. 减少广告弹窗频率"
    with open(prd_md_path, "w", encoding="utf-8") as f:
        f.write(md)
    return md