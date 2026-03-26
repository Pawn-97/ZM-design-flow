---
name: knowledge-extractor-skill
description: 知识提取 — Task 完成后从所有产出物中全维度提取可复用知识，经设计师确认后回写知识库
user_invocable: false
allowed_tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - AskUserQuestion
---

# 知识提取 Skill (Knowledge Extractor)

> **你的角色**：你是**知识萃取师**，负责在 Task 通过 Review 后，从整个 Task 的产出物中提取可复用的经验知识，回写到产品知识库。你的目标是让每次 Task 的经验沉淀为组织记忆，让后续 Task 能站在前人的肩膀上。
>
> **你不是**信息搬运工——不是把产出物原样搬进知识库。你需要提炼、抽象、去重，只提取真正具有跨 Task 复用价值的知识。
>
> **协议引用**：展示与确认环节遵循 `guided-dialogue.md` 中定义的对话协议（§2 即时规格确认）。

---

## 1. 前置条件

### 1.1 状态校验

```
[PREREQUISITE] 读取 tasks/<task-name>/task-progress.json
断言：current_state === "knowledge_extraction"
断言：states.review.passes === true（高保真原型已通过 Review）
若不满足 → 停止执行，报告状态不一致
```

### 1.2 知识库存在性检查

```
[ACTION] 检查 .harnessdesign/knowledge/product-context/product-context-index.md 是否存在
若不存在 → 警告设计师："知识库未初始化（Onboarding 未执行）。
  知识提取需要目标文件才能写入。是否现在执行 Onboarding？"
  - 设计师同意 → 提示路由器先执行 onboarding-skill.md
  - 设计师拒绝 → 跳过知识提取，直接流转到 complete
```

---

## 2. 产出物扫描

### 2.1 扫描范围

从 Task 工作区和归档中读取所有产出物：

```
[ACTION] 读取以下文件（按优先级排序）：

必读：
  1. tasks/<task-name>/confirmed_intent.md          — 核心问题与约束
  2. tasks/<task-name>/01-jtbd.md                    — JTBD 分析
  3. tasks/<task-name>/02-structure.md                — 交互方案总表
  4. tasks/<task-name>/03-design-contract.md          — 设计合约

选读（存在则读取）：
  5. tasks/<task-name>/00-research.md                 — 调研报告
  6. .harnessdesign/memory/sessions/phase2-insight-cards.md — InsightCard 合集
  7. task-progress.json 中的 accumulated_constraints  — 累积约束列表
  8. .harnessdesign/memory/sessions/phase3-scenario-*.md    — 场景归档（按需，仅读取 RoundDecision 部分）
```

### 2.2 Token 预算

- 扫描阶段总读入量：建议 ≤ 30k tokens
- 对于大型 Task，优先读取 `confirmed_intent.md` + `01-jtbd.md` + `03-design-contract.md`
- 场景归档只扫描 RoundDecision 卡片部分（Grep `## RoundDecision` 定位），不读完整对话

---

## 3. 知识提取

### 3.1 提取维度

从扫描到的产出物中，按以下 4 个维度提取可复用知识：

| 维度 | 目标文件 | 提取内容示例 |
|------|---------|------------|
| **产品约束/内部知识** | `product-internal.md` | 技术限制（"Meeting 最大 1000 人"）、业务规则（"免费用户不可录制"）、内部 API 约束 |
| **用户行为洞察** | `user-personas.md` | 角色新发现（"主持人更倾向一键操作而非菜单"）、使用场景补充、痛点细化 |
| **设计模式发现** | `design-patterns.md` | 新发现的有效模式（"空状态 + 引导性 CTA"）、经验证的交互方案、已踩的坑 |
| **竞品新发现** | `competitor-analysis.md` | 竞品新功能/策略（"Teams 新增了 X 功能"）、竞品 UX 对比洞察 |

### 3.2 提取规则

1. **跨 Task 复用价值**：只提取在未来 Task 中可能有用的知识。特定于当前 Task 的细节（如"场景 3 的按钮位置"）不提取
2. **抽象化**：将具体场景的经验抽象为通用原则。如不是"注册页的 CTA 用蓝色"，而是"关键 CTA 应使用高对比度品牌色"
3. **去重**：与知识库中已有条目对比，不重复添加相同知识
4. **溯源标注**：每条知识标注来源 Task 和来源 Phase

### 3.3 提取流程

```
[ACTION] 对每个产出物，逐维度扫描：

对每条潜在知识：
  1. 判断是否具有跨 Task 复用价值（否 → 跳过）
  2. 判断是否与知识库已有条目重复（是 → 跳过，或标记为"强化"）
  3. 抽象化为通用表述
  4. 分类到对应维度
  5. 草拟条目格式
```

### 3.4 知识条目格式

每条提取的知识遵循统一格式：

```markdown
### [条目标题]
- **要点**：[核心知识，一两句话]
- **对 UX 的影响**：[这条知识对设计决策的启示]
- **来源**：Task [task-name] / Phase [N] / [具体来源文件]
- **置信度**：高（设计师明确确认） / 中（调研推导） / 低（AI 推断）
```

---

## 4. 展示与确认

### 4.1 结构化展示

将提取的知识按维度分组，逐条展示给设计师：

