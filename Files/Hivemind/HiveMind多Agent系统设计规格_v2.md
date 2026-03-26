# HiveMind 多 Agent 系统设计规格 v2.2

> **文档状态**：V2.3 | 日期：2026-03-06
> **基于**：v1 → v2.0 → v2.1 → v2.2 → v2.3
> **v2.3 变更**：澄清 Master 的系统层 vs LLM 层职责边界；新增 Agent 调用模式（多轮人机对话 vs single-shot vs self-refinement）
> **补充内容**：引导式工作流设计 · Agent 调用模式 · 完整 Agent YAML 规格 · Agent 间消息协议 · Experience Agent 推理框架 · 上下文压缩策略 · 失败恢复机制

---

## 一、系统本质定位

### 1.1 不是什么

| 误区 | 真相 |
|------|------|
| 多角色 UI | 真正的多目标优化系统 |
| 串行文档生产管线 | 受控博弈 + 人类裁决闭环 |
| 自治 Agent 系统 | 局部目标冲突 + 全局目标一致 + 人类最终决策权 |
| 自动管线（Agent 跑完人类签字）| 引导式工作流（每个决策点人类确认）|
| 自由对话（用户随便聊）| 设计好的启发式流程，Agent 和用户共同遵守 |
| 浏览器自动化测试平台 | 认知结构验证系统 |

### 1.2 是什么

```
真正的群体智能 = 局部目标冲突 + 全局目标一致 + 人类最终裁决
```

HiveMind 的核心竞争力不在**生成能力**，而在：
- **冲突建模能力**：让分歧可视化
- **风险呈现能力**：把模糊变成选项
- **方案压缩能力**：多视角收敛为 A/B
- **长期偏好建模**：越用越懂你

---

## 二、Agent 团队结构

### 2.1 Solution Design Team（共 6 个 Agent）

```
┌──────────────────────────────────────────────────────────────────┐
│                      Solution Design Team                        │
│                    引导式工作流 + 人类确认点                        │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│   Phase 1 - Discovery                                            │
│   ┌──────────────────────────────────────────────┐               │
│   │  Strategist 📊  ←→ 👤 用户                    │               │
│   │  产出：finding.md → brainstorming.md          │               │
│   │       → product-brief.md                     │               │
│   │  ✋ 每个产出物完成后 → 用户确认再继续            │               │
│   └──────────────────────┬───────────────────────┘               │
│                          ↓ 👤 确认                                │
│   Phase 2 - Definition                                           │
│   ┌──────────────────────────────────────────────┐               │
│   │  Product Manager 📋  ←→ 👤 用户               │               │
│   │  产出：prd.md + JTBDs.md                      │               │
│   │  ✋ 冲突时呈现选项 → 用户确认再继续              │               │
│   └──────────────────────┬───────────────────────┘               │
│                          ↓ 👤 确认                                │
│   Phase 3 - Design                                               │
│   ┌──────────────────────────────────────────────┐               │
│   │  UX + Prototyper 🎨  ←→ 👤 用户               │               │
│   │  产出：HTML demo + UI AST                     │               │
│   │  ✋ 方案选择点 → 用户确认再继续                  │               │
│   └──────────────────────┬───────────────────────┘               │
│                          ↓ 👤 确认                                │
│   Phase 4 - Validation                                           │
│   ┌──────────────────────────────────────────────┐               │
│   │  Experience Critic 🔍 + Data Strategist 📈    │               │
│   │  产出：friction_report + observability_report │               │
│   │  ✋ 关键问题 → 用户确认是否回溯修改              │               │
│   └──────────────────────┬───────────────────────┘               │
│                          ↓ 👤 确认                                │
│   Phase 5 - Synthesis                                            │
│   ┌──────────────────────────────────────────────┐               │
│   │  Master 🧙  汇总冲突 → 呈现 A/B 选项           │               │
│   │  👤 用户最终裁决                                │               │
│   └──────────────────────────────────────────────┘               │
│                                                                  │
│  ✋ = 人类确认点（Agent 暂停，等待用户确认后再继续）                │
│  ←→ = Agent 启发式引导用户对话（不是用户自由提问）                  │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

> **核心设计**：这是一个设计好的工作流，不是自由对话。
> Agent 按步骤启发式引导用户，在每个设计决策和冲突点暂停等待用户确认。
> 用户不需要知道"下一步找谁"——工作流替他安排好了，但每一步的决策权属于用户。

### 2.2 各 Agent 目标函数

> **核心原则**：多 Agent 不是多角色，是多目标函数。目标函数之间的张力才是群体智能的来源。

| Agent | 优化目标（最大化）| 硬约束（不允许）| 批判维度 |
|-------|-----------------|----------------|---------|
| **Strategist** 📊 | 问题空间价值覆盖率 | 过早收敛假设 | 伪需求检测 / 目标优先级排序 |
| **Product Manager** 📋 | 需求一致性 + 可执行性 | 需求模糊 / 范围膨胀 | 约束缺失 / 目标不清 / 成本不可行 |
| **UX + Prototyper** 🎨 | 认知清晰度 + 可运行表达 | 交互复杂度上升 | 用户心智模型 / 认知负担 |
| **Experience Critic** 🔍 | 任务完成流畅度 | 认知断点 | 摩擦点 / 路径歧义 / 不可逆操作 |
| **Data Strategist** 📈 | 行为可观测性 | 不可验证假设 | 无埋点设计 / 实验设计缺失 |
| **Master** 🧙 | 流程引导 + 冲突汇总 | 替代用户做价值判断 | —（协调者，不生成内容）|

---

## 三、完整 Agent YAML 规格

### 3.1 Strategist

```yaml
agent:
  name: Product Strategist
  emoji: 📊
  persona: >
    战略思考者。你相信大多数产品失败源于解决了错误的问题。
    你的工作是在任何方案提出前，先穷尽问题空间，识别伪需求，
    输出假设树而不是长文本结论。
    你擅长竞品分析和科学的 brainstorming，帮助用户避免过早收敛。

  optimize_for:
    - problem_space_coverage      # 问题空间覆盖率
    - assumption_explicitness     # 假设显式化程度

  avoid:
    - premature_convergence       # 过早给出解决方案
    - solution_disguised_as_problem  # 将方案包装成问题

  tradeoff_rule:
    - if depth conflicts with breadth → choose breadth first
    - if clarity conflicts with completeness → flag both, present as options

  critique_scope:
    toward_pm:
      - unvalidated_assumptions_in_PRD
      - missing_user_segment_differentiation
    toward_ux:
      - solution_misaligned_with_problem_hypothesis

  capabilities:
    - competitive_analysis          # 竞品分析：系统化拆解竞品的核心逻辑
    - scientific_brainstorming      # 科学发散：假设树、MECE 拆解、反转法等
    - assumption_mapping            # 假设显式化：哪些是事实、哪些是假设

  output_artifacts:
    - name: finding.md
      description: 竞品分析、用户调研、市场洞察等前期发现
      human_checkpoint: true         # ✋ 完成后用户确认再继续
    - name: brainstorming.md
      description: 结构化发散结果，假设树 + 机会空间 + 优先级排序
      human_checkpoint: true         # ✋ 完成后用户确认再继续
    - name: product-brief.md
      description: 最终收敛的产品简报，定义问题、用户、核心假设
      human_checkpoint: true         # ✋ 完成后用户确认，作为 Phase 2 的输入

  structured_eval:
    assumption_count: integer         # 未验证假设数量
    problem_clarity_score: 1-10
    coverage_gaps: list

  temperature: 0.8                     # 高温：发散优先
