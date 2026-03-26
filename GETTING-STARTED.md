# HarnessDesign 使用手册

> 面向 UX 设计师的全流程指南。不需要任何编程或 Git 基础。

---

## 目录

1. [安装前准备](#1-安装前准备)
2. [为新项目安装工作流](#2-为新项目安装工作流)
3. [日常使用](#3-日常使用)
4. [多项目管理与切换](#4-多项目管理与切换)
5. [更新工作流](#5-更新工作流)
6. [移除工作流](#6-移除工作流)
7. [常见问题](#7-常见问题)

---

## 1. 安装前准备

你需要先安装三样东西：**Git**、**Python** 和 **Claude Code**（或 Codex）。已安装的可以跳过。

> **怎么打开终端？** Mac 按 `Cmd + 空格`，输入 `终端` 或 `Terminal`，回车。

### 1.1 安装 Git

在终端输入：

```
git --version
```

如果显示版本号（如 `git version 2.x.x`），跳过。如果提示找不到命令：

- **Mac**：终端会自动弹窗提示安装 Xcode Command Line Tools，点 **Install** 即可
- **Windows**：访问 https://git-scm.com/downloads 下载安装

### 1.2 安装 Python

在终端输入：

```
python3 --version
```

如果显示 `Python 3.10.x` 或更高版本，跳过。否则：

1. 访问 https://www.python.org/downloads/
2. 点击黄色的 **Download Python 3.x.x** 按钮
3. 双击安装包，一路点 **Continue** → **Install**
4. **关闭终端再重新打开**，再次运行 `python3 --version` 确认

### 1.3 安装 Claude Code

> 如果你用 Codex，跳到 [1.4](#14-安装-codex替代方案)。

1. 访问 https://docs.anthropic.com/en/docs/claude-code
2. 按照页面指引安装
3. 在终端输入 `claude --version`，能看到版本号说明成功

### 1.4 安装 Codex（替代方案）

1. 访问 https://openai.com/index/introducing-codex/
2. 按照页面指引安装
3. 在终端输入 `codex --version` 确认

---

## 2. 为新项目安装工作流

> **核心概念**：每个设计项目有自己的文件夹。工作流安装到项目文件夹中，所有产出（PRD 分析、调研报告、线框图、原型）都在这个文件夹里。

### 一键安装

把下面这行命令**整行**复制粘贴到终端，把末尾的路径换成你的项目文件夹：

```
curl -fsSL https://raw.githubusercontent.com/Pawn-97/harnessurdesign-UX-flow/main/install.sh | bash -s -- ~/Desktop/我的项目名
```

**举个例子**：如果你要做一个 Spam Dashboard 项目，就运行：

```
curl -fsSL https://raw.githubusercontent.com/Pawn-97/harnessurdesign-UX-flow/main/install.sh | bash -s -- ~/Desktop/spam-dashboard
```

安装脚本会自动：
- 下载工作流引擎文件
- 安装 Python 依赖
- 配置 Claude Code（自动禁用无关插件）
- 运行完整性验证

看到 **安装成功！** 字样就说明一切就绪。

> **遇到问题？**
> - `git: command not found` → 回到 [1.1 安装 Git](#11-安装-git)
> - `Permission denied` 或 `Repository not found` → 联系 GuanchengDing 获取仓库访问权限
> - `pip3: Permission denied` → 在终端运行 `sudo pip3 install -r .harnessdesign/scripts/requirements.txt`（输入电脑密码）

---

## 3. 日常使用

### 3.1 启动新任务

打开终端，进入你的项目文件夹：

```
cd ~/Desktop/spam-dashboard
```

启动 Claude Code：

```
claude
```

> 用 Codex 的话，把 `claude` 换成 `codex`。

在 AI 对话界面中输入：

```
/harnessdesign-start --prd path/to/your-prd.md
```

> **小技巧**：不知道文件路径？把 PRD 文件直接**拖拽**到终端窗口，路径会自动填入。
>
> 你也可以先把 PRD 文件放到项目文件夹里，然后直接写文件名：
> `/harnessdesign-start --prd my-prd.md`

**首次启动**会进入 Onboarding（Phase 0），AI 会引导你建立产品知识库。同一产品的后续任务会跳过这一步。

### 3.2 工作流四个阶段

| 阶段 | 做什么 | 你需要做什么 |
|------|--------|-------------|
| Phase 1: 上下文对齐 | AI 和你对齐对 PRD 的理解 | 回答问题、确认共识 |
| Phase 2: 调研 + JTBD | AI 引导你做用户调研和任务分析 | 参与讨论、确认洞察 |
| Phase 3: 交互设计 | AI 和你逐场景设计交互方案 | 审阅方案、给反馈 |
| Phase 4: 高保真原型 | AI 生成符合设计系统的 HTML | 审阅原型、指导修改 |

每个阶段结束时，AI 会等你确认（你会看到 `[STOP AND WAIT FOR APPROVAL]`）。**你随时可以说"不"或提出修改意见**——AI 是你的共创伙伴，不是决策者。

### 3.3 中途离开和恢复

可以随时关闭终端。下次回来时：

```
cd ~/Desktop/spam-dashboard
```

```
claude
```

进入对话后输入：

```
/harnessdesign-resume
```

AI 会自动恢复到你上次离开的位置。

### 3.4 查看当前状态

在对话中输入：

```
/harnessdesign-status
```

### 3.5 你的项目文件夹里有什么

任务完成后，项目文件夹的结构大致是这样的：

```
~/Desktop/spam-dashboard/
├── my-prd.md                      ← 你的 PRD 原文
├── tasks/
│   └── spam-dashboard/
│       ├── confirmed_intent.md    ← Phase 1: 对齐共识
│       ├── 00-research.md         ← Phase 2: 调研报告
│       ├── 01-jtbd.md             ← Phase 2: 用户任务分析
│       ├── 02-structure.md        ← Phase 3: 交互方案总表
│       ├── 03-design-contract.md  ← Phase 3→4: 设计合约
│       ├── wireframes/            ← Phase 3: 黑白线框 HTML
│       └── index.html             ← Phase 4: 高保真原型 ★
├── .harnessdesign/                ← 工作流引擎（不用管）
├── scripts/                       ← 验证脚本（不用管）
└── CLAUDE.md / AGENTS.md          ← AI 配置（不用管）
```

你最终需要的产出物主要是 `tasks/<任务名>/` 下的文件。

---

## 4. 多项目管理与切换

### 4.1 创建新项目

每个项目独立安装，互不影响。再运行一次安装命令，换个文件夹名即可：

```
curl -fsSL https://raw.githubusercontent.com/Pawn-97/harnessurdesign-UX-flow/main/install.sh | bash -s -- ~/Desktop/新项目名
```

比如你同时在做三个项目：

```
~/Desktop/spam-dashboard/       ← Spam Dashboard 项目
~/Desktop/meeting-scheduler/    ← Meeting Scheduler 项目
~/Desktop/user-onboarding/      ← User Onboarding 项目
```

### 4.2 在项目之间切换

切换项目就是切换文件夹。**关闭当前的 AI 对话**（按 `Ctrl + C` 或直接关闭终端），然后：

```
cd ~/Desktop/另一个项目名
```

```
claude
```

```
/harnessdesign-resume
```

AI 会读取这个项目文件夹中的 `task-progress.json`，自动恢复到该项目上次的位置。

> **重要**：不要在同一个终端窗口直接 `cd` 到另一个项目再启动 claude——先退出当前 claude 会话。

### 4.3 查看所有项目状态

在终端中运行（不需要进入 claude）：

```
for d in ~/Desktop/*/tasks/*/task-progress.json; do
  echo "📁 $(dirname $(dirname $d))"
  python3 -c "import json; d=json.load(open('$d')); print(f'   状态: {d[\"current_state\"]}')"
  echo ""
done
```

这会列出桌面上所有安装了 HarnessDesign 的项目及其当前状态。

---

## 5. 更新工作流

当 GuanchengDing 通知有新版本时，对**每个项目**重新运行安装命令：

```
curl -fsSL https://raw.githubusercontent.com/Pawn-97/harnessurdesign-UX-flow/main/install.sh | bash -s -- ~/Desktop/spam-dashboard
```

安装脚本会：
- 更新引擎文件（skills、scripts、设计系统规范）
- **不会覆盖**你的任务数据（`tasks/`）、知识库（`product-context/`）和对话归档（`memory/`）
- 不会覆盖你自定义过的 `CLAUDE.md` / `AGENTS.md`
- 重新验证安装完整性

> **或者在 AI 对话中更新**：进入项目的 claude 会话后输入 `/harnessdesign-update`

---

## 6. 移除工作流

### 移除单个项目

```
rm -rf ~/Desktop/spam-dashboard
```

> **想保留产出物？** 先把 `tasks/` 目录中需要的文件复制到别处。

### 只移除工作流引擎（保留项目文件）

如果项目文件夹里还有其他你的文件，只移除工作流部分：

```
cd ~/Desktop/spam-dashboard
rm -rf .harnessdesign scripts .claude CLAUDE.md AGENTS.md tasks
```

---

## 7. 常见问题

### Q: 安装命令提示 "curl: command not found"

Mac 自带 curl，一般不会出现这个问题。如果出现，先安装 Xcode Command Line Tools：

```
xcode-select --install
```

### Q: `Permission denied` 或 `Repository not found`

你需要 GitHub 仓库的访问权限。联系 GuanchengDing 把你的 GitHub 账号加入项目。

如果你没有 GitHub 账号：
1. 访问 https://github.com/signup 注册
2. 把你的用户名发给 GuanchengDing

### Q: `pip3 install` 提示 "Permission denied"

在命令前加 `sudo`：

```
sudo pip3 install -r .harnessdesign/scripts/requirements.txt
```

系统会要求你输入电脑登录密码（输入时屏幕不会显示任何字符，这是正常的），输完按回车。

### Q: Claude Code 里出现奇怪的 "Vercel"、"React" 建议

安装脚本已自动禁用无关插件。如果仍然出现，检查项目文件夹下是否有 `.claude/settings.json`：

```
cat ~/Desktop/你的项目/.claude/settings.json
```

如果不存在，重新运行安装命令。

### Q: 工作流卡住了，AI 不响应

1. 关闭终端
2. 重新打开终端
3. `cd ~/Desktop/你的项目 && claude`
4. 输入 `/harnessdesign-resume`

### Q: 想重新开始一个任务（丢弃当前进度）

```
rm -rf ~/Desktop/你的项目/tasks/任务名
```

然后重新 `/harnessdesign-start --prd ...`

### Q: 更新后验证测试没有全部通过

截图发给 GuanchengDing，附上终端中的错误信息。

### Q: 同一个项目能不能跑多个任务？

可以。每次 `/harnessdesign-start` 会创建一个新的任务工作区。`/harnessdesign-resume` 会让你选择要恢复哪个任务。

---

## 需要帮助？

直接联系 GuanchengDing —— Slack、微信、或任何你方便的渠道。
