# HiveMind 代码实现分析 & LangGraph 改进方案

> **文档状态**：分析报告 | 日期：2026-03-10
> **基于**：hivemind 代码库现状 + PRD v4 + 设计规格 v2.3
> **目的**：全面审计多 Agent 工作流实现完成度，提出 LangGraph 改进方案

---

## 修改原因

当前代码的多 Agent 工作流**纯靠大模型提示词控制**，核心流程依赖 LLM 遵循特定输出格式（五反引号 filepath 块、嵌入 structured_eval JSON 等）。这套方案存在根本性缺陷：

1. **极不稳定**：LLM 输出格式稍有偏差（换了文件名、少了反引号、JSON 格式变化），整个产出物检测和 Checkpoint 触发链路就会断裂
2. **复杂工作流无法实现**：循环（Agent 多轮修改→重新验证）、有状态的阶段推进、HITL（Human-in-the-Loop）暂停/恢复、人机干预后的条件分支——这些用提示词工程根本无法可靠实现
3. **调试困难**：7 环节的 dispatch 链路（checkpoint-action → advanceStep → push event → store → React effect → createChat → LLM stream），任何一环出问题都导致工作流卡死，且难以定位

**结论**：需要引入 LangGraph 作为确定性编排引擎，将工作流控制从"LLM 提示词驱动"转变为"图状态机驱动"。

---

## 一、代码实现 vs PRD v4 对照分析

### 技术栈概览

| 层 | 技术 |
|---|---|
| 桌面框架 | Electron 35 |
| 前端 | React 19 + Zustand 5 + Tailwind |
| 数据库 | better-sqlite3 |
| LLM | Vercel `ai` SDK + 自封装 Provider |
| 构建 | electron-vite |

### 1.1 已实现的部分 ✅

以下 PRD 需求在代码中有对应实现：

| PRD 需求 | 实现位置 | 完成度 |
|---------|---------|--------|
| FR-W1 Phase 状态机管理 | `orchestrator.ts` 单例 + DB 持久化 | ✅ 完整 |
| FR-W2 Human Checkpoint 检测与暂停 | `triggerCheckpoint()` + 4 种 trigger_type | ✅ 完整 |
| FR-W3 Agent 路由 | `PHASE_STEPS` step-level routing | ✅ 完整 |
| FR-W4 产出物版本追踪 | `artifact-manager.ts` version 递增 + superseded | ✅ 完整 |
| FR-W5 上下文压缩与预算控制 | `context-compressor.ts` 8000 token budget | ⚠️ 有缺陷 |
| FR-W6 批判预算跟踪 | `critique-budget.ts` max=2, escalate_to_master | ✅ 完整 |
| FR-W8~W10 Checkpoint 机制 | confirm/edit/challenge/rollback + DB 恢复 | ✅ 完整 |
| FR-W16~W18 结构化异议协议 | `validateCritique()` + scope 校验 + 越界丢弃 | ✅ 完整 |
| FR-A1 6 个 Agent YAML 规格 | `agents.ts` 加载所有增强字段 | ✅ 完整 |
| FR-A2 多轮对话防护 | `awaitingUserInput` flag | ✅ 完整 |
| FR-A3 Agent 目标函数稳定 | `[Agent Core Objectives — Immutable]` 注入 | ✅ 完整 |
| FR-A4 structured_eval 验证 | validate + retry prompt | ⚠️ 不够可靠 |
| FR-AT1~AT4 工具注入与执行 | `tool-registry.ts` + `llm.ts` 分发 | ⚠️ write_file 被替换 |
| IPC 通道体系 | `workflow.ts` 全部 handler 已实现 | ✅ 完整 |
| Push 事件系统 | `workflow-push.ts` 8+ 种事件 | ✅ 完整 |
| Workflow Store | Zustand + push listeners | ✅ 完整 |
| 冲突检测 | `conflict-detector.ts` compareStructuredEvals | ⚠️ 过于机械 |
| 冲突解决 | `resolveConflict()` + UI conflict cards | ✅ 基本完整 |
| 产出物 Diff | `getArtifactDiffContent()` | ✅ 完整 |
| Challenge 评审 | reviewer agent dispatch + context 注入 | ✅ 完整 |