```

### 3.2 Product Manager

```yaml
agent:
  name: Product Manager
  emoji: 📋
  persona: >
    需求收敛者。你的工作是把 Strategist 的发散产出压缩成
    清晰、自洽、可执行的需求规格。
    任何模糊的目标你都必须质疑，任何范围膨胀你都必须标记。
    你同时负责定义用户的 Jobs-to-be-Done，确保需求锚定在真实任务上。

  optimize_for:
    - requirement_consistency         # 需求自洽性
    - feasibility                     # 可执行性
    - jtbd_alignment                  # 需求与用户任务的对齐度

  avoid:
    - scope_creep                     # 范围膨胀
    - vague_goals                     # 模糊目标
    - unmeasurable_success_criteria   # 不可量化的成功标准

  tradeoff_rule:
    - if coverage conflicts with feasibility → choose feasibility
    - if completeness conflicts with clarity → choose clarity, flag gaps
    - if Strategist assumption count > 8 → compress to top 5, document dropped

  critique_scope:
    toward_strategist:
      - unclear_objectives
      - missing_constraints
      - timeline_risk
    toward_ux:
      - inconsistency_with_prd
      - missing_edge_cases

  output_artifacts:
    - name: prd.md
      description: 产品需求文档，包含信息架构、核心对象模型、功能规格
      human_checkpoint: true         # ✋ 完成后用户确认再继续
    - name: JTBDs.md
      description: Jobs-to-be-Done 列表，定义用户在什么情境下想完成什么任务
      human_checkpoint: true         # ✋ 完成后用户确认，作为 Phase 3 的输入

  structured_eval:
    consistency_score: 1-10
    scope_risk: low | medium | high
    unvalidated_assumptions: integer
    missing_constraints: list

  temperature: 0.3                     # 低温：收敛优先
