# Java 和 Python 实现功能一致性说明

## 功能对比

| 功能维度 | Java | Python | 状态 |
|---------|------|--------|------|
| **8 种人设** | ✅ | ✅ | 一致 |
| **9 大场景** | ✅ | ✅ | 一致 |
| **品牌库** | ✅ | ✅ | 一致 |
| **规格库** | ✅ | ✅ | 一致 |
| **价格范围** | ✅ | ✅ | 一致 |
| **地理位置** | ✅ | ✅ | 一致 |
| **配送要求** | ✅ | ✅ | 一致 |
| **情境描述** | ✅ | ✅ | 一致 |
| **CLI 工具** | ✅ | ✅ | 一致 |
| **HTTP API** | ✅ | ✅ | 一致 |

## 概率参数（已统一）

| 维度 | 默认概率 | P004(价格敏感) | P003(品质追求) |
|------|----------|---------------|---------------|
| **品牌** | 90% | 90% | 90% |
| **规格** | 70% | 70% | 70% |
| **位置** | 80% | 80% | 80% |
| **配送** | 60% | 60% | 60% |
| **价格** | 50% | 80% | 40% |

## 数据一致性

### 母婴用品 - 品牌定义
```java
// Java
babyBrands.put("奶粉", Arrays.asList("飞鹤", "美赞臣", "惠氏", "雅培", 
                                     "贝因美", "爱他美", "雀巢", "伊利"));
babyBrands.put("纸尿裤", Arrays.asList("花王", "帮宝适", "好奇", 
                                       "尤妮佳", "大王"));
```

```python
# Python
{
    "奶粉": ["飞鹤", "美赞臣", "惠氏", "雅培", "贝因美", "爱他美", "雀巢", "伊利"],
    "纸尿裤": ["花王", "帮宝适", "好奇", "尤妮佳", "大王"]
}
```

### 母婴用品 - 规格定义
```java
// Java
babySpecs.put("奶粉", Arrays.asList("1段", "2段", "3段", "羊奶", "有机", "水解蛋白"));
babySpecs.put("纸尿裤", Arrays.asList("NB码", "S码", "M码", "L码", 
                                      "拉拉裤", "超薄透气", "夜用"));
```

```python
# Python
{
    "奶粉": ["1段", "2段", "3段", "羊奶", "有机", "水解蛋白"],
    "纸尿裤": ["NB码", "S码", "M码", "L码", "拉拉裤", "超薄透气", "夜用"]
}
```

## 生成示例对比

### Java 输出
```
1. 找性价比高的分体童装 5 公里内，要求次日达
   [品牌:英氏 规格:分体 价格:性价比高的 位置:5 公里内 配送:次日达]
   
2. 小孩拉肚子，找超薄透气纸尿裤 3 公里内，要求 1 小时达
   [品牌:尤妮佳 规格:超薄透气 价格:- 位置:3 公里内 配送:1 小时达]
```

### Python 输出
```
1. 孩子咳嗽，想买 100 元以内咬胶玩具 3 公里内，要求小时达
   [品牌:费雪 规格:咬胶 价格:100 元以内 位置:3 公里内 配送:小时达]
   
2. 想买花王的性价比高的夜用纸尿裤 10 公里内，要求 1 小时达
   [品牌:花王 规格:夜用 价格:性价比高的 位置:10 公里内 配送:1 小时达]
```

## 调用方式对比

### CLI 调用

**Java:**
```bash
cd /Users/linjie/Documents/workspace/skill/query-gen/java
java QueryGenCLI -p "新手焦虑型妈妈" -s "母婴用品" -c 10
```

**Python:**
```bash
cd /Users/linjie/Documents/workspace/skill/query-gen/python
python3 query_gen_cli.py -p "新手焦虑型妈妈" -s "母婴用品" -c 10
```

### HTTP API 调用

**Java:**
```bash
java QueryGenHttpServer 5000
curl -X POST http://localhost:5000/generate \
  -H "Content-Type: application/json" \
  -d '{"persona":"新手焦虑型妈妈","scene":"母婴用品","count":10}'
```

**Python:**
```bash
python3 api_server.py --port 5000
curl -X POST http://localhost:5000/generate \
  -H "Content-Type: application/json" \
  -d '{"persona":"新手焦虑型妈妈","scene":"母婴用品","count":10}'
```

## 更新记录

### 2024-04-01 - 功能统一更新

1. **统一概率参数**
   - 品牌：70% → 90%
   - 位置：50% → 80%
   - 配送：30% → 60%
   - 价格：30% → 50% (P004: 60% → 80%)

2. **修复 Java 规格数据**
   - Java 版本正确传入 babySpecs
   - 确保规格信息正常出现在 query 中

3. **完善响应格式**
   - Java HTTP API 添加 context 字段
   - 包含 brand, spec, priceRange, location, delivery 等完整信息

## 测试验证

运行以下命令验证功能一致性：

```bash
# Java 测试
cd java && javac QueryGeneratorV2.java QueryGenHttpServer.java
java QueryGenHttpServer 5019 &
curl -X POST http://localhost:5019/generate \
  -H "Content-Type: application/json" \
  -d '{"persona":"新手焦虑型妈妈","scene":"母婴用品","count":10}'

# Python 测试
cd python && python3 query_gen_cli.py -p "新手焦虑型妈妈" -s "母婴用品" -c 10
```

两个版本应生成质量相当、信息丰富的 query。
