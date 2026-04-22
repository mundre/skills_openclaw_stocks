# 组件片段集

每个组件包含 **HTML 结构** 和 **必需的 CSS**。按需复制到 base-template.html 的 `<style>` 段和 `<body>` 段。

---

## 1. Cost Card（月对月数据对比）

### HTML
```html
<div class="cost-hero">
  <div class="cost-card march">
    <div class="cost-card-label">
      <div class="cost-card-month">3 月（全月）</div>
      <div class="cost-card-tag">BASELINE</div>
    </div>
    <div class="cost-card-value">¥26<span class="cost-card-unit">W</span></div>
    <div class="cost-card-note">备注文字</div>
  </div>

  <div class="cost-arrow">
    <div class="cost-arrow-icon">&#10145;</div>
    <div class="cost-arrow-pct">+170%</div>
    <div class="cost-arrow-text">MoM</div>
  </div>

  <div class="cost-card april">
    <div class="cost-card-label">
      <div class="cost-card-month">4 月（截至 21 日）</div>
      <div class="cost-card-tag">超预期</div>
    </div>
    <div class="cost-card-value">¥70<span class="cost-card-unit">W</span></div>
    <div class="cost-card-note">备注文字</div>
  </div>
</div>
```

### CSS
```css
.cost-hero {
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  gap: 24px;
  align-items: stretch;
  margin-bottom: 28px;
}
.cost-card {
  background: rgba(255,255,255,0.03);
  border-radius: 16px;
  border: 1px solid rgba(255,255,255,0.08);
  padding: 28px 32px;
  position: relative;
  overflow: hidden;
}
.cost-card.march { border-color: rgba(100,116,139,0.3); }
.cost-card.april {
  border-color: rgba(239,68,68,0.45);
  background: linear-gradient(135deg, rgba(239,68,68,0.08), rgba(255,255,255,0.03));
  box-shadow: 0 0 30px rgba(239,68,68,0.08);
}
.cost-card-label { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.cost-card-month { font-size: 14px; font-weight: 700; color: #8899bb; letter-spacing: 1px; }
.cost-card.april .cost-card-month { color: #fca5a5; }
.cost-card-tag { font-size: 11px; padding: 3px 10px; border-radius: 4px; font-weight: 600; letter-spacing: 0.5px; }
.cost-card.march .cost-card-tag { background: rgba(100,116,139,0.2); color: #94a3b8; }
.cost-card.april .cost-card-tag { background: rgba(239,68,68,0.2); color: #fca5a5; }
.cost-card-value { font-size: 52px; font-weight: 800; color: #fff; line-height: 1; margin-bottom: 8px; }
.cost-card.april .cost-card-value {
  background: linear-gradient(135deg, #fca5a5, #ef4444);
  -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
}
.cost-card-unit { font-size: 20px; font-weight: 600; color: #7788aa; margin-left: 4px; -webkit-text-fill-color: #7788aa; }
.cost-card-note { font-size: 13px; color: #7788aa; line-height: 1.5; margin-top: 10px; }
.cost-card.april .cost-card-note { color: #fecaca; }
.cost-arrow { display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 8px; min-width: 140px; }
.cost-arrow-icon { font-size: 36px; color: #ef4444; }
.cost-arrow-pct {
  font-size: 28px; font-weight: 800;
  background: linear-gradient(135deg, #fb923c, #ef4444);
  -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
}
.cost-arrow-text { font-size: 12px; color: #8899bb; font-weight: 600; letter-spacing: 1px; text-transform: uppercase; }
```

---

## 2. Budget Banner（预算说明三联格）

### HTML
```html
<div class="budget-banner">
  <div class="budget-item">
    <div class="budget-label">预算已到账</div>
    <div class="budget-value">100<span class="sub">W</span></div>
  </div>
  <div class="budget-item">
    <div class="budget-label">已消耗</div>
    <div class="budget-value">~96<span class="sub">W</span></div>
  </div>
  <div class="budget-item">
    <div class="budget-label">剩余可用</div>
    <div class="budget-value" style="color: #fca5a5;">~4<span class="sub">W</span></div>
  </div>
</div>
```

### CSS
```css
.budget-banner {
  background: linear-gradient(135deg, rgba(167,139,250,0.1), rgba(80,112,255,0.1));
  border: 1px solid rgba(167,139,250,0.3);
  border-radius: 14px;
  padding: 22px 28px;
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 24px;
  margin-bottom: 10px;
}
.budget-item { border-right: 1px solid rgba(167,139,250,0.15); padding-right: 20px; }
.budget-item:last-child { border-right: none; }
.budget-label { font-size: 12px; color: #a0b4ff; font-weight: 600; letter-spacing: 1px; margin-bottom: 6px; text-transform: uppercase; }
.budget-value { font-size: 22px; font-weight: 800; color: #fff; }
.budget-value .sub { font-size: 13px; font-weight: 500; color: #8899bb; margin-left: 6px; }
```