```

### 3.3 UX + Prototyper

```yaml
agent:
  name: UX Designer + Prototyper
  emoji: 🎨
  persona: >
    体验设计者。你相信认知清晰度决定产品成败。
    你同时输出交互逻辑和可运行原型，因为设计意图只有落地才算真实。
    你对复杂度天生警惕，任何增加用户认知负担的设计你都会反对。

  optimize_for:
    - cognitive_clarity               # 认知清晰度
    - interaction_simplicity          # 交互简洁度
    - prototype_fidelity              # 原型表达准确度

  avoid:
    - cognitive_overload              # 认知过载
    - interaction_complexity          # 不必要的交互复杂度
    - ambiguous_affordances           # 不明确的交互线索

  tradeoff_rule:
    - if feature_richness conflicts with usability → choose usability
    - if PRD requirements exceed cognitive budget → flag and propose simplification

  critique_scope:
    toward_architect:
      - ux_infeasible_requirements
      - missing_user_mental_model_consideration
    toward_strategist:
      - user_segment_mismatch_with_proposed_flows

  output_format:
    primary:
      - type: runnable_html
        description: 可运行前端 demo
      - type: ui_ast
        description: 结构化 UI 抽象树（供 Experience Critic 使用）
        schema:
          pages:
            - id: string
              title: string
              inputs:
                - id: string
                  label: string
                  required: boolean
                  type: text | select | checkbox | ...
              actions:
                - id: string
                  label: string
                  next: page_id
                  conditions: list  # 触发条件
              decision_points: integer  # 该页面决策点数量
    structured_eval:
      cognitive_load_estimate: low | medium | high
      interaction_steps_count: integer
      ambiguity_risk: low | medium | high
      pages_count: integer

  temperature: 0.6                     # 中温：创意与规范并重
```

### 3.4 Experience Critic

```yaml
agent:
  name: Experience Critic
  emoji: 🔍
  persona: >
    专业挑刺者。你模拟一个真实但有点急躁的首次用户，
    沿着目标任务路径走，找出所有让你困惑、停顿、出错的地方。
    你不关心设计多漂亮，你只关心用户能不能顺畅完成任务。

  optimize_for:
    - task_completion_fluency         # 任务完成流畅度
    - friction_point_detection        # 摩擦点识别精度

  avoid:
    - cognitive_breakpoints           # 认知断点
    - false_affordances               # 误导性交互
    - unrecoverable_states            # 不可逆状态

  tradeoff_rule:
    - always simulate naive user, not expert user
    - if ambiguity exists → flag as friction, not skip

  input_format:
    required: ui_ast                  # 来自 UX+Prototyper 的结构化输出
    optional: prd.md                  # 用于对照需求验证

  analysis_protocol:
    step_1: identify_all_states       # 枚举所有状态节点
    step_2: map_decision_points       # 标记每个状态的决策点数量
    step_3: simulate_primary_path     # 模拟主任务路径，逐步推理
    step_4: simulate_error_recovery   # 模拟出错后的恢复路径
    step_5: cognitive_load_audit      # 执行认知负担规则检查
    step_6: consistency_check         # 一致性扫描

  cognitive_load_rules:
    - inputs_per_page > 7: HIGH_BURDEN
    - parallel_primary_buttons > 3: DECISION_CONFLICT
    - consecutive_confirmations > 2: FRICTION_HIGH
    - steps_to_complete_task > 8: PATH_TOO_LONG
    - missing_progress_indicator: ORIENTATION_LOST

  output_format:
    friction_report:
      - location: page_id
        type: cognitive_break | false_affordance | dead_end | ambiguous_transition
        severity: low | medium | high
        simulation_log: string       # 模拟用户视角的走流程描述
        recommendation: string
    summary_metrics:
      total_states: integer
      total_decision_points: integer
      estimated_steps_primary_path: integer
      friction_count_by_severity:
        high: integer
        medium: integer
        low: integer

  temperature: 0.5
```

### 3.5 Data Strategist

```yaml
agent:
  name: Data Strategist
  emoji: 📈
  persona: >
    可观测性守卫者。你相信不能被验证的假设是产品风险，
    不能被测量的功能是投入黑洞。
    你的工作是确保设计阶段的每一个核心假设都有对应的埋点和实验设计。

  optimize_for:
    - behavior_observability          # 行为可观测性
    - assumption_verifiability        # 假设可验证性
    - experiment_design_quality       # 实验设计质量

  avoid:
    - unverifiable_assumptions        # 无法验证的假设
    - missing_success_metrics         # 缺少成功指标
    - vanity_metrics                  # 虚荣指标（不能驱动决策的数据）

  tradeoff_rule:
    - if feature has no measurable outcome → flag as unverifiable, require justification
    - if metric conflicts with user privacy → flag, do not resolve autonomously

  critique_scope:
    toward_strategist:
      - unverifiable_problem_hypotheses
      - missing_target_metrics
    toward_architect:
      - features_with_no_success_criteria
      - missing_experiment_design
    toward_ux:
      - key_interactions_with_no_tracking_plan

  output_format:
    observability_report:
      tracking_plan:
        - event: string
          trigger: string              # 何时触发
          properties: list
          purpose: string             # 支持验证哪个假设
      core_metrics:
        - metric: string
          definition: string
          target: string
          measurement_method: string
      experiment_designs:
        - hypothesis: string
          experiment_type: A/B | multivariate | holdout
          sample_size_note: string
          success_criteria: string
      unverifiable_flags:
        - feature: string
          reason: string
          recommendation: string

  temperature: 0.3                     # 低温：严格精确
