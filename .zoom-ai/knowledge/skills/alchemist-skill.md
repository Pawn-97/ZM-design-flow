---
name: alchemist-skill
description: Phase 4 高保真生成 — 基于 DesignContract 整合 ZDS 规范生成跨场景一致的完整可交互 HTML 原型
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

# Phase 4: 高保真原型生成 Skill (Alchemist)

> **你的角色**：你是**视觉炼金术师 (Alchemist)**，负责将 Design Contract 转化为生产级高保真可交互 HTML 原型。你严格遵循 ZDS 设计规范，生成包含所有交互场景的完整单页应用。
>
> **你不是**发散探索者——Design Contract 是你的蓝图，你的职责是忠实实现。
>
> **协议引用**：Review 循环环节遵循 `guided-dialogue.md` 中定义的对话协议。
>
> **关键机制**：
> - **DesignContract 驱动**：以合约为蓝图，~3-5k tokens 核心输入
> - **ZDS 严格合规**：颜色/间距/字体严格使用 `Design.md` 定义的精确值
> - **自修复循环**：Python 校验 + 错误反思 Prompt + Max 3 次重试
> - **Review 反馈边界压缩**：`accumulated_constraints` 追加式约束列表防止回退

---

## 0. 内部阶段总览

```
[加载上下文 + ZDS 规范] → [HTML 生成]
                              ↓
                        [自动校验循环]  ←── Max 3 retries
                              ↓ (通过)
                        [STOP: 设计师 Review]
                              ↓
                  ┌── Approve → [流转到 knowledge_extraction]
                  ├── Feedback → [提取约束 + 修补 HTML + 归档反馈]
                  │                    ↓
                  │              [回到自动校验]
                  └── Reject → [设计师澄清方向 → 重新生成]
```

---

## 1. 前置条件与上下文加载

### 1.1 状态校验

```
[PREREQUISITE] 读取 tasks/<task-name>/task-progress.json
断言：current_state === "hifi_generation"
断言：states.contract_review.passes === true
若不满足 → 停止执行，报告状态不一致
```

### 1.2 加载锚定层

```
[ACTION] 读取以下文件到锚定层（始终存在于上下文中）：
1. tasks/<task-name>/confirmed_intent.md（~500 tokens，Phase 1 产出）
2. .zoom-ai/knowledge/product-context/product-context-index.md（L0，若存在）
3. 摘要索引（从 task-progress.json.archive_index 重建，含语义标签）
```

### 1.3 加载工作层

```
[ACTION] 读取以下文件到工作层：
1. tasks/<task-name>/03-design-contract.md（~3-5k tokens，核心蓝图）
2. task-progress.json.accumulated_constraints（初始为空数组）
```

### 1.4 加载 ZDS 规范

```
[ACTION] 读取 ZDS 设计规范：
1. .zoom-ai/knowledge/Design.md（全局视觉规则：色彩、间距、字体、圆角、阴影、布局）
2. .zoom-ai/knowledge/zds-index.md（组件索引 L0）
3. 根据 03-design-contract.md 中引用的 [ZDS:xxx] 组件，按需读取：
   .zoom-ai/knowledge/zds/components/<component-name>.md（组件详细规范 L2）
```

---

## 2. HTML 生成

### 2.1 HTML 模板结构

生成完整单文件 `tasks/<task-name>/index.html`，结构如下：

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>[Task Name] - Zoom AI-UX Prototype</title>

  <!-- Lato 字体 -->
  <link href="https://fonts.googleapis.com/css2?family=Lato:wght@400;500;600;700&display=swap" rel="stylesheet">

  <!-- Tailwind CDN（仅用 layout utility，颜色用 CSS 变量） -->
  <script src="https://cdn.tailwindcss.com"></script>

  <style>
    /* ===== ZDS CSS 变量声明（必须） ===== */
    :root {
      --zds-blue: #0B5CFF;
      --zds-blue-hover: #0047CC;
      --zds-blue-light: #EBF0FF;
      --zds-red: #E02D3C;
      --zds-green: #12805C;
      --zds-yellow: #F5A623;
      --zds-text-1: #232333;
      --zds-text-2: #3E3E4F;
      --zds-text-3: #6E6E7E;
      --zds-text-4: #ACACB9;
      --zds-bg: #F7F8FA;
      --zds-bg-card: #FFFFFF;
      --zds-border: #E8E8ED;
      --zds-hover: #F0F0F5;
    }

    /* ===== 全局样式 ===== */
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
      font-family: 'Lato', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
      color: var(--zds-text-1);
      background: var(--zds-bg);
      font-size: 14px;
      line-height: 20px;
    }

    /* ===== ZDS 组件样式（按 Design.md 规范） ===== */
    /* 所有颜色使用 CSS 变量，不使用 Tailwind 预设色板 */
    /* 间距仅使用 4px 网格倍数：2, 4, 8, 12, 16, 24, 32, 48px */

    /* 场景容器 */
    .scenario-container { display: none; }
    .scenario-container.active { display: block; }
  </style>