### 1.2 已实现但有严重缺陷的部分 ⚠️

#### 缺陷 1：产出物输出依赖 LLM 遵循特定格式（最大痛点）

当前实现要求 LLM 用五个反引号输出 filepath 格式：

```
`````filepath:_output/finding.md
<content>
`````
```

整个产出物检测链路是：
1. System Prompt 要求 LLM 用 `` `````filepath:_output/xxx.md `` 格式输出
2. 前端检测流内容中的 filepath 模式
3. 提取内容后保存文件
4. 保存后调用 `registerArtifact` 注册版本
5. 注册后触发 checkpoint

**问题**：LLM 经常不遵循这个格式——用三个反引号而非五个、用不同文件名、省略 filepath 前缀、或者在内容中嵌套代码块导致提前截断。这是**系统中最脆弱的环节**。

#### 缺陷 2：structured_eval 提取靠正则匹配

`extractStructuredEval()` 从 LLM 文本中用正则 `/```json\s*([\s\S]*?)```/i` 匹配 JSON 代码块。LLM 稍有格式变化就提取失败，导致 artifact 注册因 `validateStructuredEval` 校验失败而中断。

#### 缺陷 3：冲突检测过于粗糙

`compareStructuredEvals()` 只做字面值对立检测（`high/low`、`true/false`、`required/optional` 等硬编码对立对），无法检测真正的语义级冲突（如"PM 认为功能 X 应该删减 vs Strategist 认为功能 X 是核心假设"）。大多数真实冲突检测不到。

#### 缺陷 4：上下文压缩假设中文标题

`extractMarkdownSection()` 依赖产出物中有精确的中文 `##` 标题（"假设树"、"核心发现"、"核心对象模型"等），但 LLM 可能用英文或不同措辞输出，导致章节提取全部失效。

#### 缺陷 5：Agent Dispatch 链路太长

工作流推进的完整链路有 **7 个环节**：

```
checkpoint-action → advanceStep/advancePhase
  → sendWorkflowPush(state-updated + agent-dispatched)
    → Renderer: workflow store listener
      → set pendingDispatch
        → App.tsx useEffect 检测 pendingDispatch
          → selectAgent() + createChat()
            → 发送初始消息到新 Agent
              → LLM stream 开始
```

任何一个环节出问题都会导致工作流卡住，且难以定位具体是哪一步失败。

#### 缺陷 6：web_search 是 stub

`executeWebSearch()` 返回空结果，Strategist 在 Phase 1 需要做竞品分析但搜索工具实际不可用。

### 1.3 完全未实现的部分 ❌

| PRD 模块 | 状态 | 说明 |
|---------|------|------|
| 模块 3: Party Mode (FR-P1~P6) | ❌ 未实现 | 多 Agent 群聊 |
| 模块 5: Skills 系统 (FR-S1~S8, FR-AT5~AT8) | ❌ 未实现 | 技能创建/管理/调用 |
| 模块 7: TELOS 引导 (FR-T1~T7) | ❌ 未实现 | 首次使用向导 |
| FR-W7: 失败自动恢复 | ❌ 仅 report | 无自动重试/降级 |
| FR-W11: 回滚同步提示 | ❌ 未实现 | 获取了 downstream list 但无 Master 提示 |
| FR-W13: Master 语义压缩 A/B/C | ❌ 硬编码 | 选项是代码模板，非 Master LLM 生成 |
| FR-W14: 偏好推荐排序 | ❌ 未实现 | 无用户偏好模型 |
| FR-M1~M4: 记忆与工作流集成 | ❌ 未实现 | 决策写回/偏好更新 |
| FR-AP3: discoverModels() | ❌ 未实现 | 模型列表硬编码 |
| FR-TC6~TC8: Skill 工具卡片 | ❌ 未实现 | Skills 系统缺失 |
| phase_transition 卡片 | ❌ 未实现 | Phase 切换 UI 提示 |

