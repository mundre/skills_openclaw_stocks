---
name: inventory-reorder-calculator
description: Estimate ecommerce reorder timing and quantity using demand, lead time, and safety stock assumptions. Use when operators need a practical reorder point instead of guesswork.
---

# Inventory Reorder Calculator

补货不是“快没了再下单”，而是提前算出风险和时间窗口。

## 先交互，再计算

开始时先问：
1. 你们现在想算的是：
   - reorder point
   - reorder quantity
   - stockout risk window
   - 大促前备货量
2. 你们平时怎么设 safety stock？
3. lead time 是固定值还是波动区间？
4. 是否要考虑 MOQ、现金约束、季节性或活动影响？
5. 要沿用现有逻辑，还是让我给推荐补货框架？

## Python script guidance

当用户给出结构化数据后：
- 生成 Python 脚本完成补货点 / 补货量计算
- 展示需求、交期、安全库存假设
- 输出风险区间
- 返回可复用脚本

## 解决的问题

很多库存问题不是不会卖，而是：
- 卖太快，断货；
- 下太多，压现金；
- lead time 一波动，计划就失真；
- 没有 safety stock，运营靠感觉补货。

这个 skill 的目标是：
**根据销量、库存、交期和安全库存，算出更稳妥的 reorder point 和建议补货量。**

## 何时使用

- SKU 在快速增长或大促前；
- 供应链 lead time 不稳定；
- 需要在不断货和不压货之间找平衡。

## 输入要求

- 当前库存
- 日均销量 / 周均销量
- 供应商 lead time
- MOQ / 包装倍数
- 安全库存目标
- 可选：季节性、大促、补货周期限制

## 工作流

1. 明确补货逻辑和风险目标。
2. 估算补货周期内需求。
3. 加上安全库存缓冲。
4. 计算 reorder point。
5. 给出建议补货量和风险提示。
6. 返回可复用 Python 脚本。

## 输出格式

1. 假设表
2. Reorder point
3. 建议补货量
4. 风险区间与建议
5. Python 脚本

## 质量标准

- 明确写出交期和需求假设。
- 区分补货点和补货量。
- 能支持日常运营决策，而不是只给公式。
- 对波动风险有提醒。
- 未确认口径前不假装精确。

## 资源

参考 `references/output-template.md`。
