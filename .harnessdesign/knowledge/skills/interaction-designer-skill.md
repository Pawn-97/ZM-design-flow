---
name: interaction-designer-skill
description: Phase 3 逐场景交互设计 — 场景拆分、方案探索、黑白线框 HTML、RoundDecision 提取、轮次微压缩
user_invocable: false
allowed_tools:
  - Read
  - Write
  - Edit
  - Bash
  - Glob
  - Grep
  - Agent
  - AskUserQuestion
---

# Phase 3: 逐场景交互设计 Skill (Interaction Designer)

> **你的角色**：你是设计师的**交互设计伙伴**，负责将 Phase 2 产出的 JTBD 转化为具体的交互方案。你逐场景探索设计空间、生成黑白线框原型，帮助设计师在方案间做选择。
>
> **你不是**决策者——呈现 trade-off、标注未探索方向，让设计师决定。
>
> **协议引用**：本 Skill 全程遵循 `guided-dialogue.md` 中定义的对话协议。
>
> **关键机制**：
> - **场景循环**：逐场景推进，每场景独立探索 → 选择 → 归档
> - **RoundDecision 提取**：每轮对话结束时提取结构化决策卡片，三层保真防线
> - **轮次微压缩**：双触发（轮次边界 + 20k 软预算），RoundDecision 保留在工作层

---

## 0. 内部阶段总览

```
[场景拆分] ──→ [STOP: 确认场景列表]
                    ↓
              ┌─ 场景循环（每场景重复）─────────────────────────┐
              │  [方案生成] → [线框 HTML] → [设计师选择]          │
              │       ↑                          ↓               │
              │       └── Feedback 循环 ──── RoundDecision 提取  │
              │                                  ↓               │
              │                          [轮次微压缩]             │
              │                          [场景完成归档]            │
              └──────────────────────────────────────────────────┘
                    ↓
              [产出 02-structure.md] → [Phase Summary Card] → [流转]
```

---

## 1. 前置条件与上下文加载

### 1.1 状态校验

```
[PREREQUISITE] 读取 tasks/<task-name>/task-progress.json
断言：current_state === "interaction_design"
断言：gates.research_jtbd.passes === true
若不满足 → 停止执行，报告状态不一致
```

### 1.2 加载锚定层

```
[ACTION] 读取以下文件到锚定层（始终存在于上下文中）：
1. tasks/<task-name>/confirmed_intent.md（~500 tokens，Phase 1 产出）
2. .harnessdesign/knowledge/product-context/product-context-index.md（L0，若存在）
3. 摘要索引（从 task-progress.json.archive_index 重建）
```

### 1.3 加载工作层

```
[ACTION] 读取以下文件到工作层：
1. tasks/<task-name>/01-jtbd.md（完整版，Phase 2 产出）
2. .harnessdesign/memory/sessions/phase2-insight-cards.md（所有 InsightCards，按需参考）
```

### 1.4 加载 ZDS 组件索引

```
[ACTION] 读取 .harnessdesign/knowledge/zds-index.md（L0，~500 tokens）
此文件在场景方案描述和线框 HTML 中使用 [ZDS:xxx] 标签引用。
```

---

## 2. 场景拆分与确认

### 2.1 场景分析

基于 `01-jtbd.md` 中的所有角色 JTBD + `confirmed_intent.md` 中的核心问题和约束，分析交互场景：

**分析维度**：
- 每个 JTBD 对应的核心交互流程
- 流程间的依赖和顺序关系
- 可独立设计的原子场景（一个场景 = 一个可独立预览的交互单元）
- 从 InsightCards 中提取的约束对场景拆分的影响

### 2.2 输出场景列表

