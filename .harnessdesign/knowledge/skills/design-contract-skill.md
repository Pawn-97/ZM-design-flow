---
name: design-contract-skill
description: Phase 3→4 过渡 — 从场景归档中提取 ScenarioContract、合成 DesignContract、双向校验完备性，反上下文饥饿
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

# Phase 3→4 过渡: 设计合约生成 Skill (Design Contract Generator)

> **你的角色**：你是**跨场景信息提取器**，负责从 Phase 3 所有场景归档中定向提取导航拓扑、交互承诺和全局约束，合成结构化设计合约。你的产出是 Phase 4 高保真生成的蓝图。
>
> **为什么需要这一步**：Phase 3 的场景级压缩（每场景 ~200 tokens 摘要）会丢失跨场景导航拓扑、具体交互承诺和全局设计约束。Design Contract 机制在进入 Phase 4 前定向提取这些关键信息，确保 Alchemist 拥有生成跨场景一致原型所需的全部上下文。
>
> **协议引用**：本 Skill 在设计师 Review 环节遵循 `guided-dialogue.md` 中定义的对话协议。

---

## 0. 内部阶段总览

```
[加载上下文] → [并发场景提取 ScenarioContract]
                     ↓
              [全局合约合成 DesignContract]
                     ↓
              [双向校验 + GAP 标注]
                     ↓
              [写入 03-design-contract.md]
                     ↓
              [摘要索引回填]
                     ↓
              [STOP: 设计师 Review/编辑合约]
                     ↓
              [流转到 hifi_generation]
```

---

## 1. 前置条件与上下文加载

### 1.1 状态校验

```
[PREREQUISITE] 读取 tasks/<task-name>/task-progress.json
断言：current_state === "prepare_design_contract"
断言：states.interaction_design.passes === true
断言：所有 scenarios 的 status 均为 "archived" 或 "skipped"
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
1. tasks/<task-name>/02-structure.md（交互方案总表，Phase 3 产出）
2. task-progress.json 中的 scenarios 字段（获取场景列表和归档路径）
```

---

## 2. 并发场景提取 — ScenarioContract

### 2.1 提取流程

对 `task-progress.json.states.interaction_design.scenarios` 中每个 `status === "archived"` 的场景执行提取：

```
[ACTION] 对每个已完成场景，读取：
1. .harnessdesign/memory/sessions/phase3-scenario-{n}.md（场景归档，含 RoundDecision 汇总）
2. .harnessdesign/memory/sessions/phase3-scenario-{n}-round-{m}.md（各轮次 Recall Buffer，按需）

从归档中提取 ScenarioContract。
```

> **并行能力**：N 个场景的提取相互独立，可利用 AI 工具的 Agent 并行能力并发执行。每个场景独立产出 ScenarioContract，符合 Assembler Pattern 原则。

### 2.2 ScenarioContract 结构

对每个场景提取以下结构：

```yaml
# ScenarioContract（单场景的设计合约）

scenario_id: "scenario-1"
scenario_name: "会前准备"
selected_option_summary: "时间线视图，支持拖拽排序议程项"  # ~100 tokens

# 入口条件
entry_conditions:
  - source_scenario: "scenario-0"       # 或 "external"（首场景）
    trigger: "用户点击'准备会议'"
    shared_state_changes:
      - "current_flow → prep"

# 出口动作
exit_actions:
  - target_scenario: "scenario-2"
    trigger: "用户点击'完成准备'"
    shared_state_changes:
      - "meeting_status → prepared"

# 共享状态依赖
shared_state_dependencies:
  consumed_from:
    - "current_user（来自登录流程）"
    - "meeting_info（来自会议列表）"
  produced_for:
    - "agenda_items（供场景 2 消费）"
    - "meeting_status（供场景 3 检查）"

# 交互承诺（从 RoundDecision.interaction_details 提取，max 5 条）
interaction_commitments:
  - "列表项支持拖拽排序，拖拽时显示占位虚线框"
  - "空状态使用插画 + 引导文案 + CTA 按钮"
  - "时间线视图支持折叠/展开"
  # ... max 5 条最关键的交互决策

# 全局约束（从 RoundDecision.constraints_added 提取）
global_constraints:
  - "首屏不超过 5 个交互模块"
  - "不使用纯文字空状态"

# 边缘态清单
edge_cases_to_handle:
  - "0 个议程项 → 空状态"
  - "权限不足 → 错误提示 + 跳转"
  - "网络中断 → 重试按钮"
```