---

## 3. Storyline（故事线卡片，带左侧彩色条）

### HTML
```html
<div class="storylines">
  <div class="storyline storyline-1">
    <div class="storyline-header">
      <div class="storyline-num">1</div>
      <div class="storyline-title">故事线标题</div>
    </div>
    <div class="storyline-path">
      <div class="path-node">节点A</div>
      <div class="path-arrow">&#10140;</div>
      <div class="path-node">节点B</div>
      <div class="path-arrow">&#10140;</div>
      <div class="path-node">节点C</div>
    </div>
    <div class="storyline-desc">
      详细描述，可用 <strong>加粗</strong> 和 <a href="#" style="color:#a78bfa;">链接</a>。
    </div>
  </div>
  <!-- storyline-2、storyline-3 结构相同，class 换成 storyline-2 / storyline-3 -->
</div>
```

### CSS
```css
.storylines { display: flex; flex-direction: column; gap: 24px; }
.storyline {
  background: rgba(255,255,255,0.03);
  border-radius: 16px;
  border: 1px solid rgba(255,255,255,0.06);
  padding: 28px 32px;
  position: relative;
  overflow: hidden;
}
.storyline::before { content: ''; position: absolute; left: 0; top: 0; bottom: 0; width: 4px; }
.storyline-1::before { background: linear-gradient(180deg, #5070ff, #a78bfa); }
.storyline-2::before { background: linear-gradient(180deg, #10b981, #34d399); }
.storyline-3::before { background: linear-gradient(180deg, #f59e0b, #fbbf24); }
.storyline-header { display: flex; align-items: center; gap: 16px; margin-bottom: 14px; }
.storyline-num {
  width: 36px; height: 36px; border-radius: 10px;
  display: flex; align-items: center; justify-content: center;
  font-size: 16px; font-weight: 800; color: #fff;
}
.storyline-1 .storyline-num { background: linear-gradient(135deg, #5070ff, #7c3aed); }
.storyline-2 .storyline-num { background: linear-gradient(135deg, #10b981, #059669); }
.storyline-3 .storyline-num { background: linear-gradient(135deg, #f59e0b, #d97706); }
.storyline-title { font-size: 20px; font-weight: 700; color: #fff; }
.storyline-path { display: flex; align-items: center; gap: 10px; margin-bottom: 14px; flex-wrap: wrap; }
.path-node { padding: 6px 14px; border-radius: 8px; font-size: 13px; font-weight: 600; white-space: nowrap; }
.storyline-1 .path-node { background: rgba(80,112,255,0.12); border: 1px solid rgba(80,112,255,0.25); color: #a0b4ff; }
.storyline-2 .path-node { background: rgba(16,185,129,0.12); border: 1px solid rgba(16,185,129,0.25); color: #6ee7b7; }
.storyline-3 .path-node { background: rgba(245,158,11,0.12); border: 1px solid rgba(245,158,11,0.25); color: #fcd34d; }
.path-arrow { color: #4a5a7a; font-size: 14px; font-weight: 600; }
.storyline-desc { font-size: 14px; color: #8899bb; line-height: 1.7; }
.storyline-desc strong { color: #c0ccee; }
```

---

## 4. Decision Cards（决策卡片 / 方案对比）

### HTML
```html
<div class="decisions">
  <div class="decision-card">
    <div class="decision-icon blue">&#9733;</div>
    <div class="decision-title">决策点标题</div>
    <div class="decision-content">
      决策说明
      <div class="decision-options">
        <div class="option option-a"><div class="option-dot"></div>方案 A：...</div>
        <div class="option option-b"><div class="option-dot"></div>方案 B：...</div>
      </div>
    </div>
  </div>
  <!-- 重复 -->
</div>
```

### CSS
```css
.decisions { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
.decision-card {
  background: rgba(255,255,255,0.03);
  border-radius: 14px;
  border: 1px solid rgba(255,255,255,0.06);
  padding: 24px;
  position: relative;
}
.decision-card.full-width { grid-column: 1 / -1; }
.decision-icon {
  width: 40px; height: 40px; border-radius: 10px;
  display: flex; align-items: center; justify-content: center;
  font-size: 20px; margin-bottom: 14px;
}
.decision-icon.blue   { background: rgba(80,112,255,0.15); }
.decision-icon.purple { background: rgba(124,58,237,0.15); }
.decision-icon.green  { background: rgba(16,185,129,0.15); }
.decision-icon.orange { background: rgba(245,158,11,0.15); }
.decision-title { font-size: 16px; font-weight: 700; color: #fff; margin-bottom: 8px; }
.decision-content { font-size: 13px; color: #8899bb; line-height: 1.7; }
.decision-options { margin-top: 10px; display: flex; flex-direction: column; gap: 6px; }
.option { display: flex; align-items: center; gap: 8px; font-size: 13px; }
.option-a { color: #a0b4ff; }
.option-b { color: #fcd34d; }
.option-dot { width: 6px; height: 6px; border-radius: 50%; flex-shrink: 0; }
.option-a .option-dot { background: #5070ff; }
.option-b .option-dot { background: #f59e0b; }
```