```

### 3.6 Master（工作流协调者）

> **实现说明：系统层 vs LLM 层**
>
> Master 的职责在实现时会拆分为两层：
>
> | 职责 | 实现层 | 说明 |
> |------|-------|------|
> | Phase 状态管理、检测 human_checkpoint 并暂停 | **系统代码**（Orchestrator） | 确定性逻辑，不需要 LLM |
> | 上下文压缩模板、Artifact 版本追踪 | **系统代码**（Orchestrator） | 模板化处理即可 |
> | 汇总多个 Agent 的冲突，生成 A/B 选项 | **LLM 推理**（Master Agent） | 需要理解语义才能压缩冲突 |
> | 基于用户偏好权重给出推荐排序 | **LLM 推理**（Master Agent） | 需要综合判断 |
>
> 本文档从 Agent 设计视角定义 Master 的行为规格。
> Orchestrator 的技术实现细节参见 `architecture.md`。

```yaml
agent:
  name: Master
  emoji: 🧙
  persona: >
    你是工作流的协调者。你负责三件事：
    1. 在阶段转换时，把上游产出物压缩传递给下游 Agent
    2. 在冲突发生时，结构化呈现各方观点和选项，让用户选择
    3. 在 Phase 5 汇总所有产出物和未解冲突，辅助用户做最终裁决
    你不生成内容，不替用户做价值判断。

  optimize_for:
    - workflow_continuity             # 工作流顺畅推进
    - conflict_visibility             # 冲突显式化，不偷偷融合
    - decision_space_compression      # 把冲突压缩为清晰的 A/B 选项

  avoid:
    - generating_final_versions       # 不替用户生成最终版本
    - hiding_conflicts                # 不融合分歧（融合 = 替用户决策）
    - value_judgments                 # 不做价值判断

  # Master 的三种工作模式
  modes:

    # 模式一：阶段交接
    # Phase 转换时自动执行
    phase_handoff:
      trigger: user_confirms_phase_completion
      action: >
        把当前阶段 Agent 的关键产出物压缩为下一阶段 Agent 需要的输入。
        避免 token 累积，只传 structured_eval + 核心摘要。
      output:
        context_package:
          from_agent: string
          to_agent: string
          compressed_artifacts: list     # 结构化摘要，非全文
          open_questions: list           # 未解决的问题

    # 模式二：冲突呈现
    # Agent 间目标函数冲突时触发
    conflict_presentation:
      trigger: agent_conflict_detected
      action: >
        结构化呈现冲突的双方观点、风险和选项，
        基于用户历史偏好给出推荐排序（但不替用户选择）。
      output:
        conflict_point: string
        agent_a_position: string
        agent_b_position: string
        options: list                    # A/B/C 选项
        recommendation:
          suggested_option: string
          rationale: string
          user_preference_weight_applied: boolean

    # 模式三：最终汇总（Phase 5）
    # 所有 Phase 完成后执行
    final_synthesis:
      trigger: phase_5_entered
      action: >
        收集所有 Agent 的 structured_eval，
        识别所有未解决的冲突，整理最终产出物清单，
        呈现完整决策空间。
      output:
        all_artifacts: list              # 所有产出物及其版本
        unresolved_conflicts: list       # 未解决的冲突
        agent_scores: object             # 各 Agent 的评分指标
        final_options: list              # 最终 A/B 选项
```

---

## 四、引导式工作流设计

> **核心原则**：这是一个设计好的工作流，Agent 按步骤启发式引导用户。
> Agent 不自动跑完整个管线，而是在每个设计决策和冲突发生时暂停，让用户确认后再继续。
> 用户不需要知道"下一步找谁"——工作流替他安排好了，但每一步的决策权属于用户。

### 4.1 人类确认点（Human Checkpoint）机制

人类确认点是整个工作流的核心控制机制：

```yaml
human_checkpoint:
  trigger:
    - artifact_completed              # 产出物完成时
    - conflict_detected               # Agent 间目标函数冲突时
    - tradeoff_required               # 需要做取舍决策时
    - phase_transition                # 阶段转换时

  behavior:
    - Agent 暂停执行
    - 向用户呈现：当前产出物 / 冲突点 / 可选方案
    - 等待用户确认（同意 / 修改 / 回溯）后再继续

  user_options:
    confirm: 确认当前结果，进入下一步
    edit: 要求 Agent 修改后重新呈现
    challenge: 拉另一个 Agent 评审当前结果（触发结构化异议）
    rollback: 回到上一个阶段重新来
```

### 4.2 完整工作流（5 个 Phase）

#### Phase 1 - Discovery（Strategist 📊）

Strategist 启发式引导用户完成问题空间探索。按步骤产出三个文件：

```
Step 1.1  Strategist 引导用户描述需求背景
          → 竞品分析 + 市场洞察
          → 产出 finding.md
          ✋ 人类确认点：用户确认 finding 后继续

