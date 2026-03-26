# Citation & Traceability Directive

> This rule requires AI to explicitly cite the source of design decisions
> when presenting options or generating artifacts. It transforms
> "quality degradation from context loss" into a visible, verifiable signal.

---

## Core Rule

**Every design decision presented to the designer must include a "依据溯源" (Evidence Trace) section.**

If the AI cannot find a citation source in the archive, it must mark it as `[⚠️ 无归档依据]` — this is a signal that context may have been lost during compression or Context Reset.

---

## Phase 3: Interaction Option Presentation

When presenting 1-2 interaction options per scenario, each option must include:

```markdown
### 方案 {A/B}: {方案名称}

{方案描述...}

> **依据溯源**：
> - [InsightCard: {topic_domain}-{n}] {引用的洞察内容}
> - [RoundDecision: scenario-{n}-round-{m}] {引用的约束或交互细节}
> - [confirmed_intent] {引用的原始需求要素}
> - [00-research.md §{章节}] {引用的调研发现}
>
> {如果某个设计决策没有归档依据:}
> - [⚠️ 无归档依据] {决策描述} — 基于 AI 自身判断
```

### Example

```markdown
### 方案 A: 时间线视图

横向时间轴展示会前/会中/会后状态，集成日历 + 议程 + 参会者状态。
空状态使用插画 + 引导文案，首屏限制 5 个模块。

> **依据溯源**：
> - [InsightCard: competitive-1] Notion 空状态用插画+引导文案，好评率 78%
> - [InsightCard: user_pain_points-1] 高频用户偏好键盘快捷键操作
> - [confirmed_intent] 核心目标：提升会前准备效率
> - [⚠️ 无归档依据] 时间轴采用横向布局 — 基于 AI 对日历类产品的理解
```

---

## Phase 4: Design Contract Verification

When the AI synthesizes the Design Contract (`03-design-contract.md`), each
`interaction_commitments` entry must reference its source:

```yaml
interaction_commitments:
  - commitment: "议程项支持拖拽排序"
    source: "RoundDecision: scenario-1-round-2, constraints_added[1]"
  - commitment: "空状态使用插画+引导文案"
    source: "InsightCard: competitive-1, key_insights[0]"
  - commitment: "列表默认按时间倒序"
    source: "[⚠️ 无归档依据] AI inference"
```

---

## Phase 4: High-Fidelity HTML Generation

Before generating `index.html`, the AI must output a brief alignment check:

```markdown
## 生成对齐检查

我将基于以下设计合约生成高保真原型：

| 场景 | 核心交互 | 来源 |
|------|---------|------|
| 会前准备 | 时间线视图 + 拖拽排序 | Design Contract §scenarios[0] |
| 会中协作 | 浮动工具栏 + 悬停展开 | Design Contract §scenarios[1] |
| ... | ... | ... |

全局约束：
- 首屏 ≤ 5 模块 [Design Contract §global_constraints]
- 动效 ≤ 300ms [Design Contract §global_constraints]
- 侧边栏统一导航 [Design Contract §visual_consistency_rules]

确认无误后我开始生成。
```

---

## Why This Matters

1. **Makes context loss visible**: If AI lost important constraints during Context Reset,
   the `[⚠️ 无归档依据]` marker makes it immediately obvious to the designer
2. **Designer can verify without reading archives**: The citation tells the designer
   *where* the decision came from — they can spot-check against their memory
3. **Creates accountability**: AI can't silently make up design decisions — everything
   must either be traced to an archive source or explicitly marked as AI judgment
4. **Recoverable**: When designer spots a `[⚠️ 无归档依据]` on something they
   discussed earlier, they know to use `/recall` to recover the lost context