---

## 5. Next Steps（行动项时间轴）

### HTML
```html
<div class="next-steps">
  <div class="step">
    <div class="step-time">4 月底</div>
    <div class="step-content">
      <div class="step-title">要做的事</div>
      <div class="step-desc">描述</div>
      <div class="step-owner">@负责人</div>
    </div>
  </div>
  <!-- 重复 -->
</div>
```

### CSS
```css
.next-steps { display: flex; flex-direction: column; gap: 16px; }
.step {
  display: flex; align-items: flex-start; gap: 18px;
  background: rgba(255,255,255,0.03);
  border-radius: 12px;
  border: 1px solid rgba(255,255,255,0.06);
  padding: 20px 24px;
}
.step-time {
  min-width: 80px;
  padding: 6px 12px;
  border-radius: 8px;
  background: rgba(80,112,255,0.1);
  border: 1px solid rgba(80,112,255,0.2);
  color: #7cacff;
  font-size: 12px;
  font-weight: 600;
  text-align: center;
  white-space: nowrap;
}
.step-content { flex: 1; }
.step-title { font-size: 15px; font-weight: 600; color: #e0e6f0; margin-bottom: 4px; }
.step-desc { font-size: 13px; color: #7788aa; line-height: 1.6; }
.step-owner {
  display: inline-block; padding: 2px 8px; border-radius: 4px;
  background: rgba(167,139,250,0.12); border: 1px solid rgba(167,139,250,0.2);
  color: #c4b5fd; font-size: 11px; font-weight: 600; margin-top: 6px;
}
```

---

## 6. Future Cards（Now / Next 规划对比）

### HTML
```html
<div class="future-cards">
  <div class="future-card now">
    <div class="future-card-tag">现阶段（Q2）</div>
    <div class="future-card-title">标题</div>
    <div class="future-card-desc">描述，可用 <strong>加粗</strong></div>
  </div>
  <div class="future-card next">
    <div class="future-card-tag">下一步（H2 起）</div>
    <div class="future-card-title">标题</div>
    <div class="future-card-desc">描述</div>
  </div>
</div>
```

### CSS
```css
.future-cards { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
.future-card {
  background: rgba(255,255,255,0.03);
  border-radius: 14px;
  border: 1px solid rgba(255,255,255,0.06);
  padding: 24px;
  position: relative;
}
.future-card.now  { border-color: rgba(16,185,129,0.3); }
.future-card.next { border-color: rgba(245,158,11,0.3); }
.future-card-tag {
  display: inline-block; font-size: 11px; font-weight: 700;
  padding: 3px 10px; border-radius: 4px;
  letter-spacing: 1px; margin-bottom: 12px;
}
.future-card.now  .future-card-tag { background: rgba(16,185,129,0.15); color: #6ee7b7; }
.future-card.next .future-card-tag { background: rgba(245,158,11,0.15); color: #fcd34d; }
.future-card-title { font-size: 17px; font-weight: 700; color: #fff; margin-bottom: 10px; }
.future-card-desc { font-size: 13px; color: #8899bb; line-height: 1.7; }
.future-card-desc strong { color: #c0ccee; }
```

---

## 7. Placeholder（内容待补充占位页）

### HTML
```html
<div class="placeholder">
  <div class="placeholder-icon">&#128221;</div>
  <div class="placeholder-title">素材待补充</div>
  <div class="placeholder-desc">
    等 XX 同步内容后填充，包括但不限于：<br><br>
    · <strong style="color:#c0ccee;">要点1</strong><br>
    · <strong style="color:#c0ccee;">要点2</strong>
  </div>
</div>
```

### CSS
```css
.placeholder {
  background: rgba(255,255,255,0.03);
  border: 2px dashed rgba(255,255,255,0.12);
  border-radius: 16px;
  padding: 60px 40px;
  text-align: center;
  margin-bottom: 20px;
}
.placeholder-icon { font-size: 40px; margin-bottom: 16px; opacity: 0.5; }
.placeholder-title { font-size: 20px; font-weight: 700; color: #7788aa; margin-bottom: 10px; }
.placeholder-desc { font-size: 14px; color: #5a6a8a; line-height: 1.7; max-width: 700px; margin: 0 auto; }
```