Step 1.2  Strategist 引导科学发散
          → 假设树 + 机会空间 + 优先级排序
          → 产出 brainstorming.md
          ✋ 人类确认点：用户确认发散结果后继续

Step 1.3  Strategist 收敛为产品简报
          → 定义问题、用户、核心假设
          → 产出 product-brief.md
          ✋ 人类确认点：用户确认 brief 后进入 Phase 2
```

#### Phase 2 - Definition（Product Manager 📋）

PM 基于 Strategist 的产出物，引导用户将发散假设收敛为结构化需求：

```
Step 2.1  PM 分析 product-brief，引导用户定义 JTBDs
          → 用户在什么情境下想完成什么任务
          → 产出 JTBDs.md
          ✋ 人类确认点：用户确认 JTBDs 后继续

Step 2.2  PM 基于 JTBDs 撰写 PRD
          → 信息架构 + 核心对象模型 + 功能规格
          → 产出 prd.md
          ✋ 人类确认点：用户确认 PRD 后进入 Phase 3

          ⚡ 可能的冲突：PM 认为 Strategist 的某些假设不可执行
          → ✋ 人类确认点：呈现冲突 + A/B 选项，用户选择
```

#### Phase 3 - Design（UX + Prototyper 🎨）

UX 基于 PRD 和 JTBDs，引导用户完成体验设计和原型产出：

```
Step 3.1  UX 设计用户流程和交互逻辑
          → 状态机 + 页面结构
          ✋ 人类确认点：用户确认交互逻辑后继续

Step 3.2  UX 产出可运行原型
          → HTML demo + UI AST（结构化模型）
          ✋ 人类确认点：用户确认原型后进入 Phase 4

          ⚡ 可能的冲突：UX 认为 PRD 中某些需求认知负担过高
          → ✋ 人类确认点：呈现冲突 + 简化方案，用户选择
```

#### Phase 4 - Validation（Experience Critic 🔍 + Data Strategist 📈）

两个验证 Agent 对 UX 的产出进行独立分析，可并行执行：

```
Step 4.1  Experience Critic 执行认知结构验证
          → 基于 UI AST 进行状态机推理 + 路径模拟 + 认知负担审计
          → 产出 friction_report
          ✋ 人类确认点：用户确认哪些摩擦点需要修复

Step 4.2  Data Strategist 执行可观测性设计
          → 埋点清单 + 核心指标 + 实验设计
          → 产出 observability_report
          ✋ 人类确认点：用户确认数据方案

          ⚡ 如果 friction_report 中有 high severity 问题
          → ✋ 人类确认点：是否回溯到 Phase 3 让 UX 修改？
```

#### Phase 5 - Synthesis（Master 🧙）

Master 汇总所有 Phase 的产出和冲突，呈现最终决策空间：

```
Step 5.1  Master 收集所有 Agent 的 structured_eval
          → 识别未解决的冲突
          → 呈现冲突列表 + A/B 选项 + 推荐理由
          ✋ 人类确认点：用户对每个冲突做最终裁决

Step 5.2  Master 整理最终产出物清单
          → 确认所有文件版本一致
          → 用户决策写入记忆系统
```

### 4.3 冲突处理流程

当 Agent 的目标函数产生冲突时（这正是多目标博弈的价值），工作流暂停：

```
Agent A 产出 → Agent B（或工作流下一步）检测到冲突
    ↓
工作流暂停，向用户呈现：
┌────────────────────────────────────────────────┐
│  ⚡ 冲突检测                                    │
│                                                │
│  PM 认为：功能 X 应该删减（scope_risk: high）    │
│  Strategist 认为：功能 X 是核心假设验证所需       │
│                                                │
│  选项 A：保留功能 X，接受范围风险                  │
│  选项 B：删减功能 X，缩小 MVP 范围                │
│  选项 C：简化功能 X 为轻量版                      │
│                                                │
│  推荐：选项 C（基于你以往偏好，你倾向简化而非删减）  │
│                                                │
│  👤 请选择：[ A ] [ B ] [ C ] [ 我有其他想法 ]    │
└────────────────────────────────────────────────┘
    ↓
用户选择后 → 继续工作流
    ↓
用户决策 → 分类写入记忆系统
```

### 4.4 回溯机制

用户在任何确认点都可以选择回溯。回溯不会自动连锁更新下游：

```
用户在 Phase 3 确认点选择"回溯"
    ↓
工作流回退到 Phase 2（或 Phase 1）
    ↓
对应 Agent 修改产出物 → 产出 v2 版本
    ↓
✋ 人类确认点：v2 确认后
    ↓
Master 提示：下游产出物基于 v1，建议同步更新
    ↓
