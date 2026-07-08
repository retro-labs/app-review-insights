import streamlit as st
import json
import os
import time
import pandas as pd
import plotly.express as px
from datetime import datetime

from src.collectors.appstore import AppStoreReviewCollector
from src.processors.cleaner import ReviewCleaner
from src.processors.classifier import ReviewClassifier
from src.processors.analyzer import ReviewAnalyzer
from src.processors.translator import ReviewTranslator
from src.ai.prd_generator import PRDGenerator
from src.ai.test_generator import TestCaseGenerator
from src.ai.hallucination_check import HallucinationChecker
from src.database.connection import init_db

APP_STORE_URL = "https://apps.apple.com/us/app/workout-for-women-home-gym/id839285684"

STAGES = [
    {"id": "collect", "name": "采集", "icon": "📥"},
    {"id": "clean", "name": "清洗", "icon": "🧹"},
    {"id": "classify", "name": "分类", "icon": "🏷️"},
    {"id": "analyze", "name": "挖掘", "icon": "🔍"},
    {"id": "prd", "name": "PRD", "icon": "📝"},
    {"id": "test", "name": "测试", "icon": "🧪"},
    {"id": "verify", "name": "校验", "icon": "✅"},
    {"id": "done", "name": "完成", "icon": "🎉"}
]

