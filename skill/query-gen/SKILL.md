---
name: query-gen
description: Generate realistic search queries based on user personas for testing search/recommendation systems. Use when creating test queries, evaluating search quality across demographics, or benchmarking recommendation algorithms with diverse user behavior patterns.
---

# Query Generator Skill

基于数字人设自动生成真实搜索 Query，用于评测搜索推荐系统效果。

## 核心功能

- **8 种用户人设**: 覆盖宝妈、老人、Z 世代等不同群体
- **9 大生活场景**: 医疗、母婴、餐饮、教育、生活服务等
- **自然语言生成**: 根据人设特征生成符合真实表达习惯的 Query
- **评测友好**: 输出包含预期评测重点，便于自动化评测
- **CLI 支持**: 完整的命令行接口，支持多种输出格式

## 快速开始

### CLI 命令行使用 (推荐)

**查看帮助:**

```bash
cd /Users/linjie/Documents/workspace/skill/query-gen/python

python3 query_gen_cli.py --help
```

**常用命令:**

```bash
# 列出所有人设和场景
python3 query_gen_cli.py --list

# 生成单个 Query
python3 query_gen_cli.py --persona "新手焦虑型妈妈" --scene "医疗健康"

# 批量生成 10 条
python3 query_gen_cli.py --persona "新手焦虑型妈妈" --scene "医疗健康" --count 10

# 多人群对比
python3 query_gen_cli.py --multi --personas "新手焦虑型妈妈,谨慎保守型老人" --scene "医疗健康" --count 5

# 输出 JSON 格式
python3 query_gen_cli.py --persona "新手焦虑型妈妈" --scene "医疗健康" --count 5 --format json

# 保存到文件
python3 query_gen_cli.py --persona "新手焦虑型妈妈" --scene "医疗健康" --count 100 --format csv --output queries.csv
```

**CLI 参数说明:**

| 参数 | 简写 | 说明 | 示例 |
|------|------|------|------|
| `--persona` | `-p` | 人设名称 | `--persona "新手焦虑型妈妈"` |
| `--scene` | `-s` | 场景名称 | `--scene "医疗健康"` |
| `--count` | `-c` | 生成数量 | `--count 10` |
| `--multi` | `-m` | 多人群对比模式 | `--multi` |
| `--personas` | | 多个人设(逗号分隔) | `--personas "妈妈,老人"` |
| `--format` | `-f` | 输出格式(text/json/csv) | `--format json` |
| `--output` | `-o` | 输出文件路径 | `--output result.json` |
| `--list` | `-l` | 列出所有人设和场景 | `--list` |

### Java 使用

**编译和运行:**

```bash
cd /Users/linjie/Documents/workspace/skill/query-gen/java

# 编译
javac QueryGenerator.java QueryGeneratorDemo.java

# 运行演示
java QueryGeneratorDemo
```

**代码示例:**

```java
// 1. 初始化
QueryGenerator generator = new QueryGenerator();

// 2. 生成单个 Query
GeneratedQuery query = generator.generateSingle("新手焦虑型妈妈", "医药健康");
System.out.println(query.getQuery());  
// → "urgent 宝宝发烧 求推荐附近5公里范围内的药店"

// 3. 批量生成
List<GeneratedQuery> queries = generator.generateBatch(
    "新手焦虑型妈妈", "母婴保健", 10
);

// 4. 多人群对比
Map<String, List<GeneratedQuery>> results = generator.generateMultiPersona(
    Arrays.asList("新手焦虑型妈妈", "谨慎保守型老人"),
    "医药健康", 
    5
);

// 5. 获取所有人设/场景名称
Set<String> personas = generator.getAllPersonaNames();
Set<String> scenes = generator.getAllSceneNames();
```

### Python 使用

**运行演示:**

```bash
cd /Users/linjie/Documents/workspace/skill/query-gen/python

# 运行演示
python3 test_demo.py
```

**代码示例:**

```python
from query_generator import QueryGenerator

generator = QueryGenerator()

# 生成单个 Query
query = generator.generate_single("新手焦虑型妈妈", "医药健康")
print(query.query)  # → "urgent 宝宝发烧 求推荐半小时内能够送达的布洛芬"

# 批量生成
queries = generator.generate_batch("效率实用型妈妈", "品牌", count=10)

# 多人群对比
results = generator.generate_multi_persona(
    ["价格敏感型妈妈", "品质追求型妈妈"],
    "母婴保健",
    count_per_persona=5
)
```

## 支持的人设