---

## 二、核心问题总结

每次测试都遇到新问题的**根本原因**：

> **当前架构把太多关键决策点委托给了 LLM 的输出格式遵从性，没有确定性的编排引擎来保障流程的可靠推进。**

### 5 个致命问题

| # | 问题 | 影响 | 根因 |
|---|------|------|------|
| 1 | **产出物检测靠 LLM 输出特定格式** | 格式不对就失败，artifact 无法注册，checkpoint 不触发 | 提示词驱动，无确定性保障 |
| 2 | **structured_eval 提取靠正则匹配** | JSON 格式稍变就失败，artifact 注册被 validate 拦截 | 依赖 LLM 文本格式 |
| 3 | **冲突检测只做字面值对比** | 大多数真实语义冲突检测不到 | 缺少 LLM-powered 冲突分析 |
| 4 | **上下文压缩假设中文标题** | 标题不匹配则章节提取全部失效 | 硬编码假设，不适应 LLM 输出 |
| 5 | **7 环节 dispatch 链路** | 任何一环断裂工作流就卡死 | 编排逻辑跨 IPC 分散，无单一控制中心 |

### 无法实现的能力

当前纯提示词驱动的架构根本无法可靠实现以下能力：

- **循环**：Agent 修改产出物 → 重新验证 → 不通过再修改（没有图结构支持循环边）
- **条件分支**：用户选择 rollback 后，根据回退目标动态选择重新执行的 Phase
- **并行**：Phase 4 的 Experience Critic 和 Data Strategist 并行执行（当前只能串行）
- **有状态暂停/恢复**：用户关闭应用 3 天后回来，精确恢复到上次暂停的 Agent 对话
- **人机干预后的分支路由**：用户在 Checkpoint 选择 challenge 后，动态路由到 reviewer agent，review 完成后再回到原始 checkpoint

---

## 三、LangGraph 改进方案

### 3.1 为什么选 LangGraph

在调研了 GitHub 上所有主流多 Agent 框架（CrewAI、AutoGen/AG2、OpenAI Agents SDK、Microsoft Agent Framework、OVADARE 等）后，**LangGraph 是与 HiveMind 需求匹配度最高的框架**：

| HiveMind 核心需求 | LangGraph 支持 | CrewAI | AG2/AutoGen |
|-----------------|---------------|--------|-------------|
| 图驱动状态机（5 Phase） | ✅ 原生 DAG | ⚠️ 仅 Sequential/Hierarchical | ❌ 对话式 |
| Human-in-the-Loop 暂停/恢复 | ✅ `interrupt()` + `Command(resume=)` | ⚠️ 有限 | ⚠️ 开发中 |
| Checkpoint 持久化（崩溃恢复） | ✅ 内置 Checkpointer | ❌ 无 | ⚠️ 开发中 |
| Rollback 回退 | ✅ Platform 原生支持 | ❌ 无 | ❌ 无 |
| 条件分支（challenge/rollback/confirm） | ✅ 条件边 + Command(goto=) | ⚠️ 有限 | ❌ 弱 |
| 并行执行（Phase 4 双 Agent） | ✅ 并行节点 | ⚠️ 有限 | ⚠️ 有限 |
| Supervisor 模式（Master） | ✅ langgraph-supervisor 库 | ⚠️ Hierarchical | ✅ GroupChat |
| 循环（修改→重新验证） | ✅ 图支持循环边 | ❌ 无 | ⚠️ 有限 |
| 结构化输出 | ✅ Pydantic Schema 强制 | ⚠️ 不原生 | ⚠️ 不原生 |
| 生产就绪度 | ⭐⭐⭐⭐⭐ v1.0 GA | ⭐⭐⭐⭐ | ⭐⭐ |