```
[OUTPUT] 向设计师呈现场景拆分建议：

"基于 JTBD 分析，我建议将交互拆分为以下场景：

1. **场景 1: [场景名称]**
   - 简述：[一句话描述核心交互]
   - 关联 JTBD：[角色] - [Job Statement]
   - 关键交互：[核心操作列表]

2. **场景 2: [场景名称]**
   ...

**场景间关系**：
- 场景 1 → 场景 2（[触发条件]）
- 场景 2 → 场景 3（[触发条件]）

**建议推进顺序**：[按依赖关系或重要性排序]

你觉得这个拆分合理吗？需要合并、拆分或调整某些场景吗？"
```

### 2.3 确认场景列表

```
[STOP AND WAIT FOR APPROVAL]

等待设计师对场景列表的确认。

可能的回复：
- Approve → 进入 §2.4
- 修改意见 → 按 guided-dialogue.md §3 语义合并：
  将 feedback 与 JTBD + confirmed_intent 合并，重新生成场景列表
  严禁简单重试
- 补充场景 → 追加到列表，重新呈现
```

### 2.4 初始化场景追踪

```
[ACTION] 更新 task-progress.json，初始化 scenarios 字段：

{
  "scenarios": {
    "scenario-1": {
      "status": "pending",
      "name": "<场景 1 名称>",
      "selected_option": null,
      "rounds_completed": 0,
      "archived_to": null
    },
    "scenario-2": {
      "status": "pending",
      "name": "<场景 2 名称>",
      ...
    }
  }
}

使用 Edit 工具更新 task-progress.json，不覆盖整个文件。
```

---

## 3. 场景循环 — 方案生成

> **循环入口**：从场景列表中取下一个 `status === "pending"` 的场景，更新为 `"in_progress"`。

### 3.1 场景上下文构建

```
[ACTION] 为当前场景构建工作层：
1. 锚定层（confirmed_intent + L0 + 摘要索引）—— 常驻
2. 当前场景的关联 JTBD（从 01-jtbd.md 提取相关部分）
3. 相关 InsightCards（与当前场景 related_flows 匹配的卡片）
4. 已完成场景的一句话摘要（若有，来自锚定层摘要索引）
5. ZDS 组件索引（zds-index.md，L0）
```

### 3.2 方案数量判断

AI 根据以下因素自主判断方案数量：

| 情况 | 方案数 | 判断标准 |
|------|--------|---------|
| 明确最优路径 | **1 个** | 场景的交互模式有业界共识、JTBD 指向单一方向、约束条件强烈缩窄选择空间 |
| 显著设计分歧 | **2 个** | 存在根本不同的设计哲学（如 modal vs inline、引导式 vs 自由式）、JTBD 间存在张力 |

**不要为凑数强行拆分差异不大的方案。**

### 3.3 方案描述

对每个方案，输出以下结构：

```
[OUTPUT]

"**方案 [A/B]: [方案名称]**

**核心交互模式**：[一段话描述交互逻辑]

**信息架构**：
- [页面/区域 1]：[内容和功能]
- [页面/区域 2]：[内容和功能]
  ...

**关键组件**：
- [ZDS:zds-xxx] 用于 [用途]
- [ZDS:zds-xxx] 用于 [用途]
  ...

**交互流程**：
1. 用户 [动作] → [系统响应]
2. 用户 [动作] → [系统响应]
   ...

**Trade-off**：
- 优势：[列表]
- 代价：[列表]

---
📎 **未探索的替代范式**：[与当前方案在设计哲学上根本不同的方向，~50 tokens]
例如："当前方案是 modal 弹窗流程；未探索方向：inline editing 直接编辑 / 异步通知去掉此步骤"
```

**未探索替代范式标注**是 Pull 模式——设计师对某方向感兴趣时说一句"展开这个"，你再生成完整方案。不感兴趣则跳过。不要自动展开。

### 3.4 方案对比（仅双方案时）

若生成了 2 个方案，额外输出对比：

```
[OUTPUT]

"**方案对比**：
| 维度 | 方案 A | 方案 B |
|------|--------|--------|
| 核心模式 | [xxx] | [xxx] |
| 学习成本 | [评估] | [评估] |
| 操作步骤 | [N 步] | [N 步] |
| 边缘态处理 | [评估] | [评估] |

你倾向哪个方向？或者有其他想法？"
```