| 人设 ID | 人设名称 | 特征描述 | Query 风格 |
|--------|----------|----------|-----------|
| P001 | 新手焦虑型妈妈 | 0-1 岁宝宝，第一胎，谨慎焦虑 | 长句、多疑问、强调"靠谱/安全" |
| P002 | 效率实用型妈妈 | 职场妈妈，时间碎片化，追求效率 | 短句、关键词、强调"快/近" |
| P003 | 品质追求型妈妈 | 经济条件好，注重品质和体验 | 描述详细、强调"品牌/高端/专业" |
| P004 | 价格敏感型妈妈 | 精打细算，关注性价比 | 简洁直接、强调"便宜/优惠/价格范围" |
| P005 | 社交分享型妈妈 | 爱新鲜事物，爱分享，跟风 | 求推荐、带情感词 |
| P006 | 谨慎保守型老人 | 60 岁+，数字素养低，害怕被骗 | 正式、强调"正规/有保障" |
| P007 | 求助依赖型老人 | 不熟悉操作，习惯求助 | 求助式、简单语言 |
| P008 | 潮流探索型Z世代 | 18-25 岁，追新潮，注重体验 | 短句、网络用语、潮流词 |

**注意**: 人设名称包含特殊字符"Z世代"(无空格)，使用时请确保完全匹配。建议通过 `getAllPersonaNames()` 获取准确名称。

## 支持的场景

### 医药健康（电商零售）
- **需求**: 退烧药、感冒药、过敏药、益生菌、维生素、钙片、口罩、体温计、血压计、血糖仪、药店
- **品牌**:
  - 退烧药: 强生、美林、泰诺林、仁和、葵花药业、哈药、修正
  - 感冒药: 999、白云山、以岭、仁和、同仁堂、香雪、云南白药
  - 过敏药: 开瑞坦、息斯敏、仙特明、顺尔宁、贝分
  - 益生菌: 合生元、妈咪爱、康萃乐、Life-Space、培菲康、金双歧、拜奥
  - 维生素: 伊可新、星鲨、汤臣倍健、Swisse、善存、21金维他
  - 钙片: 钙尔奇、迪巧、朗迪、Swisse、三精、龙牡
  - 口罩: 稳健、振德、3M、霍尼韦尔、袋鼠医生、可孚、海氏海诺
  - 体温计: 博朗、欧姆龙、鱼跃、可孚、迈克大夫、华盛昌
  - 血压计: 欧姆龙、鱼跃、可孚、松下、九安、乐心
  - 血糖仪: 罗氏、强生、欧姆龙、鱼跃、三诺、艾科、雅培
  - 药店: 海王星辰、老百姓大药房、国大药房、同仁堂、大参林、益丰大药房、一心堂、叮当快药
- **规格/特征**:
  - 退烧药: 布洛芬、对乙酰氨基酚、美林、泰诺林、小儿退热栓、退热贴
  - 感冒药: 小儿氨酚黄那敏、999感冒灵、板蓝根、连花清瘟、蒲地蓝、小柴胡、抗病毒口服液
  - 过敏药: 氯雷他定、西替利嗪、扑尔敏、孟鲁司特钠
  - 益生菌: 妈咪爱、合生元、康萃乐、Life-Space、培菲康、金双歧
  - 维生素: D3、AD、复合、DHA、维生素C、维生素B
  - 钙片: 钙尔奇、迪巧、朗迪、Swisse、葡萄糖酸钙、乳钙
  - 口罩: N95、医用外科、儿童口罩、KN95、一次性医用
  - 体温计: 电子、耳温枪、额温枪、水银、红外测温
  - 血压计: 电子血压计、手腕式、上臂式
  - 血糖仪: 免调码、智能、家用
  - 药店: 24小时、连锁、医保定点、网上药店

### 母婴用品
- **需求**: 奶粉、纸尿裤、辅食、玩具、童装、婴儿车
- **品牌**: 
  - 奶粉: 飞鹤、美赞臣、惠氏、雅培、贝因美、爱他美、雀巢、伊利
  - 纸尿裤: 花王、帮宝适、好奇、尤妮佳、大王
  - 辅食: 嘉宝、亨氏、小皮、贝拉米
  - 玩具: 费雪、乐高、伟易达、面包超人
  - 童装: 英氏、巴拉巴拉、丽婴房、全棉时代
  - 婴儿车: 好孩子、昆塔斯、虎贝尔、bebebus
- **规格/特征**:
  - 奶粉: 1段、2段、3段、羊奶、有机、水解蛋白
  - 纸尿裤: NB码、S码、M码、L码、拉拉裤、超薄透气、夜用
  - 辅食: 6个月、9个月、12个月、高铁、无添加、有机
  - 玩具: 益智、积木、毛绒、早教、安抚、咬胶
  - 童装: 纯棉、加厚、连体、分体、0-3个月、3-6个月
  - 婴儿车: 轻便、可躺、双向、高景观、一键收车、避震

### 餐饮外卖
- **需求**: 儿童餐、营养餐、辅食、月子餐、亲子餐厅、外卖、快餐

### 教育早教
- **需求**: 早教中心、托班、兴趣班、幼儿园、亲子活动、游泳、英语

### 生活服务
- **需求**: 保洁、月嫂、育儿嫂、儿童摄影、维修、洗衣

### 休闲娱乐
- **需求**: 儿童乐园、亲子游、游泳馆、绘本馆、亲子酒店、游乐场、动物园

### 社区服务
- **需求**: 社区医院、老年食堂、便民超市、快递代收、理发、维修

### 便民生活
- **需求**: 缴费、充值、查询、预约、办事、咨询