---

## 8. Metric Table（对比数据表）

结构化对比数据，支持 3 列或 4 列（指标 / 前期 / 当期 / 变化）：

### HTML
```html
<div style="background: rgba(255,255,255,0.025); border-radius: 14px; border: 1px solid rgba(255,255,255,0.06); padding: 20px 28px;">
  <!-- 表头 -->
  <div style="display: grid; grid-template-columns: 1.4fr 1fr 1fr 0.9fr; gap: 20px; padding-bottom: 12px; border-bottom: 1px solid rgba(255,255,255,0.08); font-size: 12px; color: #7788aa; font-weight: 700; letter-spacing: 1px; text-transform: uppercase;">
    <div>指标</div>
    <div style="text-align: right;">前期</div>
    <div style="text-align: right; color: #c4b5fd;">当期</div>
    <div style="text-align: right;">变化</div>
  </div>
  <!-- 数据行 -->
  <div style="display: grid; grid-template-columns: 1.4fr 1fr 1fr 0.9fr; gap: 20px; padding: 12px 0; border-bottom: 1px solid rgba(255,255,255,0.04); align-items: center;">
    <div style="font-size: 14px; font-weight: 600; color: #c0ccee;">模型成本</div>
    <div style="text-align: right; font-size: 16px; font-weight: 700; color: #c0ccee;">¥26.1 W</div>
    <div style="text-align: right; font-size: 16px; font-weight: 800; color: #fff;">¥70.5 W</div>
    <div style="text-align: right; font-size: 13px; font-weight: 700; color: #ef4444;">↑ +170%</div>
  </div>
  <!-- 更多行 -->
</div>
```

---

## 9. Budget Timeline（预算预估条）

用于多月预算预估 + 总计申请。

### HTML
```html
<div style="background: rgba(255,255,255,0.025); border-radius: 14px; border: 1px solid rgba(239,68,68,0.2); padding: 20px 28px;">
  <div style="display: grid; grid-template-columns: repeat(5, 1fr) auto; gap: 10px; align-items: stretch;">
    <div style="background: rgba(100,116,139,0.08); border-radius: 10px; padding: 14px 12px; text-align: center; border: 1px solid rgba(100,116,139,0.2);">
      <div style="font-size: 11px; color: #94a3b8; margin-bottom: 6px;">3 月（已发生）</div>
      <div style="font-size: 22px; font-weight: 800; color: #e0e6f0;">26<span style="font-size:12px;color:#7788aa;">W</span></div>
    </div>
    <!-- ... 重复 4 个月 ... -->
    <div style="background: linear-gradient(135deg, rgba(16,185,129,0.12), rgba(52,211,153,0.06)); border-radius: 10px; padding: 14px 16px; text-align: center; border: 1px solid rgba(16,185,129,0.3); min-width: 140px; display: flex; flex-direction: column; justify-content: center;">
      <div style="font-size: 11px; color: #6ee7b7; margin-bottom: 6px; font-weight: 600;">待申请预算</div>
      <div style="font-size: 26px; font-weight: 900; color: #10b981;">355<span style="font-size:13px;color:#6ee7b7;">W</span></div>
    </div>
  </div>
  <div style="display: flex; margin-top: 14px; padding-top: 14px; border-top: 1px solid rgba(255,255,255,0.06); font-size: 12px; color: #7788aa;">
    3~7 月合计 <strong style="color:#fff;">~481W</strong> − 已到账 <strong style="color:#fff;">100W</strong> = 待申请 <strong style="color:#10b981;">~355W</strong>
  </div>
</div>
```

---

## 10. Conclusion Banner（结论横幅）

用于页底的核心结论强调。

### HTML
```html
<div class="attr-conclusion">
  <div class="attr-conclusion-icon">&#9881;</div>
  <div class="attr-conclusion-text">
    <strong>核心结论</strong>放这里，可以在关键数字上 <strong>加粗</strong>。
  </div>
</div>
```

### CSS
```css
.attr-conclusion {
  background: linear-gradient(135deg, rgba(167,139,250,0.12), rgba(80,112,255,0.12));
  border: 1px solid rgba(167,139,250,0.3);
  border-radius: 14px;
  padding: 24px 28px;
  display: flex;
  align-items: center;
  gap: 24px;
}
.attr-conclusion-icon { font-size: 36px; color: #a78bfa; line-height: 1; }
.attr-conclusion-text { font-size: 17px; font-weight: 600; color: #fff; line-height: 1.6; }
.attr-conclusion-text strong { color: #c4b5fd; font-weight: 800; }
```

---

## 11. SVG 架构图

完整架构图见 `examples/report.html` slide 2，详细规则见 `references/svg-architecture-rules.md`。
