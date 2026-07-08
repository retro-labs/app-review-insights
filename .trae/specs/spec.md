# LaienTech iOS 应用审查分析和版本规划评估 - 产品需求文档

## Overview
- **Summary**: 构建一个可运行的 Web 应用程序，实现从美区 App Store 收集用户评论、清洗分析、生成产品需求文档 (PRD) 和测试用例的完整工作流程。
- **Purpose**: 将真实用户评价转化为可执行的产品方案，展示"氛围编码"能力和 AI/Agent 使用能力。
- **Target Users**: 产品经理、开发团队、面试官（评估候选人能力）

## Goals
- [x] 收集美区 App Store 应用真实用户评论数据
- [x] 清洗并整理评论数据，去除无效数据
- [x] 对评论进行分类和情感分析
- [x] 根据分析结果生成产品需求文档 (PRD)，包含版本规划
- [x] 根据 PRD 生成测试用例，每条用例可追溯到原始评论
- [x] 在用户界面中展示完整工作流程进度
- [x] 展示各阶段中期交付成果
- [x] 实现 AI 生成内容的幻觉校验机制

## Non-Goals (Out of Scope)
- [ ] 不实现用户注册/登录系统
- [ ] 不实现多应用并行分析
- [ ] 不实现外部 API 调用的完整高可用架构
- [ ] 不实现商业化部署方案

## Background & Context
- 目标应用：Workout for Women: Home Gym (App ID: 839285684)
- 数据源：美区 App Store 官方 API / 第三方数据采集库
- 技术栈：Python + Streamlit + 数据分析库
- 评估标准：数据真实性、分析合理性、PRD 质量、测试用例可追溯性、UI 可用性

## Functional Requirements
- **FR-1**: 用户可输入美区 App Store 链接，系统自动提取 App ID
- **FR-2**: 系统自动采集应用的用户评价数据（支持多级降级策略）
- **FR-3**: 系统清洗并整理评论数据（去重、去除空数据、标准化格式）
- **FR-4**: 系统对评论进行分类（Bug、功能需求、性能、易用性等）和情感分析
- **FR-5**: 系统提取关键问题和功能需求
- **FR-6**: 系统根据分析结果生成产品需求文档 (PRD)，包含多版本规划
- **FR-7**: 系统根据 PRD 生成测试用例，每条用例标记关联评论
- **FR-8**: 系统对 AI 生成内容进行幻觉校验，确保可追溯
- **FR-9**: 用户界面展示完整工作流程进度，包含各阶段状态
- **FR-10**: 用户界面展示各阶段中期交付成果（原始数据、清洗后数据、分类结果等）
- **FR-11**: 用户界面展示最终分析结果、PRD 文档和测试用例
- **FR-12**: 支持中英文对照显示评论内容，方便开发理解

## Non-Functional Requirements
- **NFR-1**: 应用可在本地环境一键运行
- **NFR-2**: 网络环境受限情况下，提供缓存数据或示例数据作为降级方案
- **NFR-3**: 所有 AI 生成内容必须保留原始评论证据
- **NFR-4**: 界面响应时间 < 3 秒（不包括数据采集时间）
- **NFR-5**: 代码结构清晰，包含完整注释和文档

## Constraints
- **Technical**: Python 3.12+, Streamlit, 需处理依赖版本冲突
- **Business**: 数据来源必须合规，禁止网页爬虫，禁止编造数据
- **Dependencies**: 依赖第三方库采集 App Store 评论数据

## Assumptions
- [x] 用户具备基本 Python 环境配置能力
- [x] 网络环境可能受限，需提供离线降级方案
- [x] 项目用于面试评估，需展示完整的实现过程和思考

## Acceptance Criteria

### AC-1: 数据采集功能
- **Given**: 用户输入有效的美区 App Store 链接
- **When**: 点击"开始分析"按钮
- **Then**: 系统成功采集评论数据，显示采集数量和数据源说明
- **Verification**: `programmatic`

### AC-2: 数据清洗功能
- **Given**: 已采集原始评论数据
- **When**: 执行清洗步骤
- **Then**: 数据被清洗并保留有效评论，显示保留率统计
- **Verification**: `programmatic`

### AC-3: 评论分类功能
- **Given**: 已清洗评论数据
- **When**: 执行分类分析
- **Then**: 每条评论被标记分类标签和情感标签，显示分布图表
- **Verification**: `human-judgment`

### AC-4: PRD 生成功能
- **Given**: 已完成分类分析
- **When**: 执行 PRD 生成
- **Then**: 生成包含需求列表和版本规划的 PRD，每条需求关联原始评论
- **Verification**: `human-judgment`

### AC-5: 测试用例生成功能
- **Given**: 已生成 PRD
- **When**: 执行测试用例生成
- **Then**: 生成测试用例，每条用例可追溯到相关评论
- **Verification**: `human-judgment`

### AC-6: 幻觉校验功能
- **Given**: 已生成 PRD 和测试用例
- **When**: 执行幻觉校验
- **Then**: 生成校验报告，验证 AI 生成内容的可靠性
- **Verification**: `programmatic`

### AC-7: 用户界面展示
- **Given**: 系统运行正常
- **When**: 用户访问应用
- **Then**: 界面展示工作流程进度、各阶段成果和最终结果
- **Verification**: `human-judgment`

### AC-8: 中英文对照功能
- **Given**: 已采集英文评论
- **When**: 查看评论详情
- **Then**: 同时显示英文原文和中文翻译
- **Verification**: `human-judgment`

### AC-9: 离线运行能力
- **Given**: 网络环境受限
- **When**: 运行应用并点击分析
- **Then**: 系统使用缓存数据或示例数据完成分析流程
- **Verification**: `programmatic`

## Open Questions
- [x] App Store API 访问限制和替代方案已确认
- [x] 依赖版本冲突解决方案已确认
- [x] 中英文翻译方案已确认