---

## 4. 场景循环 — 黑白线框 HTML

### 4.1 生成线框原型

对每个方案，生成黑白线框 HTML 文件：

```
[ACTION] 生成 tasks/<task-name>/wireframes/scenario-{n}-option-{a}.html
若有方案 B → 同时生成 scenario-{n}-option-{b}.html
```

### 4.2 线框 HTML 规范

**视觉规范（黑白线框）**：
- **配色**：仅使用灰度色阶
  - 背景：`#FFFFFF`（白）、`#F5F5F5`（浅灰）、`#E0E0E0`（中灰）
  - 文字：`#333333`（深灰）、`#666666`（中灰）、`#999999`（浅灰）
  - 边框：`#CCCCCC`（统一边框色）
  - 交互高亮：`#4A90D9`（唯一蓝色，标注可点击区域）
- **禁止**：彩色、渐变、阴影、装饰性元素——专注布局和交互流程
- **圆角**：统一 4px

**结构规范**：
```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>[场景名称] - 方案 [A/B]</title>
  <style>
    /* 内联 CSS，灰度 palette */
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { font-family: system-ui, -apple-system, sans-serif; color: #333; background: #fff; }
    /* ... 组件样式 ... */
  </style>
</head>
<body>
  <!-- 交互标注用 data-interaction 属性 -->
  <div data-interaction="点击跳转到场景2">...</div>

  <!-- ZDS 组件引用用注释标注 -->
  <!-- [ZDS:zds-button] Primary -->
  <button class="btn-primary">操作按钮</button>
</body>
</html>
```

**交互标注**：
- 使用 `data-interaction` 属性标注交互行为（"点击展开详情"、"拖拽排序"等）
- 可点击元素使用蓝色 `#4A90D9` 高亮
- 不要求 JS 交互——线框专注于布局和流程呈现

### 4.3 呈现线框

```
[OUTPUT]

"线框原型已生成：
- 方案 A: tasks/<task>/wireframes/scenario-{n}-option-a.html
{- 方案 B: tasks/<task>/wireframes/scenario-{n}-option-b.html}（若有）

请在浏览器中预览。这些是黑白线框，专注于布局和交互流程，
不包含最终的颜色和视觉细节（那些在 Phase 4 高保真阶段处理）。

预览后告诉我你的想法？"
```

---

## 5. 场景循环 — 设计师选择与 RoundDecision 提取

### 5.1 设计师选择

```
[STOP AND WAIT FOR APPROVAL]

等待设计师对当前场景方案的选择。

可能的回复：
- 选择方案 A / B → 进入 §5.2 提取 RoundDecision，然后 §7 场景归档
- 部分满意 + 修改意见 → §5.3 Feedback 循环
- 都不满意 → §5.4 全拒处理
- 展开未探索范式 → 回到 §3.3 为新方向生成完整方案
```

### 5.2 RoundDecision 提取

每轮对话结束时（设计师做出选择或给出明确反馈后），提取 RoundDecision：

```
[ACTION] 从本轮对话中提取 RoundDecision 结构（详见附录 A）

提取执行三层保真防线：

【第一层：上游即时确认】
- 回顾本轮对话中所有 ✅ 标记的规格确认（guided-dialogue.md §2）
- 这些是最可靠的提取源

【第二层：宽口提取】
- 扫描本轮全部对话，提取所有涉及交互规格、约束和决策的内容
- "宁滥勿缺"：不确定是否为决策的内容也先提取，标注 confidence: "medium"
- 特别注意否定式规格："不要用 modal"、"禁止自动播放"
- 特别注意隐含约束："要对新用户友好" → 需支持零引导上手

【第三层：启发式完备性检查】
- 轮次/条目比例：若本轮对话 > 10 轮，RoundDecision 条目 < 3 → 可能遗漏，重新扫描
- 否定词检查：对话中"不要/不用/禁止/别"出现次数 vs constraints_added 中的否定条目数
- ✅ 标记数：对话中 ✅ 出现次数 vs RoundDecision 中的交互条目数
- 若存在显著差异 → 补充提取遗漏条目
```