### 2.3 提取质量检查

对每个 ScenarioContract 执行以下检查：

```
[CHECK] ScenarioContract 完备性检查：
- [ ] entry_conditions 至少 1 条（首场景可为 "external"）
- [ ] exit_actions 至少 1 条（末尾场景可为 "task_complete"）
- [ ] interaction_commitments ≤ 5 条，每条来自 RoundDecision.interaction_details
- [ ] edge_cases_to_handle 至少包含：空状态、错误态
- [ ] selected_option_summary 不超过 100 tokens
```

缺失项标注 `[⚠️ GAP]` 并补充合理推断（标记 `[auto-补充]`）。

---

## 3. 全局合约合成 — DesignContract

### 3.1 合成输入

```
[ACTION] 将以下内容合成为 DesignContract：
1. 所有 ScenarioContract（N 个）
2. 02-structure.md（交互方案总表）
3. confirmed_intent.md（核心问题、约束条件、成功标准）
```

### 3.2 DesignContract 结构

```yaml
# DesignContract（Phase 4 高保真生成的完整设计合约）

# 导航拓扑图
navigation_topology:
  entry_point: "scenario-1"             # 用户进入的第一个场景
  adjacency:                            # 场景间连接关系
    scenario-1: ["scenario-2"]
    scenario-2: ["scenario-3", "scenario-1"]
    scenario-3: []                      # 终点场景

# 共享状态模型
shared_state_model:
  - name: "current_user"
    type: "User 对象"
    produced_by: ["auth_flow"]
    consumed_by: ["scenario-1", "scenario-2", "scenario-3"]
  - name: "agenda_items"
    type: "Agenda[]"
    produced_by: ["scenario-1"]
    consumed_by: ["scenario-2"]

# 全局设计约束（从所有 ScenarioContract 中去重合并）
global_constraints:
  - "首屏交互模块数 ≤ 5"
  - "不使用纯文字空状态"
  - "动效时长 ≤ 300ms"
  # ... 去重后的完整约束列表

# 视觉一致性规则（从约束推导）
visual_consistency_rules:
  - "所有场景使用统一的侧边栏导航"
  - "按钮圆角统一 8px"
  - "信息密度控制：每屏 ≤ 12 个交互元素"
  # ... 从 confirmed_intent 和 constraints 推导

# 各场景合约
scenarios:
  - scenario_id: "scenario-1"
    scenario_name: "会前准备"
    selected_option_summary: "..."
    entry_conditions: [...]
    exit_actions: [...]
    interaction_commitments: [...]
    edge_cases_to_handle: [...]
  # ... 完整 ScenarioContract 列表

# 聚合边缘态清单
edge_cases_to_handle:
  - category: "空状态"
    scenarios: ["scenario-1", "scenario-3"]
    pattern: "[ZDS:zds-empty-state] 插画 + 引导文案"
  - category: "网络错误"
    scenarios: ["all"]
    pattern: "Toast 提示 + 重试按钮"
  - category: "权限缺失"
    scenarios: ["scenario-1"]
    pattern: "错误页 + 跳转建议"
```

### 3.3 约束去重合并规则

```
[RULE] 合并 global_constraints 时：
1. 精确匹配 → 去重保留
2. 同维度冲突（如"≤ 5 模块" vs "≤ 7 模块"）→ 保留更严格的约束，标注来源场景
3. 隐含重复（如"不使用弹窗"和"避免 modal"）→ 统一为一条，注明覆盖范围
```

---

## 4. 双向校验

### 4.1 前向校验（承诺完整性）

```
[CHECK] 对每个 ScenarioContract 的 interaction_commitments：
- 追溯到原始 phase3-scenario-{n}.md 归档中的 RoundDecision
- 确认每个承诺都有对应的 RoundDecision.interaction_details 支撑
- 无支撑的承诺 → 标注 [⚠️ GAP: 无原始依据]
```