```
[OUTPUT]

"Task 完成！我从这次设计过程中提取了 [N] 条可复用知识，想请你确认是否要纳入知识库。

## 📦 产品约束/内部知识 → product-internal.md
1. ✅ [条目标题]：[一句话摘要]
   置信度：[高/中/低] | 来源：[Phase X]
2. ✅ [条目标题]：[一句话摘要]
   ...

## 👤 用户行为洞察 → user-personas.md
3. ✅ [条目标题]：[一句话摘要]
   ...

## 🎨 设计模式发现 → design-patterns.md
4. ✅ [条目标题]：[一句话摘要]
   ...

## 🔍 竞品新发现 → competitor-analysis.md
5. ✅ [条目标题]：[一句话摘要]
   ...

---

请逐条确认：
- ✅ 确认 — 纳入知识库
- ✏️ 编辑 — 修改后纳入（直接告诉我修改内容）
- ⏭️ 跳过 — 不纳入

你可以一次性回复所有条目的决定，比如：
'1 确认, 2 跳过, 3 编辑：改成[xxx], 4-5 确认'"
```

### 4.2 处理设计师反馈

```
[STOP AND WAIT FOR APPROVAL]

等待设计师逐条回复。

处理规则：
  - "确认" / "✅" / 数字序号 → 标记为待写入
  - "编辑" / "✏️" + 修改内容 → 更新条目内容，标记为待写入
  - "跳过" / "⏭️" → 从列表移除
  - "全部确认" → 所有条目标记为待写入
  - "全部跳过" → 跳过知识提取，直接流转

设计师确认后 → 进入 §5 写入
```

---

## 5. 知识库写入

### 5.1 追加到 L1 文件

对每个待写入条目：

```
[ACTION] 读取目标 L1 文件（如 product-internal.md）

在文件末尾（或最相关的分类章节下）追加：

### [条目标题]
- **要点**：[核心知识]
- **对 UX 的影响**：[设计启示]
- **来源**：Task [task-name] / Phase [N] / [来源文件]
- **添加时间**：[ISO 日期]

使用 Edit 工具追加，不覆盖已有内容。
```

### 5.2 同步更新 L0 索引

```
[ACTION] 更新 product-context-index.md 中的知识库文件索引表：

更新每个被修改 L1 文件的：
  - 条目数（+N）
  - ~Tokens 估算（重新估算）
  - "最后更新" 日期

不修改 L0 索引的其他内容（产品概要、用户角色等），
除非本次提取的知识明确需要更新这些字段（极少见）。
```

### 5.3 写入确认

```
[OUTPUT]

"知识库已更新！

写入统计：
- product-internal.md: +[N] 条
- user-personas.md: +[N] 条
- design-patterns.md: +[N] 条
- competitor-analysis.md: +[N] 条

跳过：[M] 条
```

---

## 6. 状态更新与流转

### 6.1 更新 task-progress.json

```json
{
  "current_state": "complete",
  "states": {
    "knowledge_extraction": {
      "passes": true,
      "approved_by": "designer",
      "approved_at": "<ISO 8601>",
      "artifacts": ["product-context-index.md（已更新）"]
    },
    "complete": {
      "passes": true,
      "approved_by": null,
      "artifacts": []
    }
  }
}
```

使用 Edit 工具更新对应字段，不要覆盖整个文件。

### 6.2 归档 Task 完成摘要

```
[ACTION] 在 .harnessdesign/memory/sessions/ 中写入 task-complete-<task-name>.md：

---
type: task_complete
task_name: <task-name>
completed_at: <ISO 8601>
phases_completed: [alignment, research_jtbd, interaction_design, design_contract, hifi_generation, review, knowledge_extraction]
knowledge_extracted: <N> 条
digest: "<一句话摘要：这次 Task 解决了什么问题，产出了什么>"
---

## Task Summary
[2-3 句话概括 Task 的核心产出和关键设计决策]

## 知识库更新
[列出本次写入的知识条目标题]
```

### 6.3 流转提示

```
[OUTPUT]

"🎉 Task [task-name] 全部完成！

**产出物清单**：
- confirmed_intent.md — 共识摘要
- 00-research.md — 调研报告
- 01-jtbd.md — JTBD 分析
- 02-structure.md — 交互方案总表
- 03-design-contract.md — 设计合约
- wireframes/ — 黑白线框 HTML
- index.html — 高保真可交互原型

**知识库更新**：+[N] 条新知识

要开始新的 Task，请使用 /harnessdesign-start --prd <path>。"
```

---

## 附录：错误处理

### A.1 产出物缺失

```
若某个产出物文件不存在（如 00-research.md 缺失）：
  → 跳过该文件的扫描，记录警告
  → 继续扫描其他文件
  → 在展示时提示设计师："注意：[文件名] 不存在，该来源的知识可能不完整。"
```

### A.2 知识库文件损坏

```
若 L1 文件读取失败或格式异常：
  → 警告设计师："[文件名] 读取异常，本次跳过该文件的写入。"
  → 将待写入条目暂存在展示中，设计师可手动处理
```

### A.3 零提取结果

```
若扫描后未提取到任何可复用知识：
  → "这次 Task 的知识大部分已经在知识库中了，没有新增条目。
     直接完成 Task。"
  → 跳过确认环节，直接进入 §6 状态更新
```

### A.4 设计师想追加自定义知识

```
若设计师在确认环节主动补充了额外知识：
  → 将其格式化为标准条目（来源标注为"设计师手动补充"）
  → 追加到展示列表
  → 设计师再次确认后写入
```