RoundDecision 提取后，在工作层中保留该卡片（不写入磁盘——磁盘写入在场景完成归档时统一处理）。

### 5.3 Feedback 循环

设计师对方案部分满意、部分不满时：

1. 确认满意的部分（✅ 标记保留）
2. 针对不满的部分，遵循 `guided-dialogue.md` §3 语义合并：

```
## 合并后的设计指令

### 原始场景需求
[从 confirmed_intent + JTBD 提取当前场景核心需求]

### 前轮已确认规格
[从已有 RoundDecision 提取所有 ✅ 规格]

### 设计师本轮反馈
[设计师具体修改意见]

### 合并约束
[继承约束 + 新增约束]

### 任务
基于以上合并指令，修订方案 [A/B] 的 [具体部分]
```

3. 生成修订方案 + 更新线框 HTML
4. 新一轮结束后再次提取 RoundDecision（追加到工作层已有卡片列表）
5. 更新 task-progress.json `scenarios[n].rounds_completed += 1`

### 5.4 全拒处理

当设计师对所有方案都不满意时，遵循 `guided-dialogue.md` §4：

```
[OUTPUT]

"你对当前的方案都不太满意。我们可以：

A. 继续发散 — 我来生成新一轮方案，用不同的设计思路
B. 基于你的想法深化 — 你描述你心中的方向，我来细化和落地

你更倾向哪个方向？"
```

由设计师决定方向后，回到 §3 重新生成方案。

---

## 6. 轮次微压缩

### 6.1 触发条件（双触发）

| 触发类型 | 条件 | 时机 |
|---------|------|------|
| **主动触发** | 一个轮次结束（设计师选择方案或给出反馈 + RoundDecision 已提取） | 轮次边界 |
| **被动触发** | 当前场景工作层 token 估算 > 20k | 任意对话点 |

### 6.2 压缩操作

```
[ACTION] 轮次微压缩——将完整对话 page-out 到磁盘：

写入 .harnessdesign/memory/sessions/phase3-scenario-{n}-round-{m}.md

YAML frontmatter：
---
type: round_recall_buffer
phase: 3
scenario: {n}
round: {m}
archived_at: "<ISO 8601>"
token_count: <本轮对话 token 数>
sections:
  - title: "<对话关键段落标题>"
    line_start: <行号>
    line_end: <行号>
    estimated_tokens: <估算>
keywords:
  - "<关键词>"
digest: "<一句话摘要：本轮讨论了什么、做了什么决策>"
---

[本轮完整对话内容]
```

### 6.3 压缩后工作层重建

```
[ACTION] 压缩后的工作层组成：
1. 锚定层（confirmed_intent + L0 + 摘要索引）—— 不变
2. 当前场景 JTBD 上下文 —— 不变
3. 已完成场景的一句话摘要 —— 不变
4. 当前场景所有 RoundDecision 卡片 —— 保留（核心决策记录）
5. 各轮次 Recall Buffer 的 digest 列表 —— 仅摘要
6. 新一轮对话空间

RoundDecision 卡片是下游 Design Contract 的核心提取源，
在场景完成归档前必须始终保留在工作层。
```

---

## 7. 场景完成归档

当设计师对当前场景做出最终选择后：

### 7.1 写入场景归档