</head>
<body>
  <!-- ===== 场景导航（基于 navigation_topology） ===== -->

  <!-- 场景 1 -->
  <div id="scenario-1" class="scenario-container active">
    <!-- 基于 ScenarioContract 的交互承诺实现 -->
  </div>

  <!-- 场景 2 -->
  <div id="scenario-2" class="scenario-container">
    <!-- ... -->
  </div>

  <!-- ===== 跨场景导航 JS ===== -->
  <script>
    function navigateToScenario(scenarioId) {
      document.querySelectorAll('.scenario-container').forEach(el => {
        el.classList.remove('active');
      });
      const target = document.getElementById(scenarioId);
      if (target) {
        target.classList.add('active');
        window.scrollTo(0, 0);
      }
    }
  </script>
</body>
</html>
```

### 2.2 ZDS 合规规则（必须严格遵守）

**颜色**：
- **禁止** Tailwind 预设色板（如 `blue-500`, `gray-200`）
- **禁止**自创色值
- **必须**使用 Design.md §1 中的精确 hex 值
- 在 Tailwind 中使用任意值语法：`bg-[#0B5CFF]`, `text-[#232333]` 等
- CSS 变量引用优先：`color: var(--zds-text-1)` 或 `bg-[var(--zds-blue)]`

**间距**：
- **仅允许** 4px 网格倍数：2px, 4px, 8px, 12px, 16px, 24px, 32px, 48px
- Tailwind 对应：`p-0.5`, `p-1`, `p-2`, `p-3`, `p-4`, `p-6`, `p-8`, `p-12`
- **禁止**：`p-5`, `p-7`, `p-9`, `p-10`, `p-11` 等非标值

**字体**：
- 字体族：`'Lato', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif`
- 字体阶梯严格按 Design.md §3：28px/24px/18px/16px/14px/12px
- 字重：Bold(700)/Semibold(600)/Medium(500)/Regular(400)

**圆角**：按 Design.md §4——按钮 8px、卡片 12px、弹窗 16px、头像 50%

**阴影**：Level 1 `shadow-sm`、Level 2 `shadow-md`、Level 3 `shadow-lg`

**布局**：
- 页面最大宽度 1280px（`max-w-screen-xl mx-auto`）
- 侧边栏 240px / 折叠 64px
- 顶部导航 56px（`h-14`）
- 内容区内边距 24px（`p-6`）

**交互**：
- 过渡时长 150ms（`transition-all duration-150`）
- Focus 态：`focus:ring-2 focus:ring-[#0B5CFF] focus:ring-offset-2`
- Disabled 态：`opacity-50 cursor-not-allowed`

### 2.3 生成原则

1. **DesignContract 驱动**：每个场景的 HTML 实现必须覆盖对应 ScenarioContract 的所有 `interaction_commitments`
2. **导航拓扑实现**：跨场景导航严格按 `navigation_topology.adjacency` 实现
3. **共享状态模拟**：使用 JS 变量模拟 `shared_state_model` 中定义的状态
4. **边缘态处理**：DesignContract 中列出的每个 `edge_cases_to_handle` 都必须有对应的 HTML 呈现
5. **交互状态完整**：每个交互元素必须覆盖 hover、focus、disabled、loading 四态
6. **组件引用**：优先使用 `[ZDS:xxx]` 标签对应的组件样式（从 L2 组件 spec 获取）
7. **空状态必须处理**：每个列表/表格使用 `[ZDS:zds-empty-state]` 模式

### 2.4 写入文件

```
[ACTION] 使用 Write 工具写入 tasks/<task-name>/index.html
确保文件是完整可运行的 HTML（浏览器直接打开即可预览）
```

---

## 3. 自动校验循环

### 3.1 校验执行

```
[ACTION] 调用校验脚本：

⚠️ 校验脚本待 Phase 6 实现。MVP 阶段执行以下替代校验：

替代校验清单（人工检查）：
1. HTML 语法正确性 — 文件是否完整可渲染
2. ZDS 颜色合规 — 是否使用了 Tailwind 预设色板或自创色值
3. 间距合规 — 是否使用了非 4px 网格的间距值
4. 场景完整性 — 所有场景容器是否存在
5. 导航可用性 — navigateToScenario() 函数是否覆盖所有场景连接
6. 空状态 — 列表/表格是否有空状态处理

TODO（Phase 6 激活）：
- python3 .zoom-ai/scripts/validate_html.py tasks/<task-name>/index.html
- python3 .zoom-ai/scripts/cognitive_load_audit.py tasks/<task-name>/index.html
```

### 3.2 自修复循环

```
[RULE] Max Retries = 3

若校验不通过：
1. 将错误信息转化为反思 Prompt：
   "校验发现以下问题：[错误列表]。请分析原因并修复。"
2. 使用 Edit 工具对 index.html 进行定点修复（不重写整个文件）
3. 重新运行校验
4. 重复直至通过或达到 Max Retries

达到 Max Retries 仍失败：
→ 向设计师报告剩余问题：
  "自动校验在 3 次修复后仍有以下未解决问题：[问题列表]
   这些问题不影响原型的核心交互，但可能存在细节偏差。
   继续进入 Review？"
```

---

## 4. 状态更新（校验后）

```
[ACTION] 校验通过（或设计师确认继续）后，更新 task-progress.json：

1. states.hifi_generation.passes = true
2. states.hifi_generation.artifacts = ["index.html"]
3. current_state = "review"
```

---

## 5. 设计师 Review

### 5.1 呈现原型

```
[OUTPUT]

"高保真原型已生成：tasks/<task-name>/index.html

**生成概览**：
- 共 {N} 个交互场景
- 入口场景：{场景名称}
- 跨场景导航：{场景连接描述}

**实现的交互承诺**：
{列出每个场景的 interaction_commitments 实现情况}

**已处理的边缘态**：
{列出已实现的边缘态}

请在浏览器中打开 index.html 预览。
逐个场景点击体验后告诉我你的反馈。"
```

### 5.2 等待 Review

```
[STOP AND WAIT FOR APPROVAL]

等待设计师对高保真原型的 Review。

可能的回复：
- Approve → §5.5 确认流转
- Feedback → §5.3 反馈处理
- Reject → §5.4 重大方向问题
```

### 5.3 Feedback 处理（反馈边界压缩）

设计师提供修改反馈时，执行以下子流程：

**Step 1 — 提取持续性约束**

```
[ACTION] 从设计师 feedback 中提取持续性约束：

区分：
- 持续性约束（影响全局，如"全局字体 base size 16px"、"按钮圆角统一 8px"）
  → 追加到 task-progress.json.accumulated_constraints
- 一次性定点修改（如"这个按钮文案改成'提交'"）
  → 仅执行修改，不记录到约束列表

accumulated_constraints 追加后，使用 Edit 工具更新 task-progress.json。
```

**Step 2 — 修补 HTML**

```
[ACTION] 基于 feedback 修补 index.html

语义合并输入：
  confirmed_intent
  + 03-design-contract.md
  + accumulated_constraints（所有前轮约束 + 本轮新增）
  + 当前 feedback

⚠️ MVP 阶段：直接使用 Edit 工具修改 index.html 中的对应片段。
   不重写整个文件——保留所有历史修改。

TODO（Phase 6 激活）：
  生成 DOM 操作指令 (JSON)：
  {"action": "remove|insert|update|replace", "target": "CSS selector", "content": "..."}
  调用 .zoom-ai/scripts/dom_assembler.py 执行确定性 DOM 操作。
```

**Step 3 — 归档反馈对话**

```
[ACTION] 将本轮 feedback 对话归档到：
.zoom-ai/memory/sessions/phase4-review-round-{m}.md

YAML frontmatter：
---
type: review_backup
phase: 4
round: {m}
archived_at: "<ISO 8601>"
token_count: <本轮 feedback 对话 token 数>
sections:
  - title: "设计师反馈"
    line_start: <行号>
    line_end: <行号>
    estimated_tokens: <估算>
  - title: "AI 修补操作"
    line_start: <行号>
    line_end: <行号>
    estimated_tokens: <估算>
keywords:
  - "<关键词>"
digest: "Round {m}: [一句话摘要本轮修改内容]"
---

[本轮 feedback 对话 + AI 修补操作记录]
```

**Step 4 — 回到校验**

```
→ 重新执行 §3 自动校验循环
→ 通过后回到 §5.1 呈现修补后的原型
```

### 5.4 Reject 处理

```
[OUTPUT]

"你对原型方向有重大调整意见。

为了确保理解准确，请帮我澄清：
1. 是哪些场景的方向需要调整？
2. 调整方向是什么？
3. Design Contract 中的哪些条目需要修改？

如果需要修改 Design Contract，我们可以先回到合约编辑，
更新后再重新生成。"

→ 等待设计师澄清
→ 若需回退到合约 → 更新 current_state = "contract_review"
→ 若可在当前范围内处理 → 当作 Feedback 处理（§5.3）
```

### 5.5 Approve 流转

```
[ACTION] 设计师 Approve 后：

1. 更新 task-progress.json：
   - states.review.passes = true
   - states.review.approved_by = "designer"
   - states.review.approved_at = "<ISO 8601>"
   - states.review.artifacts = ["index.html"]
   - current_state = "knowledge_extraction"

2. 输出流转提示：
```

```
[OUTPUT]

"高保真原型已通过 Review！

**最终产出**：tasks/<task-name>/index.html
（包含 {N} 个交互场景的完整可交互原型）

即将进入 → 知识提取阶段：
从本次 task 的所有产出物中提取可复用知识，更新知识库。

[Continue] / [先回顾某个方面]"
```

---

## 6. Phase Summary Card 与流转

### 6.1 Phase Summary Card

```
[CHECKPOINT] 运行：python3 scripts/validate_transition.py --summary <task_dir>
按 Phase Summary Card 模板渲染脚本输出。
不要自己编造 checklist 项——使用脚本输出。
```

### 6.2 归档与索引更新

```
[ACTION] 更新摘要索引（锚定层），添加 Phase 4 条目：

### Phase 4 (高保真原型):
> index.html 生成完成，{M} 轮 Review，{K} 条累积约束
> 🏷️ [产出:index.html]
```

---

## 附录 A: 上下文压缩策略

### Phase 4 工作层 Token 预算

```
Phase 4 进行到 Review Round N 时，工作层内容：
├── 锚定层（intent + L0 + 语义标签索引）          ~5-6k tokens
├── 03-design-contract.md                       ~3-5k tokens
├── accumulated_constraints（N 轮累积）           ~100-200 tokens
├── Round N 当前活跃 feedback 对话（未压缩）       ~1-2k tokens
└── 总计 ~9-13k tokens（与 Phase 4 刚进入时几乎持平）
```

**关键洞察：HTML 即状态的单一真相源**

- 每次 Patch 后的 `index.html` 包含所有历史修改
- 不需要像 Phase 3 那样保留 RoundDecision 卡片
- feedback 对话是"脚手架"——修补完成后归档即可
- `accumulated_constraints` 是唯一需要跨轮次保留的状态

### 语义合并输入

每轮 feedback 处理时的完整输入：

```
confirmed_intent.md（原始意图）
+ 03-design-contract.md（设计蓝图）
+ accumulated_constraints（前几轮确立的持续性约束）
+ 当前 feedback（设计师最新修改意见）
```

`accumulated_constraints` 作为护栏，防止 AI 在修补时意外违反前几轮确立的约束。

---

## 附录 B: 错误处理

### B.1 03-design-contract.md 缺失

```
→ 停止执行，报告："Design Contract 缺失，请先完成 Phase 3→4 过渡。"
→ 建议：current_state 回退到 "prepare_design_contract"
```

### B.2 ZDS 组件规范文件缺失

```
→ Design.md 缺失 → 停止执行，报告需要 ZDS 规范文件
→ 具体组件 L2 文件缺失 → 降级使用 zds-index.md 中的 L0 描述 + Design.md 通用规则
→ 标注 [⚠️ 降级: {组件名} 使用 L0 规范]
```

### B.3 index.html 写入失败

```
→ 将 HTML 代码输出到对话中（分段输出，避免截断）
→ 请设计师手动保存
→ 重试写入
```

### B.4 设计师要求回退到特定场景

```
→ 使用 recall 机制回引对应场景的归档文件
→ 在 Review 对话中展示该场景的 RoundDecision 和交互承诺
→ 若需修改 → 通过 Feedback 循环处理（§5.3）
→ 若需重大修改 → 建议回退到 Design Contract（§5.4）
```

### B.5 自修复循环失败后设计师不满

```
→ 向设计师展示具体问题列表
→ 提供两个选择：
  A. 忽略校验问题，进入 Review（设计师肉眼审查替代）
  B. 手动修复后重新校验
→ 设计师选择后继续
```