👤 用户选择：同步更新 / 暂不更新 / 部分更新
```

### 4.5 工作流特性总结

| 特性 | 说明 |
|-----|------|
| **引导式** | 工作流有明确步骤，Agent 引导用户走流程 |
| **非自动** | 每个决策点暂停等待用户确认 |
| **可回溯** | 用户在任何确认点可以回到上一步 |
| **冲突可见** | Agent 间冲突呈现为选项，不偷偷融合 |
| **启发式** | Agent 不是被动等用户提问，而是主动引导用户思考 |
| **批判预算** | 每阶段最多 2 次回溯质疑，超出进入 Master 汇总 |

---

## 五、Agent 调用模式

> 每个 Agent 在系统里"跑一次"到底是什么结构？这个问题直接影响 token 成本、延迟和稳定性。

### 5.1 三种调用模式对比

| 调用模式 | 描述 | token 成本 | 延迟 | 稳定性 | 适合 HiveMind？ |
|---------|------|-----------|------|-------|----------------|
| **Single-shot** | 一次 LLM 调用，直接生成 artifact | 最低 | 最低 | 最高 | ❌ 无引导空间 |
| **Multi-turn with user** | Agent 和用户多轮对话，启发式引导，最后产出 artifact | 中等 | 用户控制 | 高 | ✅ **HiveMind 的选择** |
| **Self-refinement loop** | LLM 自己生成 → 自己批评 → 自己修改，无人参与 | 最高 | 最高 | 最低 | ❌ 绕过人类确认，成本不可控 |

### 5.2 HiveMind 的调用模式：多轮人机对话

每个 Agent 的一次"运行"不是一次 LLM 调用，而是一段**与用户的多轮对话**：

```
Agent 启发式提问 → 用户回答 → Agent 深入/挑战 → 用户补充
    → ... （多轮）
    → Agent 产出 artifact → ✋ 人类确认点
```

**关键约束**：
- Agent **不会自己和自己对话**（no self-refinement loop）
- 每一轮都有用户参与，"循环"由用户控制，不是 Agent 控制
- 这天然避免了 autonomous loop 的 token 爆炸和 hallucination 累积问题

### 5.3 各 Agent 的典型对话轮次

| Agent | 典型轮次 | 说明 |
|-------|---------|------|
| Strategist | 5-10 轮 | 发散阶段需要更多对话来引导用户探索 |
| Product Manager | 3-6 轮 | 收敛阶段对话更聚焦 |
| UX + Prototyper | 3-8 轮 | 方案选择可能需要多次迭代 |
| Experience Critic | 1-2 轮 | 基于 UI AST 的结构化分析，对话较短 |
| Data Strategist | 1-3 轮 | 基于 PRD 的规则化分析，对话较短 |

### 5.4 对 token 成本的影响

```
每个 Agent 运行的 token 成本 ≈ 轮次 × (input_tokens + output_tokens)

其中 input_tokens 包括：
  - Agent system prompt（固定）
  - 上游 compressed_artifacts（由 Orchestrator 压缩）
  - 本轮对话历史（随轮次增长）

控制手段：
  - 上下文压缩（第七章）控制 compressed_artifacts 的大小
  - 对话轮次由 human_checkpoint 自然截断
  - 不存在无人参与的无限循环
```

---

## 六、Agent 间消息协议

### 5.1 结构化异议格式

> 质疑不是自由吐槽。每条异议必须包含：维度（在哪里）、证据（为什么）、建议（怎么改）。

```yaml
critique:
  from: architect
  to: strategist
  version: brief_v1
  dimension: unclear_objective       # 必须是 critique_scope 中定义的维度
  evidence: >
    Brief 中"提升用户留存"缺少量化定义。
    当前表述无法转换为可验证的需求约束。
  recommendation: >
    请将"提升留存"具体化为：哪类用户、哪个行为指标、目标值是多少。
  severity: high | medium | low
  requires_revision: true | false
```

### 5.2 版本化状态机

每次质疑必须导致版本升级或明确拒绝，不能只是"评论"：

```
brief_v1 → [PM critique] → brief_v2（修订）
         → [Master 仲裁]        → brief_v1_override（用户确认保留）
```

```yaml
version_event:
  artifact: product-brief
  from_version: v1
  to_version: v2
  trigger_critique_id: critique_arch_001
  changes_summary: >
    - 留存目标量化为：D30 留存率 ≥ 40%
    - 新增用户分层：首次用户 vs 回访用户分开定义
  status: published | draft | rejected
```

### 5.3 批判预算跟踪

```yaml
critique_budget:
  phase: architecture
  max_critiques: 2
  consumed: 1
  remaining: 1
  overflow_action: escalate_to_master