def hide_streamlit_style():
    hide_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display: none;}
    section[data-testid="stSidebar"] {display: none !important;}
    .st-emotion-cache-16txtl3 {padding: 0;}
    </style>
    """
    st.markdown(hide_style, unsafe_allow_html=True)

def apply_custom_style():
    custom_style = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }
    
    body {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        background: #f8fafc;
        min-height: 100vh;
    }
    
    .header-container {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        color: white;
        padding: 24px 50px;
        box-shadow: 0 4px 24px rgba(99, 102, 241, 0.3);
    }
    
    .header-title {
        font-size: 28px;
        font-weight: 700;
    }
    
    .header-subtitle {
        font-size: 14px;
        opacity: 0.9;
        margin-top: 4px;
    }
    
    .main-container {
        padding: 24px 50px;
        max-width: 1500px;
        margin: 0 auto;
    }
    
    .control-card {
        background: white;
        border-radius: 16px;
        padding: 20px 24px;
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
        margin-bottom: 16px;
    }
    
    .card-title {
        font-size: 15px;
        font-weight: 600;
        color: #1e293b;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    .btn-primary {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 12px 28px;
        font-size: 14px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 4px 14px rgba(99, 102, 241, 0.35);
    }
    
    .btn-primary:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(99, 102, 241, 0.45);
    }
    
    .btn-secondary {
        background: #f1f5f9;
        color: #64748b;
        border: none;
        border-radius: 10px;
        padding: 12px 28px;
        font-size: 14px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .btn-secondary:hover {
        background: #e2e8f0;
    }
    
    .progress-section {
        background: white;
        border-radius: 16px;
        padding: 20px 24px;
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
        margin-bottom: 16px;
    }
    
    .progress-bar {
        height: 8px;
        background: #e2e8f0;
        border-radius: 4px;
        overflow: hidden;
        margin: 12px 0;
    }
    
    .progress-fill {
        height: 100%;
        background: linear-gradient(90deg, #6366f1 0%, #8b5cf6 100%);
        border-radius: 4px;
        transition: width 0.5s ease-out;
        animation: shimmer 2s infinite;
        background-size: 200% 100%;
    }
    
    @keyframes shimmer {
        0% { background-position: -200% 0; }
        100% { background-position: 200% 0; }
    }
    
    .progress-steps {
        display: flex;
        justify-content: center;
        align-items: center;
        margin-top: 10px;
        gap: 6px;
    }
    
    .step-item {
        display: flex;
        align-items: center;
        gap: 4px;
        padding: 4px 10px;
        border-radius: 8px;
        transition: all 0.3s ease;
    }
    
    .step-item:hover {
        background: rgba(99, 102, 241, 0.06);
    }
    
    .step-dot {
        width: 22px;
        height: 22px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 10px;
        font-weight: 600;
        transition: all 0.3s ease;
        border: 2px solid;
    }
    
    .step-dot.completed {
        background: #10b981;
        border-color: #10b981;
        color: white;
    }
    
    .step-dot.current {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        border-color: #6366f1;
        color: white;
        transform: scale(1.15);
        box-shadow: 0 0 15px rgba(99, 102, 241, 0.5);
        animation: pulse 1.5s infinite;
    }
    
    @keyframes pulse {
        0%, 100% { box-shadow: 0 0 15px rgba(99, 102, 241, 0.5); }
        50% { box-shadow: 0 0 25px rgba(99, 102, 241, 0.8); }
    }
    
    .step-dot.pending {
        background: #f1f5f9;
        border-color: #cbd5e1;
        color: #94a3b8;
    }
    
    .step-label {
        font-size: 13px;
        color: #64748b;
        white-space: nowrap;
        font-weight: 500;
    }
    
    .step-item.completed .step-label { color: #10b981; }
    .step-item.current .step-label { color: #6366f1; font-weight: 600; }
    
    .metric-card {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        color: white;
        border-radius: 12px;
        padding: 16px;
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(99, 102, 241, 0.4);
    }
    
    .metric-value {
        font-size: 28px;
        font-weight: 700;
        margin-bottom: 2px;
    }
    
    .metric-label {
        font-size: 13px;
        opacity: 0.9;
    }
    
    .lang-card {
        padding: 14px;
        border-radius: 10px;
        background: #f8fafc;
        font-size: 13px;
    }
    
    .lang-title {
        font-size: 13px;
        font-weight: 600;
        margin-bottom: 6px;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    
    .lang-en { color: #6366f1; }
    .lang-zh { color: #10b981; }
    
    .chart-container {
        background: white;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
    }
    
    .tag-badge {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 16px;
        font-size: 12px;
        font-weight: 500;
        margin-right: 6px;
    }
    
    .tag-bug { background: #fee2e2; color: #dc2626; }
    .tag-feature { background: #dbeafe; color: #2563eb; }
    .tag-performance { background: #ffedd5; color: #ea580c; }
    .tag-usability { background: #e0e7ff; color: #6366f1; }
    .tag-content { background: #dcfce7; color: #16a34a; }
    .tag-subscription { background: #fce7f3; color: #db2777; }
    .tag-positive { background: #dcfce7; color: #16a34a; }
    .tag-negative { background: #fee2e2; color: #dc2626; }
    .tag-neutral { background: #fef9c3; color: #ca8a04; }
    
    .info-card {
        background: #f8fafc;
        border-left: 4px solid #6366f1;
        border-radius: 0 10px 10px 0;
        padding: 14px 18px;
        margin-bottom: 12px;
        font-size: 13px;
    }
    
    .success-card {
        background: #ecfdf5;
        border-left: 4px solid #10b981;
        border-radius: 0 10px 10px 0;
        padding: 14px 18px;
        margin-bottom: 12px;
        font-size: 13px;
    }
    
    .error-card {
        background: #fef2f2;
        border-left: 4px solid #ef4444;
        border-radius: 0 10px 10px 0;
        padding: 14px 18px;
        margin-bottom: 12px;
        font-size: 13px;
    }
    
    .expander-content {
        font-size: 13px;
        line-height: 1.6;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        padding: 0;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: #f1f5f9;
        border-radius: 10px 10px 0 0;
        padding: 10px 20px;
        font-size: 14px;
        font-weight: 500;
        color: #64748b;
        transition: all 0.3s ease;
        border: none;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: #e2e8f0;
        color: #475569;
    }
    
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background: white;
        color: #6366f1;
        font-weight: 600;
        box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.05);
    }
    
    .stDataFrame {
        font-size: 13px;
    }
    
    .st-expander {
        border-radius: 10px;
        border: 1px solid #e2e8f0;
        margin-bottom: 8px;
    }
    
    .st-expanderHeader {
        font-size: 14px;
        font-weight: 600;
        color: #334155;
    }
    
    .stTextInput input {
        font-size: 14px;
        padding: 12px 16px;
        border-radius: 10px;
        border: 2px solid #e2e8f0;
    }
    
    .stTextInput input:focus {
        border-color: #6366f1;
        box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
    }
    </style>
    """
    st.markdown(custom_style, unsafe_allow_html=True)

def main():
    st.set_page_config(
        page_title="App评论分析与版本规划",
        page_icon="📊",
        layout="wide"
    )
    
    init_db()
    hide_streamlit_style()
    apply_custom_style()
    
    if "stage" not in st.session_state:
        st.session_state.stage = 0
    if "progress" not in st.session_state:
        st.session_state.progress = 0
    if "data" not in st.session_state:
        st.session_state.data = {}
    
    render_header()
    render_main_content()

def render_header():
    st.markdown("""
    <div class="header-container">
        <div class="header-title">📊 App评论分析与版本规划</div>
        <div class="header-subtitle">LaienTech iOS App评论分析与版本规划评估</div>
    </div>
    """, unsafe_allow_html=True)

