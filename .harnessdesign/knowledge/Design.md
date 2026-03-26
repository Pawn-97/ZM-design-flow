# ZDS Design Rules — Prototype Guide (L1)

> **用途**：Phase 4 (Alchemist) 工作层注入。定义全局视觉规则，约束 AI 的色彩/间距/字体选择。
> **维护**：ZDS 色彩/间距/字体体系变更时由设计师更新。低频变动。
> **注意**：具体组件的 Tailwind class 组合在 `zds/components/*.md` 中，通过 `[ZDS:xxx]` 标签按需加载。

---

## 1. 色彩体系

### 品牌色
| 语义 | ZDS Token | 色值 | Tailwind |
|------|----------|------|---------|
| 主操作 | --zds-blue-6 | #0B5CFF | `bg-[#0B5CFF]` `text-[#0B5CFF]` |
| 主操作悬停 | --zds-blue-7 | #0047CC | `hover:bg-[#0047CC]` |
| 主操作浅底 | --zds-blue-1 | #EBF0FF | `bg-[#EBF0FF]` |
| 危险 | --zds-red-6 | #E02D3C | `bg-[#E02D3C]` |
| 成功 | --zds-green-6 | #12805C | `text-[#12805C]` |
| 警告 | --zds-yellow-6 | #F5A623 | `text-[#F5A623]` |

### 中性色
| 语义 | 色值 | Tailwind |
|------|------|---------|
| 页面背景 | #F7F8FA | `bg-[#F7F8FA]` |
| 卡片/面板背景 | #FFFFFF | `bg-white` |
| 一级文字（标题） | #232333 | `text-[#232333]` |
| 二级文字（正文） | #3E3E4F | `text-[#3E3E4F]` |
| 三级文字（辅助） | #6E6E7E | `text-[#6E6E7E]` |
| 四级文字（占位符） | #ACACB9 | `text-[#ACACB9]` |
| 分割线/边框 | #E8E8ED | `border-[#E8E8ED]` |
| 悬停背景 | #F0F0F5 | `hover:bg-[#F0F0F5]` |

### 规则
- **禁止使用 Tailwind 预设色板**（如 `blue-500`, `gray-200`），必须使用上方精确色值
- **禁止自创色值**，所有颜色必须出自上述列表
- **HTML `<style>` 中必须声明 CSS 变量**（预留 token 替换接口）：
  ```css
  :root {
    --zds-blue: #0B5CFF;
    --zds-blue-hover: #0047CC;
    --zds-blue-light: #EBF0FF;
    --zds-red: #E02D3C;
    --zds-green: #12805C;
    --zds-text-1: #232333;
    --zds-text-2: #3E3E4F;
    --zds-text-3: #6E6E7E;
    --zds-text-4: #ACACB9;
    --zds-bg: #F7F8FA;
    --zds-border: #E8E8ED;
  }
  ```

---

## 2. 间距系统

ZDS 使用 4px 基准网格。只允许以下档位：

| 档位 | px | Tailwind | 典型用途 |
|------|-----|---------|---------|
| 2xs | 2px | `p-0.5` / `gap-0.5` | 图标与文字间距 |
| xs | 4px | `p-1` / `gap-1` | 表单标签与输入框间距 |
| sm | 8px | `p-2` / `gap-2` | 紧凑元素间距 |
| md | 12px | `p-3` / `gap-3` | 按钮内边距、列表项间距 |
| lg | 16px | `p-4` / `gap-4` | 卡片间距、区块分隔 |
| xl | 24px | `p-6` / `gap-6` | 卡片内边距、主内容区边距 |
| 2xl | 32px | `p-8` / `gap-8` | 页面级间距 |
| 3xl | 48px | `p-12` | 大区域留白 |

**禁止**：不得使用 `p-5`, `p-7`, `p-9`, `p-10`, `p-11` 等非标值。

---

## 3. 字体阶梯

| 用途 | 字号 | 行高 | 字重 | Tailwind |
|------|------|------|------|---------|
| 页面大标题 | 28px | 36px | Bold | `text-[28px] leading-9 font-bold` |
| 页面标题 | 24px | 32px | Semibold | `text-2xl leading-8 font-semibold` |
| 区块标题 | 18px | 24px | Semibold | `text-lg leading-6 font-semibold` |
| 子标题 | 16px | 24px | Medium | `text-base leading-6 font-medium` |
| 正文 | 14px | 20px | Regular | `text-sm leading-5` |
| 辅助文字 | 12px | 16px | Regular | `text-xs leading-4` |
| 按钮文字 | 14px | 20px | Medium | `text-sm leading-5 font-medium` |
| 表头 | 12px | 16px | Medium | `text-xs leading-4 font-medium` |

**字体族**：`font-family: 'Lato', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif`

---

## 4. 圆角与阴影

### 圆角
| 元素类型 | 圆角 | Tailwind |
|---------|------|---------|
| 按钮 | 8px | `rounded-lg` |
| 输入框 | 8px | `rounded-lg` |
| 卡片 | 12px | `rounded-xl` |
| 弹窗/Sheet | 16px | `rounded-2xl` |
| 头像 | 50% | `rounded-full` |
| Badge/Tag | 999px | `rounded-full` |
| 小型标签 | 4px | `rounded` |

### 阴影
| 层级 | 用途 | Tailwind |
|------|------|---------|
| Level 1 | 卡片、面板 | `shadow-sm` |
| Level 2 | 下拉菜单、悬浮面板 | `shadow-md` |
| Level 3 | 模态弹窗 | `shadow-lg` |

---

## 5. 布局原则

- **页面最大宽度**：1280px 居中（`max-w-screen-xl mx-auto`）
- **侧边栏宽度**：展开 240px / 折叠 64px
- **顶部导航高度**：56px（`h-14`）
- **内容区内边距**：24px（`p-6`）
- **卡片间距**：16px（`gap-4`）
- **区块间距**：24px（`space-y-6`）
- **表单标签与输入间距**：4px（`gap-1`）
- **响应式断点**：sm:640px / md:768px / lg:1024px / xl:1280px

---

## 6. 交互规范

- **过渡时长**：所有交互态变化 150ms（`transition-all duration-150`）
- **Hover 态**：背景色加深或添加浅色底（参考色彩体系 hover 色值）
- **Focus 态**：蓝色 ring（`focus:ring-2 focus:ring-[#0B5CFF] focus:ring-offset-2`）
- **Disabled 态**：`opacity-50 cursor-not-allowed`
- **Loading 态**：内容替换为 spinner 动画（`animate-spin`）

---

## 7. AI 生成约束（Alchemist 必读）

1. **严格使用 §1 色值**，禁止 Tailwind 预设色板和自创色值
2. **间距只用 §2 档位**，不得使用非标值
3. **组件必须通过 `[ZDS:xxx]` 标签引用 L2 规格**，不得凭空捏造组件样式
4. **空状态必须处理**：每个列表/表格都要有无数据时的 `[ZDS:zds-empty-state]`
5. **交互状态必须完整**：hover、focus、disabled、loading
6. **CSS 变量声明**：HTML `<style>` 中必须按 §1 规则声明 `:root` CSS 变量
7. **字体引入**：`<link href="https://fonts.googleapis.com/css2?family=Lato:wght@400;500;600;700&display=swap" rel="stylesheet">`

<!--
TODO: 设计师根据 ZDS 真实规范替换上述所有色值、间距、字体等占位数据。
本文件是骨架模板，色值均为示例，需要替换为 ZDS 实际值。
-->