### 3.2 LangGraph 能解决什么

| 当前问题 | LangGraph 方案 |
|---------|---------------|
| 产出物格式依赖 LLM | **结构化输出 + Tool Calls**：用 LangGraph 的 tool_calls 让 LLM 调用 `save_artifact` tool，输出 schema 由代码强制，不再依赖文本格式 |
| 7 环节 dispatch 链路 | **图状态机**：Phase/Step 转换是确定性的图边，状态转换在单一进程内完成，不需要跨 IPC 的长链路 |
| Checkpoint 暂停/恢复不可靠 | **原生 `interrupt()`**：在任意图节点暂停，Checkpointer 自动持久化状态，用户确认后 `Command(resume=value)` 恢复 |
| 回滚机制脆弱 | **原生 rollback**：回退到之前的 checkpoint state，无需手动管理下游 artifact |
| structured_eval 不可靠 | **Structured Output**：用 Pydantic/Zod schema 强制 LLM 返回结构化 JSON，编译期保证类型安全 |
| 冲突检测过于机械 | **专用冲突检测节点**：在图中插入 LLM-powered 冲突分析节点，做语义级冲突检测 |
| 状态管理分散（内存 Map + DB + Store） | **统一 State Schema**：所有工作流状态在一个 TypedDict 中，图的每个节点读写同一 State |
| 无法实现循环和并行 | **图原生支持**：循环边（修改→验证→不通过→再修改）、并行节点（Phase 4 双 Agent）|

### 3.3 推荐架构

```
当前架构（提示词驱动，不稳定）:
┌──────────────────────────────────────────┐
│  Renderer (React + Zustand)               │
│  ← IPC Push ← Main Process               │
│                 ├── Orchestrator (手写)     │  ← 状态机逻辑分散
│                 ├── LLM Provider           │  ← 产出物靠提示词格式
│                 ├── conflict-detector      │  ← 只做字面值对比
│                 └── SQLite                 │
└──────────────────────────────────────────┘
问题：编排逻辑跨 IPC 分散在 7 个环节，LLM 格式不对就全链路断裂

改进架构（LangGraph 图状态机驱动）:
┌──────────────────────────────────────────┐
│  Renderer (React + Zustand)               │
│  ← SSE/WebSocket ←─┐                     │
│                     │                     │
│  Electron Main Process                    │
│  ├── LangGraph Engine ◄── 单一编排中心     │
│  │   ├── StateGraph（5 Phase 图定义）      │
│  │   │   ├── Phase1: Strategist Nodes    │
│  │   │   ├── Phase2: PM Nodes            │
│  │   │   ├── Phase3: UX Nodes            │
│  │   │   ├── Phase4: Critic + Data       │  ← 可并行
│  │   │   ├── Phase5: Master Node         │
│  │   │   ├── conflict_check Node         │  ← LLM 语义冲突检测
│  │   │   └── 条件边 + 循环边              │  ← 原生支持
│  │   ├── Checkpointer（暂停/恢复/回滚）    │  ← 内置，不用手写
│  │   └── interrupt()（Human Checkpoint）   │  ← 确定性暂停
│  │                                        │
│  ├── 文件系统（产出物读写）                  │  ← 保留
│  ├── SQLite（本地数据）                     │  ← 保留
│  └── 记忆系统（现有实现）                    │  ← 保留
└──────────────────────────────────────────┘
优势：编排逻辑集中在 StateGraph，状态转换确定性执行，不依赖 LLM 格式
```

### 3.4 LangGraph 图设计（对应 5-Phase 工作流）