def render_main_content():
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    
    render_control_card()
    render_progress_section()
    
    tab_raw, tab_clean, tab_classify, tab_analyze, tab_prd, tab_test, tab_verify = st.tabs(
        ["📥 原始数据", "🧹 清洗结果", "🏷️ 分类分析", "🔍 问题挖掘", "📝 PRD文档", "🧪 测试用例", "✅ 校验报告"]
    )
    
    with tab_raw:
        display_raw_data()
    
    with tab_clean:
        display_cleaned_data()
    
    with tab_classify:
        display_classification()
    
    with tab_analyze:
        display_analysis()
    
    with tab_prd:
        display_prd()
    
    with tab_test:
        display_test_cases()
    
    with tab_verify:
        display_verification()
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_control_card():
    st.markdown('<div class="control-card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">🔧 输入设置</div>', unsafe_allow_html=True)
    
    col_input, col_buttons = st.columns([5, 2])
    
    with col_input:
        app_url = st.text_input(
            "App Store链接",
            value=APP_STORE_URL,
            help="输入美区App Store应用链接",
            key="app_url",
            label_visibility="collapsed",
            placeholder="请输入美区App Store应用链接..."
        )
    
    with col_buttons:
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            start_button = st.button("🚀 开始分析", key="start", width="stretch")
        with col_btn2:
            reset_button = st.button("🔄 重置", key="reset", width="stretch")
    
    if reset_button:
        st.session_state.stage = 0
        st.session_state.progress = 0
        st.session_state.data = {}
        st.rerun()
    
    if start_button:
        run_workflow(app_url)
    
    st.markdown('</div>', unsafe_allow_html=True)