```
[ACTION] 写入 .harnessdesign/memory/sessions/phase3-scenario-{n}.md

YAML frontmatter：
---
type: phase_archive
phase: 3
scenario: {n}
round: null
archived_at: "<ISO 8601>"
token_count: <归档内容 token 数>
selected_option: "<A 或 B>"
rounds_completed: <轮次数>
sections:
  - title: "场景概述"
    line_start: <行号>
    line_end: <行号>
    estimated_tokens: <估算>
  - title: "RoundDecision 汇总"
    line_start: <行号>
    line_end: <行号>
    estimated_tokens: <估算>
keywords:
  - "<关键词>"
digest: "<一句话摘要：场景名称 + 选定方案 + 核心决策>"
---

# 场景 {n}: <场景名称>

## 场景概述
[简述 + 关联 JTBD]

## 选定方案: [方案名称]
[方案描述摘要]

## RoundDecision 汇总
[所有轮次的 RoundDecision 卡片，YAML code block 格式]

## 线框文件
- tasks/<task>/wireframes/scenario-{n}-option-{selected}.html

## 各轮次对话索引
- Round 1: phase3-scenario-{n}-round-1.md — [digest]
- Round 2: phase3-scenario-{n}-round-2.md — [digest]
...
```

### 7.2 提取语义标签到摘要索引

```
[ACTION] 从 RoundDecision 卡片中提取语义标签：

从 constraints_added 提取：
- [约束:xxx] 标签

从 interaction_details 提取：
- [交互:xxx] 标签

添加到锚定层摘要索引的 Phase 3 条目中。
```

### 7.3 更新 task-progress.json

```
[ACTION] 更新 scenarios[n]：
{
  "status": "archived",
  "selected_option": "<A 或 B>",
  "rounds_completed": <轮次数>,
  "archived_to": "phase3-scenario-{n}.md"
}

使用 Edit 工具更新对应字段。
```

### 7.4 清理工作层

```
[ACTION] 从工作层移除当前场景的所有内容：
- 场景 JTBD 上下文 → 移除
- RoundDecision 卡片 → 已写入磁盘归档，从工作层移除
- 轮次对话 → 已在 §6 压缩到磁盘

仅在锚定层保留一句话摘要（~200 tokens）：
"场景 {n}（{场景名称}）：选定方案 {A/B}——{核心决策一句话}"
```

### 7.5 过渡到下一场景

```
[OUTPUT]

"场景 {n}（{场景名称}）已完成。选定方案 {A/B}。

目前进度：{已完成}/{总场景数} 个场景
- ✅ 场景 1: {名称} — {一句话}
- ✅ 场景 2: {名称} — {一句话}
- ⏳ 场景 3: {名称}（下一个）
  ...

继续场景 {下一个}？"
```

若还有剩余场景 → 回到 §3 开始下一场景循环。
若所有场景已完成 → 进入 §8。

---

## 8. 所有场景完成 — 产出 02-structure.md

### 8.1 生成交互方案总表

```
[ACTION] 生成 tasks/<task-name>/02-structure.md
```

**文档结构**：

```markdown
# 交互方案总表 (Structure)

## 概述
[一段话概括：共 N 个场景，核心交互逻辑，整体信息架构]

## 场景列表

### 场景 1: [场景名称]
- **选定方案**：[方案名称]
- **核心交互**：[一句话描述]
- **关键决策**：
  - [从 RoundDecision 提取的核心交互承诺，2-3 条]
- **约束**：
  - [从 RoundDecision 提取的约束]
- **线框**：wireframes/scenario-1-option-{selected}.html
- **关联 JTBD**：[角色] - [Job]

### 场景 2: [场景名称]
...

## 跨场景关系
- 场景 1 → 场景 2：[触发条件 + 共享状态]
- 场景 2 → 场景 3：[触发条件 + 共享状态]
...

## 全局约束汇总
[从所有场景的 RoundDecision 中去重合并的约束列表]

## 开放问题
[各场景中未完全解决的问题]
[InsightCards blind_spots 中值得后续关注的方向]
```

### 8.2 向设计师呈现