```
START
  │
  ▼
[strategist_1_1] ──interrupt()──► 用户确认 ──confirm──►
  │                                         ──edit────► (原地重试)
  │                                         ──challenge► [conflict_check]
  │                                         ──rollback─► (边界保护)
  ▼
[strategist_1_2] ──interrupt()──► 用户确认 ──confirm──►
  │
  ▼
[strategist_1_3] ──interrupt()──► 用户确认 ──confirm──►
  │
  ▼
[pm_2_1] ──interrupt()──► 用户确认 ──confirm──►
  │
  ▼
[pm_2_2] ──interrupt()──► 用户确认 ──confirm──►
  │                                  ──challenge► [conflict_check] ──► [pm_2_2]
  ▼
[ux_3_1] ──interrupt()──► 用户确认 ──confirm──►
  │
  ▼
[ux_3_2] ──interrupt()──► 用户确认 ──confirm──►
  │
  ▼
┌─────────────┐
│  并行执行     │
│ [critic_4_1] │──interrupt()──► 用户确认
│ [data_4_2]   │──interrupt()──► 用户确认
└──────┬──────┘
       │  ──rollback──► [ux_3_2] (回 Phase 3 修改)
       ▼
[master_5_1] ──interrupt()──► 用户逐项裁决
  │
  ▼
[master_5_2] ──interrupt()──► 用户最终确认
  │
  ▼
 END
```

每个节点内部：
1. 与用户多轮对话（LLM Agent）
2. 产出 artifact（通过 tool_calls，非文本格式）
3. 返回 structured_eval（Pydantic schema 强制，非正则提取）
4. `interrupt()` 暂停等待用户确认
5. 根据用户选择路由到下一节点

### 3.5 实施方式建议

**推荐方案：LangGraph.js（TypeScript 原生）**

使用 `@langchain/langgraph` JS/TS SDK，直接在 Electron Main Process 中运行，完全替代现有的 `orchestrator.ts`、`phase-runner.ts`、`conflict-detector.ts`。

| 保留的模块 | 替换的模块 | 新增的模块 |
|-----------|-----------|-----------|
| `artifact-manager.ts`（版本管理） | `orchestrator.ts` → StateGraph | LangGraph StateGraph 定义 |
| `context-compressor.ts`（压缩逻辑） | `phase-runner.ts` → 图节点 | Checkpointer 配置 |
| 记忆系统全部保留 | `conflict-detector.ts` → LLM 节点 | Structured Output Schema |
| `tool-registry.ts`（工具定义） | 7 环节 dispatch 链路 → 图边 | interrupt() 集成层 |
| SQLite + 前端 Store | 手写 Checkpoint 持久化 → 内置 | SSE/Event 推送层 |

**选择理由**：
- 技术栈统一（全 TypeScript），无需打包 Python 环境
- 可渐进式迁移，逐步替换而非推翻重写
- 保持桌面应用的离线能力
- LangGraph.js 已支持 StateGraph、interrupt、Checkpointer 等核心功能

### 3.6 预期改进收益

| 指标 | 当前状态 | LangGraph 后 |
|------|---------|-------------|
| 产出物格式错误率 | 每次测试高概率遇到 | **趋近 0**（tool_calls 强制 schema） |
| Checkpoint 触发失败 | 7 环节链路随时断裂 | **趋近 0**（原生 interrupt，确定性暂停） |
| 工作流卡死排查成本 | 需逐环节 debug | **极低**（图有明确的当前节点和状态快照） |
| 崩溃恢复可靠性 | 自己实现的 DB+Map 双写 | **内置**（Checkpointer 自动持久化） |
| 冲突检测准确度 | 仅字面值对立 | **语义级**（LLM-powered 冲突分析节点） |
| 循环/并行/条件分支 | 无法实现 | **原生支持**（图边、并行节点、条件路由） |
| structured_eval 可靠性 | 正则提取，经常失败 | **100%**（Structured Output schema 强制） |

---

*文档版本：v1.0 | 作者：AI 分析 | 日期：2026-03-10*
