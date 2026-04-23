# 非授权版本识别关键词列表

## 核心关键词

以下关键词用于识别非授权版本商品（如海外版、港版、代购等）。

---

## 默认关键词列表

### 地区版本类
- 海外版
- 港版
- 美版
- 欧版
- 日版
- 韩版
- 英版
- 德版
- 法版
- 澳版

### 购买渠道类
- 代购
- 代下单
- 代买
- 海淘
- 直邮
- 转运
- 跨境
- 跨境电商

### 进口相关类
- 进口
- 原装进口
- 纯进口
- 正品进口
- 保税仓
- 免税
- 自贸区
- 免税店

### 特殊渠道类
- 水货
- 平行进口
- 专柜代购
- 柜台代购
- 专柜货
- 门店代购

---

## 自定义扩展

如需添加新的关键词，修改 `scripts/detect_versions.py` 文件：

```python
VIOLATION_KEYWORDS = [
    # 原有关键词
    '海外版',
    '港版',
    # ...

    # 添加新关键词
    '你的新关键词1',
    '你的新关键词2',
]
```

---

## 关键词匹配规则

### 匹配逻辑
1. **不区分大小写**：关键词匹配时忽略大小写
2. **部分匹配**：商品标题中包含关键词即判定为命中
3. **多关键词**：一个商品可能命中多个关键词，但只记录第一个匹配

### 排除规则（可选）
如需排除某些特殊情况，可在脚本中添加排除逻辑：

```python
# 排除规则示例
EXCLUDED_PATTERNS = [
    '官方进口',
    '旗舰店',  # 官方旗舰店排除
]

def is_excluded(title: str) -> bool:
    """检查是否需要排除"""
    for pattern in EXCLUDED_PATTERNS:
        if pattern.lower() in title.lower():
            return True
    return False

# 在主逻辑中使用
if keyword in title and not is_excluded(title):
    # 标记为非授权
```

---

## 命中示例

### 命中案例
- ✅ "阿莫西林胶囊（海外版）" → 命中"海外版"
- ✅ "香港代购阿莫西林" → 命中"代购"
- ✅ "保税仓发货阿莫西林" → 命中"保税仓"
- ✅ "原装进口阿莫西林" → 命中"进口"

### 未命中案例
- ❌ "阿莫西林胶囊（国产）" → 未命中
- ❌ "官方正品阿莫西林" → 未命中

---

## 注意事项

1. **关键词更新**：根据实际监控情况，定期更新关键词列表
2. **误判处理**：如发现误判，可通过排除规则或人工审核机制处理
3. **关键词分类**：可按地区、渠道等维度分类管理，便于后续分析

---

## 扩展功能（可选）

### 1. 按关键词分类统计

```python
from collections import defaultdict

keyword_stats = defaultdict(int)

for item in unauthorized:
    for keyword in VIOLATION_KEYWORDS:
        if keyword.lower() in item['title'].lower():
            keyword_stats[keyword] += 1
            break

# 输出统计结果
print("非授权类型分布：")
for keyword, count in keyword_stats.items():
    print(f"  {keyword}: {count} 件")
```

### 2. 多关键词匹配

如需记录所有匹配的关键词（不只是第一个），修改检测逻辑：

```python
def detect_unauthorized_multi(data: List[Dict]) -> List[Dict]:
    """检测非授权版本，记录所有匹配关键词"""
    unauthorized = []

    for item in data:
        title = item.get('title', '').lower()
        matched_keywords = []

        for keyword in VIOLATION_KEYWORDS:
            if keyword.lower() in title:
                matched_keywords.append(keyword)

        if matched_keywords:
            unauthorized.append({
                'platform': item.get('platform', ''),
                'shop': item.get('shop', ''),
                'title': item.get('title', ''),
                'reason': f'命中关键词: {", ".join(matched_keywords)}',
                'url': item.get('url', '')
            })

    return unauthorized
```