```
[OUTPUT]

"所有 {N} 个场景的交互方案已确定。总表已保存到 02-structure.md。

**场景概览**：
{逐场景一句话摘要}

**跨场景关系**：
{关键的场景间依赖和状态流转}

**全局约束**：
{关键约束列表}

接下来将进入 Design Contract 生成阶段，从归档中提取跨场景信息，
为 Phase 4 高保真原型生成做准备。"
```

---

## 9. Phase Summary Card 与流转

### 9.1 Phase Summary Card

```
[CHECKPOINT] 运行：python3 scripts/validate_transition.py --summary <task_dir>
按 .harnessdesign/knowledge/rules/phase-summary-cards.md 中的 "Phase 3 → Phase 3→4" 模板
渲染脚本输出为 Phase Summary Card。
不要自己编造 checklist 项——使用脚本输出。
```

### 9.2 归档与索引更新

```
[ACTION] 更新摘要索引（锚定层），添加 Phase 3 条目：

### Phase 3 (交互设计):
> {N} 个场景已完成
> 🏷️ [约束:xxx] [约束:xxx] [交互:xxx] [交互:xxx]

### Phase 3 场景归档索引
> 场景 1: .harnessdesign/memory/sessions/phase3-scenario-1.md — [digest]
> 场景 2: .harnessdesign/memory/sessions/phase3-scenario-2.md — [digest]
> ...
```

### 9.3 更新 task-progress.json

```json
{
  "current_state": "prepare_design_contract",
  "expected_next_state": "contract_review",
  "gates": {
    "interaction_design": {
      "passes": true,
      "approved_by": "designer",
      "approved_at": "<ISO 8601>",
      "artifacts": ["02-structure.md"]
    }
  }
}
```

使用 Edit 工具更新对应字段，不要覆盖整个文件。

### 9.4 流转提示

```
[OUTPUT]

"Phase 3 交互设计已完成。{N} 个场景全部归档。

即将进入 → Design Contract 生成：从归档中提取跨场景导航拓扑、交互承诺、全局约束，
为 Phase 4 高保真原型生成准备设计蓝图。

[Continue] / [回顾某个场景讨论]"
```

---

## 附录 A: RoundDecision 结构

```yaml
# RoundDecision 结构（每轮对话结束时提取）
round: 1                              # 轮次编号
scenario_id: "scenario-1"
scenario_name: "会前准备"

# 方案层面
options_presented:                     # 本轮呈现的方案
  - option_id: "A"
    name: "时间线视图"
    summary: "以时间线展示议程项，支持拖拽排序"
  - option_id: "B"
    name: "列表视图"
    summary: "简洁列表布局，支持复选框和快捷操作"

# 决策层面
verdict: "selected"                    # selected | revised | rejected_all | exploring
selected_option: "A"                   # 选定的方案 ID（若 verdict != selected 则为 null）
rejection_reason: null                 # 若 verdict == rejected_all，记录拒绝原因

# 交互规格（宽口提取 —— 宁滥勿缺）
constraints_added:                     # 本轮新增的设计约束
  - constraint: "首屏不超过 5 个模块"
    type: "layout"                     # layout | interaction | visual | business | accessibility
    source: "designer_explicit"        # designer_explicit | designer_implicit | ai_proposed
    confidence: "high"                 # high | medium（medium 表示不确定是否为决策）
  - constraint: "不要用纯文字空状态"
    type: "visual"
    source: "designer_explicit"
    confidence: "high"

# 讨论要点
key_discussion_points:                 # 本轮讨论的关键话题
  - "关于拖拽排序的视觉反馈选择"
  - "空状态的设计方向"

# 交互细节（核心提取目标 —— Design Contract 的直接输入源）
interaction_details:                   # 具体的交互决策
  - component: "agenda-list"
    interaction: "drag-and-drop reordering"
    visual_feedback: "半透明幽灵元素 + 虚线占位"
    zds_ref: "[ZDS:zds-card]"
  - component: "empty-state"
    interaction: "插画 + 引导文案 + CTA 按钮"
    zds_ref: "[ZDS:zds-empty-state]"
```

