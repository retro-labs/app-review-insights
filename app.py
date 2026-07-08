# 完整启用后端爬虫、数据处理逻辑
from backend.get_reviews import crawl_reviews
from backend.clean_reviews import clean_data
from backend.classify_reviews import classify_comment
from backend.generate_prd import build_prd
from backend.generate_testcases import create_test_case
import streamlit as st
import pandas as pd
import os

# 页面基础配置
st.set_page_config(page_title="App Store评论分析工具", layout="wide")
st.title("LaienTech iOS 应用评测分析工具")

# 1. 输入框
app_url = st.text_input("输入美国App Store应用链接", value="https://apps.apple.com/us/app/workout-for-women-home-gym/id=839285684")
start_btn = st.button("开始全流程分析")

# 2. 进度条容器
progress_bar = st.progress(0)
status_text = st.empty()

# 3. 分板块展示结果标签页
tab1, tab2, tab3, tab4, tab5 = st.tabs(["原始评论", "清洗数据", "分类痛点", "PRD文档", "测试用例"])

if start_btn and app_url:
    # 阶段1：抓取评论
    status_text.text("步骤1/5：正在抓取美区App评论数据")
    raw_path = "sample_data/raw_reviews.json"
    crawl_reviews(app_url, save_path=raw_path)
    progress_bar.progress(20)

    # 阶段2：清洗数据
    status_text.text("步骤2/5：清洗、结构化评论数据")
    clean_path = "sample_data/clean_reviews.csv"
    clean_data(raw_path, clean_path)
    progress_bar.progress(40)

    # 阶段3：痛点分类
    status_text.text("步骤3/5：评论分类、提取用户痛点")
    classify_path = "sample_data/classify_result.csv"
    classify_comment(clean_path, classify_path)
    progress_bar.progress(60)

    # 阶段4：生成PRD文档
    status_text.text("步骤4/5：基于评论痛点生成产品PRD文档")
    prd_path = "sample_data/app_prd.md"
    build_prd(classify_path, prd_path)
    progress_bar.progress(80)

    # 阶段5：生成测试用例
    status_text.text("步骤5/5：根据PRD生成功能测试用例")
    case_path = "sample_data/test_cases.md"
    create_test_case(prd_path, case_path)
    progress_bar.progress(100)
    status_text.success("✅ 全流程分析完成！切换上方标签查看各阶段结果")

    # 标签页展示对应数据与文档
    with tab1:
        st.subheader("原始抓取评论")
        df_raw = pd.read_json(raw_path)
        st.dataframe(df_raw)
    with tab2:
        st.subheader("清洗后评论数据")
        df_clean = pd.read_csv(clean_path, encoding="utf-8-sig")
        st.dataframe(df_clean)
    with tab3:
        st.subheader("用户痛点分类结果")
        df_class = pd.read_csv(classify_path, encoding="utf-8-sig")
        st.dataframe(df_class)
    with tab4:
        st.subheader("自动生成PRD产品文档")
        with open(prd_path, "r", encoding="utf-8") as f:
            st.markdown(f.read())
    with tab5:
        st.subheader("自动生成功能测试用例")
        with open(case_path, "r", encoding="utf-8") as f:
            st.markdown(f.read())