```

---

## 七、上下文压缩策略

> 串行系统最大的工程风险是 token 累积。随着上游输出成为下游输入，上下文越来越厚。

### 6.1 压缩规则

| 传递方向 | 压缩策略 |
|---------|---------|
| Strategist → PM | 只传 `structured_eval` + 假设树（不含完整 brief 正文） |
| PM → UX | 只传 PRD 核心对象模型 + `structured_eval`（不含全文） |
| UX → Experience Critic | 只传 `ui_ast`（不含 HTML 源码） |
| UX → Data Strategist | 只传 `ui_ast` + PRD 核心功能列表 |
| 所有 → Master | 只传各自的 `structured_eval` + critique 列表 |

### 6.2 摘要 Token 预算

```yaml
context_budget:
  max_tokens_per_agent_input: 8000
  structured_eval_priority: highest    # 评分数据永远优先传递
  full_text_threshold: 3000            # 超过则自动切换为摘要模式
  compression_model: same_as_agent     # 由同一 LLM 执行自压缩
```

### 6.3 Master 收集时的聚合格式

Master 不接收各 Agent 的完整输出文本，只接收结构化评估和冲突标记：

```yaml
master_input_bundle:
  session_id: string
  phase: design_validation
  agent_evals:
    strategist: { assumption_count: 6, problem_clarity_score: 7, ... }
    architect: { consistency_score: 8, scope_risk: medium, ... }
    ux_prototyper: { cognitive_load: medium, interaction_steps: 6, ... }
    experience_critic: { friction_count_high: 1, friction_count_medium: 3, ... }
    data_strategist: { unverifiable_flags: 2, tracking_coverage: partial, ... }
  critiques_log:
    - { from: experience_critic, severity: high, dimension: dead_end, ... }
    - { from: data_strategist, severity: medium, dimension: missing_metrics, ... }
  critique_budget_status:
    phase_critiques_consumed: 2
    overflow: false
```

---

## 八、质量保障与失败处理

### 7.1 输出质量检测（系统自动）

> 人类主导流程不意味着放弃质量把关。以下检测由系统自动执行，对用户透明。

| 检测项 | 判定标准 | 系统行为 |
|-------|---------|---------|
| 结构化 eval 缺失 | 输出中无 `structured_eval` 字段 | 要求 Agent 补充后再展示给用户 |
| 输出格式不合规 | 缺少必填字段（如 ui_ast 中无 transitions）| 返回 Agent 重新生成，附带格式模板 |
| 批判维度越界 | critique dimension 不在 `critique_scope` 中 | 丢弃越界内容，仅保留合规部分 |

### 7.2 质量提示（用户可见）

> 系统不自动阻断，但会向用户提示风险。

| 检测项 | 判定标准 | 提示方式 |
|-------|---------|---------|
| 置信度偏低 | `consistency_score < 6` 或 `problem_clarity_score < 5` | Master 提示："当前产出物的 X 指标偏低，建议拉 Y Agent 评审一下" |
| 批判预算即将耗尽 | consumed = max - 1 | Master 提示："还剩 1 次质疑机会，下一次质疑后将进入决策阶段" |
| 上下游版本不一致 | brief v2 但 PRD 仍基于 v1 | Master 提示："brief 已更新，PRD 可能需要同步" |

### 7.3 降级策略

```
正常状态：用户与 Agent 自由对话
          ↓
Agent 响应异常（超时/报错）：
  → 通知用户，保留上一轮有效输出
  → 建议用户换一种方式提问或切换 Agent
          ↓
多次失败：
  → Master 建议基于当前已有产出物继续推进
  → 标记未完成的环节，不阻断整体流程
```

---

## 九、决策记忆写回

> 用户的最终裁决不是纠错，是偏好表达。必须分类写入不同记忆层，避免过拟合。

### 8.1 决策分类规则

| 用户决策类型 | 写入位置 | 示例 |
|------------|---------|------|
| 修正错误事实 | Episodic | "不是 B2B，是 B2C2B 模型" |
| 表达长期偏好 | Semantic | "我们永远优先简洁性而非功能完整性" |
| 单次权衡覆盖 | Working Memory（会话级，不持久化）| "这次先保留复杂功能，下个版本再简化" |
| 接受已知风险 | Episodic + 风险标记 | "已知 Data Strategist 标记的可观测性问题，暂时接受" |

### 8.2 偏好权重调整

```yaml
user_preference_model:
  update_trigger: user_decision
  update_scope: semantic_layer
  fields:
    - simplicity_vs_completeness: float   # -1.0（完整）~ 1.0（简洁）
    - risk_tolerance: low | medium | high
    - ux_weight: float                    # UX 建议的历史接受率
    - data_weight: float                  # Data 建议的历史接受率

  master_usage: >
    Master 在生成推荐方案时，基于用户偏好权重对 A/B 选项排序。
    但不修改 Agent 的目标函数，只影响 Master 的推荐排序。

  immutable_principle: >
    Agent 目标函数永远稳定。
    用户偏好只影响 Master 的推荐权重，不影响 Agent 自身的批判逻辑。
```

---

## 十、Experience Agent 完整推理框架

### 9.1 输入模型

```yaml
experience_critic_input:
  required:
    ui_ast:                           # 来自 UX+Prototyper 的结构化输出
      pages: list
      transitions: list
    prd_summary:
      core_features: list
      primary_user_goal: string
  optional:
    user_persona: string              # 模拟用户类型
    task_definition: string           # 要模拟完成的任务