def render_progress_section():
    st.markdown('<div class="progress-section">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">📈 工作流进度</div>', unsafe_allow_html=True)
    
    st.markdown(f'<div style="font-size: 14px; color: #6366f1; font-weight: 600; text-align: right;">{st.session_state.progress}%</div>', unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="progress-bar">
        <div class="progress-fill" style="width: {st.session_state.progress}%"></div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="progress-steps">', unsafe_allow_html=True)
    
    for i, stage in enumerate(STAGES):
        status = "pending"
        if i < st.session_state.stage:
            status = "completed"
        elif i == st.session_state.stage:
            status = "current"
        
        st.markdown(f"""
        <div class="step-item {status}">
            <div class="step-dot {status}">{stage['icon']}</div>
            <div class="step-label">{stage['name']}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

def run_workflow(app_url):
    with st.spinner("正在执行分析工作流..."):
        collector = AppStoreReviewCollector()
        cleaner = ReviewCleaner()
        translator = ReviewTranslator()
        classifier = ReviewClassifier()
        analyzer = ReviewAnalyzer()
        prd_generator = PRDGenerator()
        test_generator = TestCaseGenerator()
        hallucination_checker = HallucinationChecker()
        
        st.session_state.stage = 0
        st.session_state.progress = 0
        
        st.markdown('<div class="info-card"><strong>📥 阶段1：采集数据</strong></div>', unsafe_allow_html=True)
        update_progress(0, 10)
        try:
            collection_result = collector.collect(app_url)
            st.session_state.data["collection_result"] = collection_result
            
            if collection_result["success"]:
                raw_reviews = collector.load_reviews(collection_result["file_path"])
                st.session_state.data["raw_reviews"] = raw_reviews
                st.markdown(f'<div class="success-card"><strong>✅ 成功采集 {len(raw_reviews)} 条评论</strong></div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="error-card"><strong>❌ 采集失败:</strong> {collection_result["error"]}</div>', unsafe_allow_html=True)
                return
        except Exception as e:
            st.markdown(f'<div class="error-card"><strong>❌ 采集数据时出错:</strong> {e}</div>', unsafe_allow_html=True)
            return
        
        st.session_state.stage = 1
        update_progress(10, 22)
        
        st.markdown('<div class="info-card"><strong>🧹 阶段2：清洗数据</strong></div>', unsafe_allow_html=True)
        try:
            cleaned_reviews = cleaner.clean_reviews(st.session_state.data["raw_reviews"])
            st.session_state.data["cleaned_reviews"] = cleaned_reviews
            st.markdown(f'<div class="success-card"><strong>✅ 清洗完成，保留 {len(cleaned_reviews)} 条有效评论</strong></div>', unsafe_allow_html=True)
        except Exception as e:
            st.markdown(f'<div class="error-card"><strong>❌ 清洗数据时出错:</strong> {e}</div>', unsafe_allow_html=True)
            return
        
        st.markdown('<div class="info-card"><strong>🌐 阶段2.5：翻译评论</strong></div>', unsafe_allow_html=True)
        try:
            translated_reviews = translator.translate_reviews(cleaned_reviews)
            st.session_state.data["translated_reviews"] = translated_reviews
            st.markdown('<div class="success-card"><strong>✅ 翻译完成，已添加中文对照</strong></div>', unsafe_allow_html=True)
        except Exception as e:
            st.markdown(f'<div class="info-card"><strong>⚠️ 翻译失败，继续使用原始数据:</strong> {e}</div>', unsafe_allow_html=True)
            st.session_state.data["translated_reviews"] = cleaned_reviews
        
        st.session_state.stage = 2
        update_progress(22, 35)
        
        st.markdown('<div class="info-card"><strong>🏷️ 阶段3：分类分析</strong></div>', unsafe_allow_html=True)
        try:
            classified_reviews = classifier.classify_reviews(translated_reviews)
            st.session_state.data["classified_reviews"] = classified_reviews
            st.markdown('<div class="success-card"><strong>✅ 评论分类和情感分析完成</strong></div>', unsafe_allow_html=True)
        except Exception as e:
            st.markdown(f'<div class="error-card"><strong>❌ 分类分析时出错:</strong> {e}</div>', unsafe_allow_html=True)
            return
        
        st.session_state.stage = 3
        update_progress(35, 48)
        
        st.markdown('<div class="info-card"><strong>🔍 阶段4：问题挖掘</strong></div>', unsafe_allow_html=True)
        try:
            analysis_summary = analyzer.generate_summary(classified_reviews)
            st.session_state.data["analysis_summary"] = analysis_summary
            st.markdown('<div class="success-card"><strong>✅ 分析摘要生成完成</strong></div>', unsafe_allow_html=True)
        except Exception as e:
            st.markdown(f'<div class="error-card"><strong>❌ 问题挖掘时出错:</strong> {e}</div>', unsafe_allow_html=True)
            return
        
        st.session_state.stage = 4
        update_progress(48, 62)
        
        st.markdown('<div class="info-card"><strong>📝 阶段5：生成PRD</strong></div>', unsafe_allow_html=True)
        try:
            prd = prd_generator.generate_prd(analysis_summary, classified_reviews)
            st.session_state.data["prd"] = prd
            st.markdown('<div class="success-card"><strong>✅ PRD文档生成完成</strong></div>', unsafe_allow_html=True)
        except Exception as e:
            st.markdown(f'<div class="error-card"><strong>❌ 生成PRD时出错:</strong> {e}</div>', unsafe_allow_html=True)
            return
        
        st.session_state.stage = 5
        update_progress(62, 76)
        
        st.markdown('<div class="info-card"><strong>🧪 阶段6：生成测试用例</strong></div>', unsafe_allow_html=True)
        try:
            test_cases = test_generator.generate_test_cases(prd, classified_reviews)
            st.session_state.data["test_cases"] = test_cases
            st.markdown(f'<div class="success-card"><strong>✅ 生成 {len(test_cases)} 个测试用例</strong></div>', unsafe_allow_html=True)
        except Exception as e:
            st.markdown(f'<div class="error-card"><strong>❌ 生成测试用例时出错:</strong> {e}</div>', unsafe_allow_html=True)
            return
        
        st.session_state.stage = 6
        update_progress(76, 90)
        
        st.markdown('<div class="info-card"><strong>🔍 阶段7：幻觉校验</strong></div>', unsafe_allow_html=True)
        try:
            prd_check = hallucination_checker.check_prd(prd, classified_reviews)
            test_check = hallucination_checker.check_test_cases(test_cases, classified_reviews)
            report = hallucination_checker.generate_report(prd_check, test_check)
            st.session_state.data["hallucination_report"] = report
            
            if report["summary"]["overall_status"] == "PASS":
                st.markdown('<div class="success-card"><strong>✅ 幻觉校验通过</strong></div>', unsafe_allow_html=True)
            elif report["summary"]["overall_status"] == "WARNING":
                st.markdown('<div class="info-card"><strong>⚠️ 幻觉校验存在警告，建议人工审核</strong></div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="error-card"><strong>❌ 幻觉校验失败，建议全面人工审核</strong></div>', unsafe_allow_html=True)
        except Exception as e:
            st.markdown(f'<div class="error-card"><strong>❌ 幻觉校验时出错:</strong> {e}</div>', unsafe_allow_html=True)
            return
        
        st.session_state.stage = 7
        update_progress(90, 100)
        
        st.markdown("""
        <div style="background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%); color: white; border-radius: 12px; padding: 20px; text-align: center; margin-top: 16px;">
            <div style="font-size: 18px; font-weight: 700;">🎉 分析工作流完成！</div>
            <div style="opacity: 0.9; font-size: 13px; margin-top: 4px;">已成功完成所有分析步骤，请查看各Tab页获取详细结果</div>
        </div>
        """, unsafe_allow_html=True)

def update_progress(current, target):
    for i in range(current, target + 1):
        st.session_state.progress = i
        time.sleep(0.015)

def display_raw_data():
    data = st.session_state.get("data", {})
    
    if not data:
        st.markdown("""
        <div style="text-align: center; padding: 40px; color: #64748b;">
            <div style="font-size: 40px; margin-bottom: 12px;">📊</div>
            <div style="font-size: 16px; font-weight: 600; color: #1e293b; margin-bottom: 8px;">开始分析</div>
            <div style="font-size: 13px;">请在上方输入框中输入美区App Store链接，然后点击「开始分析」按钮</div>
        </div>
        """, unsafe_allow_html=True)
        return
    
    collection_result = data.get("collection_result", {})
    
    col_info1, col_info2 = st.columns(2)
    col_info1.markdown(f"<strong>数据源:</strong> <span style='color: #6366f1;'>{collection_result.get('data_source', '')}</span>", unsafe_allow_html=True)
    col_info2.markdown(f"<strong>数据局限性:</strong> <span style='color: #f59e0b;'>{collection_result.get('limitations', '')}</span>", unsafe_allow_html=True)
    
    raw_reviews = data.get("raw_reviews", [])
    if raw_reviews:
        df = pd.DataFrame(raw_reviews)
        st.dataframe(df, use_container_width=True, height=250)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{len(raw_reviews)}</div>
                <div class="metric-label">总评论数</div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            avg_rating = df['rating'].mean() if 'rating' in df.columns else 0
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{avg_rating:.2f}</div>
                <div class="metric-label">平均评分</div>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{datetime.now().strftime("%Y-%m-%d")}</div>
                <div class="metric-label">采集时间</div>
            </div>
            """, unsafe_allow_html=True)

def display_cleaned_data():
    data = st.session_state.get("data", {})
    
    if not data:
        st.markdown("""
        <div style="text-align: center; padding: 40px; color: #64748b;">
            <div style="font-size: 40px; margin-bottom: 12px;">🧹</div>
            <div style="font-size: 16px; font-weight: 600; color: #1e293b; margin-bottom: 8px;">等待数据清洗</div>
            <div style="font-size: 13px;">请先点击「开始分析」按钮执行数据采集和清洗</div>
        </div>
        """, unsafe_allow_html=True)
        return
    
    translated_reviews = data.get("translated_reviews", [])
    if translated_reviews:
        display_cols = ["review_id", "title", "title_zh", "content", "content_zh", "rating", "sentiment_label", "sentiment_label_zh", "category", "category_zh"]
        available_cols = [col for col in display_cols if col in translated_reviews[0]]
        df = pd.DataFrame(translated_reviews)[available_cols]
        st.dataframe(df, use_container_width=True, height=250)
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{len(translated_reviews)}</div>
                <div class="metric-label">清洗后有效评论数</div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            retention = len(translated_reviews) / len(data.get('raw_reviews', [1])) * 100
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{retention:.1f}%</div>
                <div class="metric-label">数据保留率</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('<h4 style="font-size: 15px; font-weight: 600; color: #1e293b; margin: 20px 0 12px;">📝 中英文对照预览</h4>', unsafe_allow_html=True)
        for i, review in enumerate(translated_reviews[:5], 1):
            with st.expander(f"评论 {i}: {review.get('title', '')}"):
                col_a, col_b = st.columns(2)
                with col_a:
                    st.markdown('<div class="lang-card"><div class="lang-title lang-en">📝 英文原文</div>', unsafe_allow_html=True)
                    st.write(f"<strong>标题:</strong> {review.get('title', '')}")
                    st.write(f"<strong>内容:</strong> {review.get('content', '')}")
                    st.markdown('</div>', unsafe_allow_html=True)
                with col_b:
                    st.markdown('<div class="lang-card"><div class="lang-title lang-zh">🌐 中文翻译</div>', unsafe_allow_html=True)
                    if "title_zh" in review:
                        st.write(f"<strong>标题:</strong> {review['title_zh']}")
                    if "content_zh" in review:
                        st.write(f"<strong>内容:</strong> {review['content_zh']}")
                    st.markdown('</div>', unsafe_allow_html=True)
                category_tag = f"<span class='tag-{review.get('category', 'other').lower()}'>{review.get('category_zh', review.get('category', ''))}</span>"
                sentiment_tag = f"<span class='tag-{review.get('sentiment_label', 'neutral').lower()}'>{review.get('sentiment_label_zh', review.get('sentiment_label', ''))}</span>"
                st.markdown(f"<strong>⭐ 评分:</strong> {review.get('rating', '')} | <strong>🏷️ 分类:</strong> {category_tag} | <strong>💭 情感:</strong> {sentiment_tag}", unsafe_allow_html=True)

def display_classification():
    data = st.session_state.get("data", {})
    
    if not data:
        st.markdown("""
        <div style="text-align: center; padding: 40px; color: #64748b;">
            <div style="font-size: 40px; margin-bottom: 12px;">🏷️</div>
            <div style="font-size: 16px; font-weight: 600; color: #1e293b; margin-bottom: 8px;">等待分类分析</div>
            <div style="font-size: 13px;">请先点击「开始分析」按钮执行分析流程</div>
        </div>
        """, unsafe_allow_html=True)
        return
    
    classified_reviews = data.get("classified_reviews", [])
    if classified_reviews:
        df = pd.DataFrame(classified_reviews)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown('<h4 style="font-size: 14px; font-weight: 600; color: #1e293b; margin-bottom: 12px;">📈 情感分布</h4>', unsafe_allow_html=True)
            sentiment_counts = df["sentiment_label_zh"].value_counts() if "sentiment_label_zh" in df.columns else df["sentiment_label"].value_counts()
            fig = px.pie(values=sentiment_counts.values, names=sentiment_counts.index, title="",
                       color_discrete_map={"正面": "#10b981", "负面": "#ef4444", "中性": "#f59e0b"},
                       height=260)
            fig.update_layout(showlegend=True)
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.markdown('<h4 style="font-size: 14px; font-weight: 600; color: #1e293b; margin-bottom: 12px;">📈 分类分布</h4>', unsafe_allow_html=True)
            category_counts = df["category_zh"].value_counts() if "category_zh" in df.columns else df["category"].value_counts()
            fig = px.bar(x=category_counts.index, y=category_counts.values, title="",
                       color_discrete_sequence=["#6366f1", "#8b5cf6", "#f59e0b", "#10b981", "#ef4444", "#ec4899", "#06b6d4"],
                       height=260)
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<h4 style="font-size: 14px; font-weight: 600; color: #1e293b; margin-bottom: 12px;">📊 评分分布</h4>', unsafe_allow_html=True)
        rating_counts = df["rating"].value_counts().sort_index()
        fig = px.bar(x=rating_counts.index, y=rating_counts.values, title="",
                   color_discrete_sequence=["#ef4444", "#f97316", "#f59e0b", "#84cc16", "#10b981"],
                   height=260)
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

def display_analysis():
    data = st.session_state.get("data", {})
    
    if not data:
        st.markdown("""
        <div style="text-align: center; padding: 40px; color: #64748b;">
            <div style="font-size: 40px; margin-bottom: 12px;">🔍</div>
            <div style="font-size: 16px; font-weight: 600; color: #1e293b; margin-bottom: 8px;">等待问题挖掘</div>
            <div style="font-size: 13px;">请先点击「开始分析」按钮执行分析流程</div>
        </div>
        """, unsafe_allow_html=True)
        return
    
    analysis_summary = data.get("analysis_summary", {})
    
    if analysis_summary:
        st.markdown('<h4 style="font-size: 15px; font-weight: 600; color: #1e293b; margin: 20px 0 12px;">🔥 关键问题（低评分评论）</h4>', unsafe_allow_html=True)
        key_issues = analysis_summary.get("key_issues", [])
        for issue in key_issues[:6]:
            with st.expander(f"问题 ({issue.get('rating')}星)"):
                col_a, col_b = st.columns(2)
                with col_a:
                    st.markdown('<div class="lang-card"><div class="lang-title lang-en">📝 英文原文</div>', unsafe_allow_html=True)
                    st.write(issue.get('content', ''))
                    st.markdown('</div>', unsafe_allow_html=True)
                with col_b:
                    st.markdown('<div class="lang-card"><div class="lang-title lang-zh">🌐 中文翻译</div>', unsafe_allow_html=True)
                    st.write(issue.get('content_zh', issue.get('content', '')))
                    st.markdown('</div>', unsafe_allow_html=True)
                st.write(f"<strong>🏷️ 分类:</strong> {issue.get('category_zh', issue.get('category', ''))}")
                st.write(f"<strong>💭 情感分数:</strong> {issue.get('sentiment_score', '')}")
                st.write(f"<strong>🔑 评论ID:</strong> {issue.get('review_id', '')}")
        
        st.markdown('<h4 style="font-size: 15px; font-weight: 600; color: #1e293b; margin: 20px 0 12px;">💡 用户功能需求</h4>', unsafe_allow_html=True)
        feature_requests = analysis_summary.get("feature_requests", [])
        for req in feature_requests[:6]:
            with st.expander(f"需求 ({req.get('rating')}星)"):
                col_a, col_b = st.columns(2)
                with col_a:
                    st.markdown('<div class="lang-card"><div class="lang-title lang-en">📝 英文原文</div>', unsafe_allow_html=True)
                    st.write(req.get('content', ''))
                    st.markdown('</div>', unsafe_allow_html=True)
                with col_b:
                    st.markdown('<div class="lang-card"><div class="lang-title lang-zh">🌐 中文翻译</div>', unsafe_allow_html=True)
                    st.write(req.get('content_zh', req.get('content', '')))
                    st.markdown('</div>', unsafe_allow_html=True)
                st.write(f"<strong>🔑 评论ID:</strong> {req.get('review_id', '')}")

def display_prd():
    data = st.session_state.get("data", {})
    
    if not data:
        st.markdown("""
        <div style="text-align: center; padding: 40px; color: #64748b;">
            <div style="font-size: 40px; margin-bottom: 12px;">📝</div>
            <div style="font-size: 16px; font-weight: 600; color: #1e293b; margin-bottom: 8px;">等待PRD生成</div>
            <div style="font-size: 13px;">请先点击「开始分析」按钮执行分析流程</div>
        </div>
        """, unsafe_allow_html=True)
        return
    
    prd = data.get("prd", {})
    
    if prd:
        col1, col2, col3, col4 = st.columns(4)
        col1.markdown(f"<strong>产品名称:</strong> <span style='color: #6366f1;'>{prd.get('product_name', '')}</span>", unsafe_allow_html=True)
        col2.markdown(f"<strong>PRD版本:</strong> <span style='color: #6366f1;'>{prd.get('prd_version', '')}</span>", unsafe_allow_html=True)
        col3.markdown(f"<strong>创建日期:</strong> <span style='color: #6366f1;'>{prd.get('created_date', '')[:10]}</span>", unsafe_allow_html=True)
        
        import json
        prd_json = json.dumps(prd, ensure_ascii=False, indent=2)
        col4.download_button(
            label="📥 下载PRD文档",
            data=prd_json,
            file_name=f"PRD_{prd.get('product_name', 'app').replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.json",
            mime="application/json",
            use_container_width=True
        )
        
        st.markdown('<h4 style="font-size: 15px; font-weight: 600; color: #1e293b; margin: 20px 0 12px;">📋 需求列表</h4>', unsafe_allow_html=True)
        requirements = prd.get("requirements", [])
        for req in requirements[:6]:
            with st.expander(f"{req.get('id', '')}: {req.get('title', '')}"):
                st.write(f"<strong>需求描述:</strong> {req.get('description', '')}")
                st.write(f"<strong>需求类型:</strong> {req.get('type', '')}")
                st.write(f"<strong>优先级:</strong> {req.get('priority', '')}")
                st.write(f"<strong>关联原始评论ID:</strong> <span style='color: #10b981;'>{', '.join(req.get('related_review_ids', []))}</span>", unsafe_allow_html=True)
        
        st.markdown('<h4 style="font-size: 15px; font-weight: 600; color: #1e293b; margin: 20px 0 12px;">📅 版本规划</h4>', unsafe_allow_html=True)
        version_plans = prd.get("version_plans", [])
        for plan in version_plans[:3]:
            with st.expander(f"🔹 {plan.get('version', '')}: {plan.get('focus', '')}"):
                st.write(f"<strong>版本目标:</strong> {plan.get('goal', '')}")
                for req in plan.get("requirements", []):
                    st.markdown(f"- {req.get('id', '')}: {req.get('title', '')}")

def display_test_cases():
    data = st.session_state.get("data", {})
    
    if not data:
        st.markdown("""
        <div style="text-align: center; padding: 40px; color: #64748b;">
            <div style="font-size: 40px; margin-bottom: 12px;">🧪</div>
            <div style="font-size: 16px; font-weight: 600; color: #1e293b; margin-bottom: 8px;">等待测试用例生成</div>
            <div style="font-size: 13px;">请先点击「开始分析」按钮执行分析流程</div>
        </div>
        """, unsafe_allow_html=True)
        return
    
    test_cases = data.get("test_cases", [])
    
    if test_cases:
        st.markdown(f"""
        <div class="metric-card" style="width: 180px; margin-bottom: 16px;">
            <div class="metric-value">{len(test_cases)}</div>
            <div class="metric-label">测试用例总数</div>
        </div>
        """, unsafe_allow_html=True)
        
        for tc in test_cases[:6]:
            with st.expander(f"{tc.get('test_id', '')}: {tc.get('title', '')}"):
                st.write(f"<strong>关联需求ID:</strong> <span style='color: #6366f1;'>{tc.get('requirement_id', '')}</span>", unsafe_allow_html=True)
                st.write(f"<strong>测试类型:</strong> {tc.get('test_type', '')}")
                st.write(f"<strong>优先级:</strong> {tc.get('priority', '')}")
                st.write(f"<strong>测试描述:</strong> {tc.get('description', '')}")
                
                st.write("<strong>测试步骤:</strong>")
                for step in tc.get("steps", []):
                    st.write(f"- {step}")
                
                st.write(f"<strong>预期结果:</strong> {tc.get('expected_result', '')}")

def display_verification():
    data = st.session_state.get("data", {})
    
    if not data:
        st.markdown("""
        <div style="text-align: center; padding: 40px; color: #64748b;">
            <div style="font-size: 40px; margin-bottom: 12px;">✅</div>
            <div style="font-size: 16px; font-weight: 600; color: #1e293b; margin-bottom: 8px;">等待幻觉校验</div>
            <div style="font-size: 13px;">请先点击「开始分析」按钮执行分析流程</div>
        </div>
        """, unsafe_allow_html=True)
        return
    
    report = data.get("hallucination_report", {})
    
    if report:
        summary = report.get("summary", {})
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{summary.get("prd_valid_count", 0)}</div>
                <div class="metric-label">PRD有效需求</div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{summary.get("prd_confidence", 0) * 100:.0f}%</div>
                <div class="metric-label">PRD置信度</div>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{summary.get("test_valid_count", 0)}</div>
                <div class="metric-label">测试用例有效</div>
            </div>
            """, unsafe_allow_html=True)
        with col4:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{summary.get("test_confidence", 0) * 100:.0f}%</div>
                <div class="metric-label">测试置信度</div>
            </div>
            """, unsafe_allow_html=True)
        
        status = summary.get("overall_status", "WARNING")
        if status == "PASS":
            st.markdown('<div class="success-card" style="text-align: center; padding: 16px; background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: white; border-color: transparent; font-size: 14px;"><strong>✅ 校验通过 - AI生成内容均有原始评论支撑</strong></div>', unsafe_allow_html=True)
        elif status == "WARNING":
            st.markdown('<div class="info-card" style="text-align: center; padding: 16px; background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); color: white; border-color: transparent; font-size: 14px;"><strong>⚠️ 存在警告 - 建议人工审核部分内容</strong></div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="error-card" style="text-align: center; padding: 16px; background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%); color: white; border-color: transparent; font-size: 14px;"><strong>❌ 校验失败 - 建议全面人工审核</strong></div>', unsafe_allow_html=True)
        
        st.markdown('<h4 style="font-size: 15px; font-weight: 600; color: #1e293b; margin: 20px 0 12px;">📋 PRD校验详情</h4>', unsafe_allow_html=True)
        prd_check = report.get("prd_validation", {})
        
        valid_reqs = prd_check.get("valid_requirements", [])
        if valid_reqs:
            st.markdown("<strong>✅ 有效需求（有原始评论支撑）:</strong>")
            for req in valid_reqs[:10]:
                st.write(f"- {req.get('requirement_id', '')}: {req.get('title', '')[:60]}... | 关联评论: {req.get('related_reviews', 0)}条 | 置信度: {req.get('confidence', 0) * 100:.0f}%")
        
        invalid_reqs = prd_check.get("invalid_requirements", [])
        if invalid_reqs:
            st.markdown("<strong>❌ 无效需求（无原始评论支撑）:</strong>")
            for req in invalid_reqs:
                st.write(f"- {req.get('requirement_id', '')}: {req.get('issue', '')}")
        
        warnings = prd_check.get("warnings", [])
        if warnings:
            st.markdown("<strong>⚠️ 警告（关联度较低）:</strong>")
            for warning in warnings:
                st.write(f"- {warning.get('requirement_id', '')}: {warning.get('issue', '')} | 置信度: {warning.get('confidence', 0) * 100:.0f}%")
        
        if not valid_reqs and not invalid_reqs and not warnings:
            st.markdown("<strong>暂无校验详情</strong>", unsafe_allow_html=True)
        
        st.markdown('<h4 style="font-size: 15px; font-weight: 600; color: #1e293b; margin: 20px 0 12px;">📋 测试用例校验详情</h4>', unsafe_allow_html=True)
        test_check = report.get("test_case_validation", {})
        
        valid_tcs = test_check.get("valid_test_cases", [])
        if valid_tcs:
            st.markdown("<strong>✅ 有效测试用例:</strong>")
            for tc in valid_tcs[:10]:
                st.write(f"- {tc.get('test_id', '')}: {tc.get('title', '')[:60]}... | 关联评论: {tc.get('related_reviews', 0)}条 | 置信度: {tc.get('confidence', 0) * 100:.0f}%")
        
        invalid_tcs = test_check.get("invalid_test_cases", [])
        if invalid_tcs:
            st.markdown("<strong>❌ 无效测试用例:</strong>")
            for tc in invalid_tcs:
                st.write(f"- {tc.get('test_id', '')}: {tc.get('issue', '')}")
        
        test_warnings = test_check.get("warnings", [])
        if test_warnings:
            st.markdown("<strong>⚠️ 警告（关联度较低）:</strong>")
            for warning in test_warnings:
                st.write(f"- {warning.get('test_id', '')}: {warning.get('issue', '')} | 置信度: {warning.get('confidence', 0) * 100:.0f}%")
        
        if not valid_tcs and not invalid_tcs and not test_warnings:
            st.markdown("<strong>暂无校验详情</strong>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()