### 4.2 反向校验（结构完整性）

```
[CHECK] 结构完整性检查：
- [ ] 每个场景至少 1 个 entry_condition（首场景可为 external）
- [ ] 每个场景至少 1 个 exit_action（终点场景可为 task_complete）
- [ ] navigation_topology.adjacency 无孤岛场景（所有场景可达）
- [ ] navigation_topology 无死胡同（除明确的终点场景外）
- [ ] shared_state_model 中每个 state 的 produced_by 和 consumed_by 都非空
- [ ] shared_state_model 无未消费的状态（produced 但不 consumed → 标注 [⚠️ GAP]）
- [ ] shared_state_model 无未生产的依赖（consumed 但不 produced → 标注 [⚠️ GAP]）
```

### 4.3 GAP 处理

- 所有 `[⚠️ GAP]` 项在输出时高亮显示
- AI 为每个 GAP 提供合理推断并标记 `[auto-补充]`
- 设计师在 Review 时逐一确认/修改/删除

---

## 5. 产出与写入

### 5.1 写入 03-design-contract.md

```
[ACTION] 写入 tasks/<task-name>/03-design-contract.md

文档格式为纯 Markdown（设计师可在 IDE 中直接编辑），结构如下：
```

```markdown
# 设计合约 (Design Contract)

> 本文档是 Phase 4 高保真生成的蓝图。修改此文件将直接影响生成的原型。
> 标注 [⚠️ GAP] 的条目需要设计师确认。标注 [auto-补充] 的条目由 AI 推断补充。

## 导航拓扑

**入口场景**：[场景名称]

**场景间连接**：
| 从 | 到 | 触发条件 |
|----|----|---------|
| 场景 1 | 场景 2 | [触发描述] |
| ... | ... | ... |

## 共享状态模型

| 状态名称 | 类型 | 生产场景 | 消费场景 |
|---------|------|---------|---------|
| current_user | User | auth_flow | 场景 1, 2, 3 |
| ... | ... | ... | ... |

## 全局设计约束

1. [约束内容]（来源：场景 N）
2. [约束内容]（来源：场景 M, N）
...

## 视觉一致性规则

1. [规则内容]
2. [规则内容]
...

## 各场景合约

### 场景 1: [场景名称]

**选定方案**：[方案摘要]

**入口条件**：
- 来自 [场景/外部]，触发：[条件]

**出口动作**：
- 前往 [场景]，触发：[条件]

**交互承诺**：
1. [具体交互决策]
2. [具体交互决策]
...（max 5 条）

**边缘态处理**：
- [边缘态] → [处理方式]
...

### 场景 2: [场景名称]
...

## 聚合边缘态清单

| 类别 | 涉及场景 | 统一处理模式 |
|------|---------|------------|
| 空状态 | 场景 1, 3 | [ZDS:zds-empty-state] 插画 + 引导文案 |
| 网络错误 | 所有 | Toast 提示 + 重试按钮 |
| ... | ... | ... |

## GAP 清单（需设计师确认）

- [ ] [⚠️ GAP] [GAP 描述]（[auto-补充]: [AI 推断内容]）
...
```

### 5.2 摘要索引回填

```
[ACTION] 从所有 ScenarioContract 中提取语义标签，回填到摘要索引：

从 shared_state_dependencies 提取：
- [状态:xxx] 标签（如 [状态:current_user], [状态:agenda_items]）

从 exit_actions 提取：
- [依赖:→场景N] 标签（如 [依赖:→场景2], [依赖:→场景3]）

回填到锚定层摘要索引中已有的场景条目。
这一步补全了场景完成时无法确定性提取的跨场景维度标签。
```

---

## 6. 更新 task-progress.json

```
[ACTION] 使用 Edit 工具更新 task-progress.json：

1. states.prepare_design_contract.passes = true
2. states.prepare_design_contract.approved_by = null（待设计师确认）
3. states.prepare_design_contract.artifacts = ["03-design-contract.md"]
4. current_state = "contract_review"

在 archive_index 中追加：
{
  "file": "03-design-contract.md",
  "type": "design_contract",
  "phase": "3→4",
  "digest": "设计合约：N 个场景的导航拓扑、交互承诺和全局约束"
}
```