```

### 9.2 分析步骤（结构化 Prompt 模板）

```
你是 Experience Critic。你的任务是基于以下结构化 UI 模型，
执行认知结构验证分析。你不点击网页，你推理信息结构。

输入 UI AST：
{{ui_ast}}

核心用户目标：{{primary_user_goal}}

请按以下步骤执行分析：

Step 1 - 状态枚举
列出所有页面/状态节点，统计总数。

Step 2 - 决策点映射
对每个状态，统计用户需要做出选择的数量。
标记 decision_points > 3 的状态为"高决策压力"。

Step 3 - 主路径模拟
模拟一个首次使用的普通用户完成「{{primary_user_goal}}」。
以第一人称写出每一步："我进入页面，看到…，我不确定…，我尝试…"
统计完成所需步骤数。

Step 4 - 错误恢复路径
模拟用户在最可能出错的节点（必填项漏填、路径选择错误）出错后的恢复路径。
标记"无出口节点"和"不可逆操作"。

Step 5 - 认知负担规则检查
逐条检查以下规则：
- 单页面输入项 > 7：HIGH_BURDEN
- 并列主按钮 > 3：DECISION_CONFLICT
- 连续确认弹窗 > 2：FRICTION_HIGH
- 完成步骤数 > 8：PATH_TOO_LONG
- 缺少进度指示：ORIENTATION_LOST

Step 6 - 一致性扫描
检查：必填字段是否有标识、错误提示是否说明原因、
所有页面是否有返回路径、是否存在无出口页面。

输出格式：friction_report（结构化 YAML） + simulation_log（自然语言）
```

### 9.3 输出指标

```yaml
experience_critic_output:
  simulation_log:
    - step: integer
      user_action: string
      system_response: string
      friction_detected: boolean
      friction_note: string

  friction_report:
    - location: page_id
      type: cognitive_break | false_affordance | dead_end | ambiguous_transition | high_burden
      severity: low | medium | high
      rule_triggered: string          # 触发了哪条认知负担规则
      recommendation: string

  summary_metrics:
    total_states: integer
    total_decision_points: integer
    high_pressure_states: list        # decision_points > 3 的状态
    estimated_steps_primary_path: integer
    unreachable_states: list
    unrecoverable_states: list
    friction_count:
      high: integer
      medium: integer
      low: integer
    cognitive_load_flags: list        # 触发的规则列表
```

---

## 十一、系统设计原则总结

### 10.1 七条核心原则

1. **引导式工作流 + 人类确认点**：工作流有明确步骤，Agent 启发式引导用户推进。每个产出物、冲突、阶段转换都暂停等待用户确认——既不是自动管线，也不是自由对话。
2. **目标函数差异化**：Agent 之间必须优化不同目标，张力才是群体智能的来源。
3. **冲突即决策点**：Agent 间目标函数冲突时，系统暂停，把冲突压缩为 A/B 选项让用户选择。冲突不是 bug，是功能。
4. **批判维度限制**：质疑必须在 `critique_scope` 定义的维度内展开。
5. **版本化状态机**：每次质疑必须产生 v2 或明确拒绝，不能只是评论。
6. **Master 是协调者不是生成器**：Master 负责阶段交接、冲突呈现、最终汇总——不生成内容，不替用户做价值判断。
7. **预测权 ≠ 决策权**：系统可以预测用户偏好并标注"你可能倾向 B"，但裁决权永远属于用户。

### 10.2 健康系统的判断标准

```
✅ 工作流有明确步骤，用户知道"我在哪、下一步是什么"
✅ 每个产出物完成后暂停等待用户确认
✅ 每个冲突点呈现为 A/B 选项让用户选择
✅ Agent 目标函数稳定不变
✅ 每条质疑有明确的维度标签
✅ 每次质疑产出版本化结果
✅ Master 呈现冲突，不融合冲突
✅ 用户可以在任何确认点回溯
✅ 回溯不自动触发下游连锁更新
✅ 用户决策被分层写入记忆
✅ 偏好权重影响推荐排序，不影响 Agent 逻辑
✅ 上下文在阶段交接时压缩，防止 token 膨胀
```

### 10.3 警戒线

```
❌ 工作流自动跑完（用户在最后才看到结果）
❌ 用户需要自己决定"下一步找谁"（应由工作流引导）
❌ Agent 跳过确认点直接推进下一步
❌ 冲突被偷偷融合（Master 生成了折中版本）
❌ Master 生成了最终版本（退化为单 Agent）
❌ Agent 数量超过 7 个（超出可解释范围）
❌ Agent 目标函数随用户偏好变化（失去独立理性）
❌ 质疑无维度限制（退化为自由讨论）
❌ 回溯自动触发下游连锁更新（用户失去控制）
❌ 所有用户决策写入 Semantic（历史固化系统）
```

---

*文档版本：v2.3 | 作者：Rickon | 整理日期：2026-03-06*
