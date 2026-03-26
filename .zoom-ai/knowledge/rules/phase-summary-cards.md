# Phase Summary Card Templates

> These templates define the standardized checkpoint cards that AI must render
> at every `[STOP AND WAIT FOR APPROVAL]` control point. Card content is driven
> by `validate_transition.py --summary` output, not by AI self-reporting.

## Usage in Skill SOP

Before transitioning to the next phase, the Skill SOP must include this instruction:

```
[CHECKPOINT] Run: python3 scripts/validate_transition.py --summary <task_dir>
Render the output as a Phase Summary Card using the template below.
Do NOT fabricate checklist items — use the script output verbatim.
Wait for designer confirmation before proceeding.
```

---

## Template: Phase Completion Card

```markdown
────────────────────────────────────
📋 {phase_name} 完成小结
────────────────────────────────────
{for each checklist item:}
{✅ if status=pass | ❌ if status=fail | ⏳ if status=pending | ℹ️ if status=info} {item_description}
{end for}

即将进入 → {next_phase_name}: {next_phase_description}
前置条件：{approval_requirement}

[Continue] / [回顾上一阶段讨论]
────────────────────────────────────
```

---

## Concrete Examples

### Phase 1 → Phase 2

```markdown
────────────────────────────────────
📋 Phase 1 (上下文对齐) 完成小结
────────────────────────────────────
✅ 共识摘要：confirmed_intent.md（已生成）
✅ 设计师确认：已 Approve
🗂️ 归档：1 个归档文件已保存

即将进入 → Phase 2: 调研 + JTBD
前置条件：无额外确认，可直接开始

[Continue] / [回顾 Phase 1 讨论]
────────────────────────────────────
```

### Phase 2 → Phase 3

```markdown
────────────────────────────────────
📋 Phase 2 (调研+JTBD) 完成小结
────────────────────────────────────
✅ 调研报告：00-research.md（已生成）
✅ JTBD 文档：01-jtbd.md（已生成）
✅ 设计师确认：JTBD 收敛已 Approve
✅ 知识库更新：{N} 条新洞察已确认写入
🗂️ 归档：{N} 个话题讨论已归档

即将进入 → Phase 3: 交互方案发散（逐场景）
前置条件：需要你确认场景列表

[Continue] / [回顾 Phase 2 讨论]
────────────────────────────────────
```

### Phase 3 → Design Contract

```markdown
────────────────────────────────────
📋 Phase 3 (交互方案) 完成小结
────────────────────────────────────
✅ 交互结构：02-structure.md（已生成）
✅ 全部场景：{N}/{N} 场景方案已选定
✅ 设计师确认：所有场景已 Approve
🗂️ 归档：{N} 个场景讨论已归档

即将进入 → 设计合约生成 (Design Contract)
此步骤将从所有场景归档中提取跨场景信息

[Continue] / [回顾某个场景讨论]
────────────────────────────────────
```

### Design Contract → Phase 4

```markdown
────────────────────────────────────
📋 设计合约 Review
────────────────────────────────────
✅ 设计合约：03-design-contract.md（已生成）
✅ 完备性校验：通过（{N} 个 [auto-补充] 项已标记）
⏳ 设计师确认：等待你 Review 合约

请在 IDE 中打开 03-design-contract.md 进行 Review：
  - 确认导航拓扑是否正确
  - 检查 [auto-补充] 标记的内容
  - 补充遗漏的交互细节

[Approve] / [需要修改]
────────────────────────────────────
```

### Phase 4 → Complete

```markdown
────────────────────────────────────
📋 Phase 4 (高保真原型) 完成小结
────────────────────────────────────
✅ 高保真原型：index.html（已生成）
✅ 自动化验收：HTML Lint + 认知负荷校验通过
✅ 设计师确认：原型已 Approve

即将进入 → 知识库学习提取
AI 将从本次 task 中提取可复用的产品知识

[Continue to Knowledge Extraction]
────────────────────────────────────
```