---

## 7. 设计师 Review

### 7.1 呈现合约

```
[OUTPUT]

"设计合约已生成，保存在 03-design-contract.md。

**概览**：
- 共 {N} 个场景，入口场景：{场景名称}
- 共享状态：{M} 个跨场景状态变量
- 全局约束：{K} 条
- 交互承诺：共 {J} 条（各场景合计）

**需要关注的 GAP**：
{列出所有 [⚠️ GAP] 项及 [auto-补充] 内容}

请在 IDE 中打开 03-design-contract.md 进行 Review。
你可以直接编辑文件内容，或在对话中告诉我修改意见。"
```

### 7.2 等待确认

```
[STOP AND WAIT FOR APPROVAL]

等待设计师对设计合约的确认。

可能的回复：
- Approve → §7.3 流转
- 修改意见 → 按 guided-dialogue.md §3 语义合并：
  合并设计师 feedback 与当前合约，更新 03-design-contract.md
  严禁简单重新生成
- 直接编辑文件 → 重新读取文件确认变更，更新摘要索引
```

### 7.3 确认后流转

```
[ACTION] 设计师确认后：

1. 更新 task-progress.json：
   - states.contract_review.passes = true
   - states.contract_review.approved_by = "designer"
   - states.contract_review.approved_at = "<ISO 8601>"
   - current_state = "hifi_generation"

2. 输出流转提示：
```

```
[OUTPUT]

"设计合约已确认。

即将进入 → Phase 4 高保真原型生成。
Alchemist 将以设计合约为蓝图，整合 ZDS 设计规范，
生成包含所有 {N} 个交互场景的完整高保真可交互 HTML。

[Continue]"
```

---

## 附录 A: Token 预算分析

### 提取阶段工作层

| 组件 | Token 预算 | 说明 |
|------|-----------|------|
| 锚定层 | ~5-6k | confirmed_intent + L0 + 摘要索引 |
| 02-structure.md | ~1-2k | 方案总表 |
| 单场景归档（提取中） | ~3-5k | phase3-scenario-{n}.md |
| ScenarioContract 输出 | ~500 | 单场景提取结果 |
| **单场景提取峰值** | **~10-13k** | |

### 合成阶段工作层

| 组件 | Token 预算 | 说明 |
|------|-----------|------|
| 锚定层 | ~5-6k | 常驻 |
| 所有 ScenarioContract | ~500 × N | N 个场景的提取结果 |
| 02-structure.md | ~1-2k | 参考 |
| DesignContract 输出 | ~3-5k | 最终合约 |
| **合成峰值** | **~12-18k** | 取决于场景数 |

---

## 附录 B: 错误处理

### B.1 场景归档文件缺失

```
→ 检查 task-progress.json.states.interaction_design.scenarios[n].archived_to
→ 若路径无效 → 报告："场景 {n} 归档文件缺失，请检查 Phase 3 归档是否完成"
→ 可从 02-structure.md 中该场景的条目做降级提取（信息量减少，标注 [⚠️ 降级提取]）
```

### B.2 RoundDecision 缺失或不完整

```
→ 从场景归档的"RoundDecision 汇总"章节中提取
→ 若汇总章节也缺失 → 从 round Recall Buffer 中逐轮搜索
→ 仍然缺失 → 该场景的 interaction_commitments 标注 [⚠️ GAP: RoundDecision 不可用]
```

### B.3 跳过的场景

```
→ status === "skipped" 的场景不提取 ScenarioContract
→ 在 DesignContract 中标注该场景为 [已跳过]
→ 若其他场景存在对该场景的 entry/exit 依赖 → 标注 [⚠️ GAP: 被跳过场景存在依赖]
```

### B.4 03-design-contract.md 写入失败

```
→ 将 DesignContract 内容输出到对话中
→ 请设计师手动保存为 03-design-contract.md
→ 重试写入
```
