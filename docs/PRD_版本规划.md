# iOS健身应用 产品需求文档（PRD）

## 一、需求背景
基于美国区App Store 476条有效用户评论分析，针对核心差评痛点制定本版本迭代规划，所有需求均可追溯至原始用户评价。

## 二、核心痛点统计
- 低分差评总数：134 条
- Top3负面问题：付费订阅、广告过多、训练内容不足

## 三、V1.0 紧急修复版
- **优先级**：P0 / P1
- **版本目标**：解决核心差评痛点，降低卸载率

### 需求1：修复已知崩溃闪退问题
- **需求描述**：排查并修复导致应用闪退的场景，保证运行稳定性
- **验收标准**：连续使用30分钟无闪退，崩溃率降至0.1%以下
- **用户评论溯源**：
  > 1. 评分2星：Used to be better now you need to watch ads for the free workouts which is fine but the ads are glitchy and you can’t al...
  > 2. 评分1星：A once decent app now unusable thanks to constant pop ups and not even being able to do free workouts without getting a ...

### 需求2：优化订阅扣费提示与退款说明
- **需求描述**：订阅页增加清晰的扣费周期、取消方式、退款规则说明，避免用户误订阅
- **验收标准**：订阅前用户可完整查看扣费规则，付费类差评占比下降30%
- **用户评论溯源**：
  > 1. 评分1星：Is there anything that is free on this app anymore?? Even workouts I had previously saved now ask you to pay. Ridiculous
  > 2. 评分1星：Cancelled my subscription and then received not one but two charges in the same day totaling almost $100!!! Don’t do it!...

### 需求3：降低训练过程中的广告频次
- **需求描述**：训练进行中不插播广告，仅在训练结束后展示，每日广告上限设为3条
- **验收标准**：训练全程无广告打断，广告相关差评占比下降40%
- **用户评论溯源**：
  > 1. 评分1星：Is there anything that is free on this app anymore?? Even workouts I had previously saved now ask you to pay. Ridiculous
  > 2. 评分1星：I do not care if I have to watch ads but what I do care about is if I get a pop up screen with no continuation option on...

## 三、V1.1 体验优化版
- **优先级**：P1 / P2
- **版本目标**：优化基础使用体验，提升留存

### 需求1：简化训练操作流程与界面导航
- **需求描述**：优化首页布局，一键直达训练，减少操作层级
- **验收标准**：用户开始一次训练的点击次数减少至2次以内
- **用户评论溯源**：
  > 1. 评分1星：I do not care if I have to watch ads but what I do care about is if I get a pop up screen with no continuation option on...
  > 2. 评分2星：I remembered using this app when I was in middle school and decided to try it again to help with some health problems I ...

### 需求2：优化视频加载与播放流畅度
- **需求描述**：增加视频预加载机制，优化弱网环境下的播放体验
- **验收标准**：视频播放加载时间缩短至1秒内，无卡顿黑屏
- **用户评论溯源**：
  > 1. 评分1星：I downloaded this app yesterday and I wanted to try the 1-week free trial, but once I used the Apple Pay feature to subs...
  > 2. 评分1星：The app may be free to download but there is little to no workouts now that you can do for free. I’ve had this app for a...

### 需求3：新增新手引导流程
- **需求描述**：首次启动增加3步引导，教会用户核心功能用法
- **验收标准**：新用户7日留存率提升15%
- **用户评论溯源**：
  > 1. 评分1星：Cancelled subscription and still got charged for it. No spot in app to manage no place on website either. Went to contac...
  > 2. 评分1星：I downloaded this app yesterday and I wanted to try the 1-week free trial, but once I used the Apple Pay feature to subs...

## 三、V1.2 内容扩充版
- **优先级**：P2
- **版本目标**：丰富训练内容，提升用户长期使用价值

### 需求1：新增3套完整训练课程
- **需求描述**：补充塑形、燃脂、力量三个方向的新课程，每个课程含8个动作
- **验收标准**：训练课程总量翻倍，用户周使用时长提升20%
- **用户评论溯源**：
  > 1. 评分1星：Is there anything that is free on this app anymore?? Even workouts I had previously saved now ask you to pay. Ridiculous
  > 2. 评分1星：I do not care if I have to watch ads but what I do care about is if I get a pop up screen with no continuation option on...

### 需求2：支持自定义训练计划
- **需求描述**：允许用户自行选择动作、组合训练时长，生成专属计划
- **验收标准**：自定义训练使用占比达到总训练量的20%
- **用户评论溯源**：
  > 1. 评分1星：Cancelled subscription and still got charged for it. No spot in app to manage no place on website either. Went to contac...
  > 2. 评分1星：I downloaded this app yesterday and I wanted to try the 1-week free trial, but once I used the Apple Pay feature to subs...