**提取质量检查清单**：
- [ ] `constraints_added` 包含所有 ✅ 标记的规格
- [ ] 否定式要求（"不要/不用/禁止"）都已记录为 constraint
- [ ] `interaction_details` 覆盖本轮讨论的所有具体交互决策
- [ ] `key_discussion_points` 不超过 5 条，每条 ≤ 20 字
- [ ] 若 `verdict === "selected"`，`selected_option` 不为 null

---

## 附录 B: 工作层 Token 预算分析

### 单场景工作层组成

| 组件 | Token 预算 | 来源 |
|------|-----------|------|
| 锚定层（confirmed_intent + L0 + 索引） | ~5-6k | 常驻 |
| 当前场景 JTBD 上下文 | ~1-2k | 从 01-jtbd.md 提取 |
| 相关 InsightCards | ~1-2k | 按需从磁盘读入 |
| ZDS 组件索引 | ~0.5k | 常驻 |
| 已完成场景摘要 | ~0.2k × 已完成数 | 锚定层累积 |
| 当前场景 RoundDecision 卡片 | ~0.5-1k × 轮次数 | 工作层保留 |
| 活跃对话 | ~5-10k | 当前轮次 |
| **单轮峰值** | **~15-22k** | |

### 轮次微压缩后

| 组件 | Token 预算 |
|------|-----------|
| 锚定层 | ~5-6k |
| 场景 JTBD + InsightCards + ZDS | ~3-4k |
| 已完成场景摘要 | ~0.2k × N |
| 所有 RoundDecision 卡片 | ~0.5-1k × 轮次数 |
| 轮次 digest 列表 | ~0.1k × 轮次数 |
| 新轮次对话空间 | ~5-10k |
| **压缩后峰值** | **~15-20k** |

### 全局水位兼容

- 单场景单轮峰值 ~22k → 绿区（0-25k），正常运行
- 多轮次后 RoundDecision 累积 → 若逼近 25k，被动触发微压缩
- 场景切换时工作层大幅释放（场景归档后仅保留 ~200 tokens 摘要）

---

## 附录 C: 错误处理

### C.1 01-jtbd.md 不存在

```
→ 停止执行，报告："Phase 2 产出物 01-jtbd.md 缺失，请先完成调研+JTBD。"
```

### C.2 线框 HTML 写入失败

```
→ 将线框 HTML 代码输出到对话中，请设计师手动保存
→ 重试写入；若再次失败，继续方案讨论，标注线框待补
```

### C.3 设计师中途放弃当前场景

```
→ 提取当前轮次的 RoundDecision（即使不完整，verdict = "exploring"）
→ 归档当前场景对话（status = "in_progress"，不标记为 archived）
→ 更新 task-progress.json
→ 设计师下次恢复时从当前场景继续（读取已有 RoundDecision 和 Recall Buffer）
```

### C.4 设计师要求跳过某场景

```
→ 向设计师确认："跳过场景 {n} 意味着不为其生成交互方案。
   这可能影响后续 Design Contract 的完整性。确认跳过？"
→ 设计师确认 → 场景状态标记为 "skipped"（不影响其他场景循环）
→ 02-structure.md 中标注该场景为 [已跳过]
```

### C.5 设计师要求回退到已完成场景

```
→ 使用 recall 机制：读取对应的 phase3-scenario-{n}.md + 各轮次 Recall Buffer
→ 展示已确认的方案和 RoundDecision
→ 若需要修改：作为新一轮处理（追加 round），更新归档
→ 若仅回顾：展示后继续当前场景
```

### C.6 场景间依赖冲突

```
→ 当后续场景的设计决策与已完成场景的约束冲突时：
  1. 从归档回引冲突场景的 RoundDecision
  2. 向设计师展示冲突点
  3. 设计师决定：修改当前场景 or 回退修改先前场景
→ 无论哪种，都通过语义合并处理，不简单重试
```
