# LaienTech iOS 应用审查分析和版本规划评估 - 实现计划

## [x] Task 1: 数据采集模块修复
- **Priority**: high
- **Depends On**: None
- **Description**: 
  - 修复 app-store-scraper 调用参数问题（添加 app_name）
  - 确保多级降级策略正常工作（scraper → XML → 缓存 → 示例数据）
  - 安装 lxml 解析器支持
- **Acceptance Criteria Addressed**: AC-1, AC-9
- **Test Requirements**:
  - `programmatic` TR-1.1: 采集模块能成功采集或降级到示例数据
  - `programmatic` TR-1.2: 输出文件包含正确格式的评论数据
- **Notes**: 处理网络环境限制，提供离线降级方案

## [x] Task 2: 数据清洗模块完善
- **Priority**: high
- **Depends On**: Task 1
- **Description**: 
  - 实现评论去重、空数据过滤、格式标准化
  - 保留必要字段（review_id, title, content, rating, version, username, date）
- **Acceptance Criteria Addressed**: AC-2
- **Test Requirements**:
  - `programmatic` TR-2.1: 清洗后数据无重复评论
  - `programmatic` TR-2.2: 清洗后数据无空内容评论
- **Notes**: 确保数据质量，为后续分析提供可靠基础

## [x] Task 3: 评论分类与情感分析模块
- **Priority**: high
- **Depends On**: Task 2
- **Description**: 
  - 实现关键词匹配分类（Bug、功能需求、性能、易用性、内容、订阅、其他）
  - 实现情感分析（正面、负面、中性）
  - 添加中英文标签对照
- **Acceptance Criteria Addressed**: AC-3
- **Test Requirements**:
  - `human-judgment` TR-3.1: 分类结果合理，符合评论内容
  - `human-judgment` TR-3.2: 情感分析结果符合预期
- **Notes**: 使用 TextBlob 进行情感分析，关键词分类可扩展

## [x] Task 4: 中英文翻译模块
- **Priority**: medium
- **Depends On**: Task 2
- **Description**: 
  - 创建翻译模块，支持英文评论翻译为中文
  - 提供内置翻译缓存和示例翻译
  - 支持 TextBlob 自动翻译作为补充
- **Acceptance Criteria Addressed**: AC-8
- **Test Requirements**:
  - `human-judgment` TR-4.1: 翻译结果准确，符合原文含义
  - `programmatic` TR-4.2: 每条评论包含 title_zh 和 content_zh 字段
- **Notes**: 离线可用，内置示例翻译确保网络环境受限情况下仍有翻译结果

## [x] Task 5: 问题挖掘与分析模块
- **Priority**: high
- **Depends On**: Task 3, Task 4
- **Description**: 
  - 提取低评分关键问题
  - 提取功能需求
  - 分析评论分布和趋势
  - 保留中文翻译字段
- **Acceptance Criteria Addressed**: AC-3
- **Test Requirements**:
  - `human-judgment` TR-5.1: 关键问题提取准确，覆盖主要用户痛点
  - `human-judgment` TR-5.2: 功能需求提取合理，有明确用户需求依据
- **Notes**: 为 PRD 生成提供数据基础

## [x] Task 6: PRD 生成模块
- **Priority**: high
- **Depends On**: Task 5
- **Description**: 
  - 根据分析结果生成产品需求文档
  - 每条需求关联原始评论 ID
  - 拆分为多版本规划（紧急 Bug 修复、重要功能、体验提升）
  - 添加需求优先级、影响范围、工作量评估
- **Acceptance Criteria Addressed**: AC-4
- **Test Requirements**:
  - `human-judgment` TR-6.1: PRD 结构完整，包含需求列表和版本规划
  - `human-judgment` TR-6.2: 每条需求可追溯到原始评论
- **Notes**: 展示 AI/Agent 使用能力，需求生成逻辑清晰

## [x] Task 7: 测试用例生成模块
- **Priority**: high
- **Depends On**: Task 6
- **Description**: 
  - 根据 PRD 生成测试用例
  - 每条测试用例关联需求 ID 和原始评论
  - 区分功能测试和回归测试
  - 包含测试步骤和预期结果
- **Acceptance Criteria Addressed**: AC-5
- **Test Requirements**:
  - `human-judgment` TR-7.1: 测试用例覆盖 PRD 需求
  - `human-judgment` TR-7.2: 每条测试用例可追溯到相关评论
- **Notes**: 测试用例设计合理，覆盖主要场景

## [x] Task 8: 幻觉校验模块
- **Priority**: high
- **Depends On**: Task 6, Task 7
- **Description**: 
  - 校验 PRD 需求是否有原始评论支撑
  - 校验测试用例是否可追溯
  - 计算置信度评分
  - 生成校验报告
- **Acceptance Criteria Addressed**: AC-6
- **Test Requirements**:
  - `programmatic` TR-8.1: 校验报告包含有效/无效需求统计
  - `programmatic` TR-8.2: 置信度计算准确，符合预期
- **Notes**: 防止 AI 幻觉，确保分析结果可靠性

## [x] Task 9: 用户界面模块
- **Priority**: high
- **Depends On**: 所有模块
- **Description**: 
  - 使用 Streamlit 构建交互式界面
  - 展示工作流程进度（8个阶段）
  - 展示各阶段中期交付成果
  - 展示最终分析结果、PRD 和测试用例
  - 支持中英文对照显示
  - 默认展开侧边栏，无需切换按钮
- **Acceptance Criteria Addressed**: AC-7, AC-8
- **Test Requirements**:
  - `human-judgment` TR-9.1: 界面清晰，操作流程直观
  - `human-judgment` TR-9.2: 各阶段成果展示完整
- **Notes**: 中文界面，美观易用

## [x] Task 10: 项目文档与部署
- **Priority**: medium
- **Depends On**: 所有模块
- **Description**: 
  - 创建 README.md，包含项目说明和部署步骤
  - 更新 requirements.txt，解决依赖冲突
  - 创建数据采集方法说明文档
  - 创建示例输出数据，确保离线可运行
- **Acceptance Criteria Addressed**: AC-9
- **Test Requirements**:
  - `human-judgment` TR-10.1: README 文档完整，部署步骤清晰
  - `programmatic` TR-10.2: pip install -r requirements.txt 可成功安装
- **Notes**: 确保项目可在本地一键运行