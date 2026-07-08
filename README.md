\# App Store 用户评论分析工具

\## 项目简介

基于苹果官方RSS接口，自动化抓取美国区App Store用户评论，完成数据清洗、智能分类、痛点统计，并自动输出产品迭代规划（PRD）与标准化测试用例。所有需求均可追溯至原始用户评价，为产品迭代提供数据支撑。

\## 核心功能

1\.  \*\*评论抓取\*\*：调用苹果官方公开RSS接口，分页获取最多500条美国区用户评论

2\.  \*\*数据清洗\*\*：自动去重、过滤无效短评论、统一结构化字段

3\.  \*\*智能分类\*\*：基于关键词规则，将评论分为8大类（崩溃bug、付费吐槽、广告、内容不足等）

4\.  \*\*痛点统计\*\*：分别统计全量与低分差评的问题分布，定位核心负面反馈

5\.  \*\*PRD自动生成\*\*：基于痛点输出三版本迭代规划，每条需求附带原始评论溯源

6\.  \*\*测试用例生成\*\*：对应产品需求，输出标准化功能测试用例清单

\## 目录结构
```

app-analysis/

├── backend/ # 后端脚本目录

│ ├── get\_reviews.py # 评论抓取脚本

│ ├── clean\_reviews.py # 数据清洗脚本

│ ├── classify\_reviews.py # 评论分类与统计脚本

│ ├── generate\_prd.py # PRD 与版本规划生成脚本

│ └── generate\_testcases.py # 测试用例生成脚本

├── sample\_data/ # 数据文件目录

│ ├── reviews\_raw.json # 原始评论数据

│ ├── reviews\_cleaned.json # 清洗后评论数据

│ ├── reviews\_classified.json # 带分类标签的评论数据

│ └── analysis\_stats.json # 痛点统计结果

├── docs/ # 产出文档目录

│ ├── PRD\_版本规划.md # 产品需求文档与迭代规划

│ └── 测试用例清单.md # 标准化功能测试用例

└── README.md # 项目说明文档

\## 使用方法

1\. 确保已安装Python 3.x环境

2\. 依次执行以下脚本：
```

py backend/get\_reviews.py # 抓取评论

py backend/clean\_reviews.py # 清洗数据

py backend/classify\_reviews.py # 分类统计

py backend/generate\_prd.py # 生成 PRD

py backend/generate\_testcases.py # 生成测试用例
```

3\. 执行完成后，查看 `sample\_data` 与 `docs` 目录下的产出文件

\## 数据说明

\- 数据源：苹果iTunes官方公开RSS评论接口

\- 数据范围：美国区、按最新排序、最多10页共500条评论

\- 局限性：RSS接口仅提供最多500条评论，无法获取全量历史评价

\## 版本迭代记录

\- V1.0：完成评论抓取、清洗、分类三大基础模块

\- V1.1：新增PRD自动生成与评论溯源功能

\- V1.2：新增标准化测试用例自动生成功能