### 新潮服务
- **需求**: 剧本杀、密室、VR、电竞、自拍馆、猫咖、潮玩

## 通用维度（所有场景适用）

### 地理位置
- 3公里内、5公里内、10公里内、附近、周边

### 配送维度
- **配送时长**: 30分钟达、1小时达、2小时达、当日达、次日达
- **配送速度**: 急送、快送、同城配送、小时达

### 价格维度（所有场景适用）
- **具体金额**: 50元以内、100元以内、200元以内、300元以内、500元以内、1000元以内、2000元以内
- **模糊范围**: 50块左右、100块左右、200块左右
- **价格特征**: 便宜点、实惠的、平价的、性价比高的、高品质的

## 人设特征详解

### 价格范围触发概率
不同人设对价格的关注程度不同，价格范围在各人设中的触发概率：
- **价格敏感型妈妈 (P004)**: 60% 概率（最高）
- **效率实用型妈妈 (P002)**: 30% 概率
- **新手焦虑型妈妈 (P001)**: 30% 概率
- **社交分享型妈妈 (P005)**: 30% 概率
- **谨慎保守型老人 (P006)**: 30% 概率
- **求助依赖型老人 (P007)**: 30% 概率
- **潮流探索型Z世代 (P008)**: 30% 概率
- **品质追求型妈妈 (P003)**: 20% 概率（较低，更关注品质）

### 价格敏感型妈妈 (P004) - 价格范围示例
**Query 示例：**
- "200元以内的过敏药哪里买"
- "体温计100块左右有吗"
- "想买便宜点的钙片"
- "实惠的益生菌有吗"
- "求推荐性价比高的维生素"

### 其他人设 - 价格范围示例
**新手焦虑型妈妈：**
- "孩子发烧，推荐200元以内的退烧药"
- "想买实惠的体温计，求推荐"

**效率实用型妈妈：**
- "300元以内儿童餐附近"
- "找性价比高的月嫂"

**品质追求型妈妈：**
- "求推荐1000元以内高品质的奶粉"
- "想买2000元以内高端的婴儿车"

## 输出字段说明

```json
{
  "query": "生成的 Query 文本",
  "persona": "人设名称",
  "scene": "场景名称", 
  "intent": "用户意图",
  "complexity": "复杂度 (高/中/低)",
  "emotionLevel": "情感强度 (高/中/低)",
  "expectedFocus": ["评测重点 1", "评测重点 2"]
}
```

## 使用场景示例

### 场景 1: 搜索质量评测

```java
// 为不同人设生成测试 Query，评测搜索系统
String[] personas = {"新手焦虑型妈妈", "效率实用型妈妈", "谨慎保守型老人"};

for (String persona : personas) {
    List<GeneratedQuery> queries = generator.generateBatch(persona, "医疗健康", 20);
    
    for (GeneratedQuery q : queries) {
        SearchResult result = searchService.search(q.getQuery());
        
        // 根据 expectedFocus 自动评测
        for (String focus : q.getExpectedFocus()) {
            RelevanceScore score = evaluator.evaluate(result, focus);
            report.add(persona, focus, score);
        }
    }
}
```

### 场景 2: A/B 测试

```java
// 控制组 vs 实验组，使用相同 Query 集合
List<GeneratedQuery> testQueries = generator.generateBatch(
    "效率实用型妈妈", "百货零食", 100
);

ABTestResult result = abTestRunner.run(
    () -> controlAlgorithm.search(testQueries),
    () -> experimentAlgorithm.search(testQueries)
);
```

### 场景 3: 覆盖率测试

```java
// 确保所有人设和场景组合都被覆盖
for (String persona : generator.getAllPersonaNames()) {
    for (String scene : generator.getAllSceneNames()) {
        List<GeneratedQuery> queries = generator.generateBatch(persona, scene, 5);
        coverageTest.add(persona, scene, queries);
    }
}
```

## 文件结构

```
/Users/linjie/Documents/workspace/skill/query-gen/
├── SKILL.md                 # 技能文档
├── java/
│   ├── QueryGenerator.java      # Java 实现 (旧版本)
│   ├── QueryGeneratorV2.java    # Java 实现 (V2增强版)
│   ├── QueryGenCLI.java         # Java CLI 工具
│   └── QueryGeneratorDemo.java  # 演示程序
└── python/
    ├── query_generator.py   # Python 实现 (V2增强版)
    ├── query_gen_cli.py     # Python CLI 工具
    └── test_demo.py         # 演示程序
```

## 依赖

**Java**:
- 无外部依赖，标准库即可运行

**Python**:
- 无外部依赖，标准库即可 (Python 3.7+)

## 注意事项

1. **Unicode 编码**: 人设名称"潮流探索型 Z 世代"中的"Z 世代"没有空格，使用时请确保完全匹配
2. **推荐使用 API**: 建议通过 `getAllPersonaNames()` 和 `getAllSceneNames()` 获取准确的名称列表
3. **独立版本**: Java 和 Python 实现都是独立的，不依赖任何外部项目

## License

MIT License
