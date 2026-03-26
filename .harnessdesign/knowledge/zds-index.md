# Prism Component Index (L0)

> **用途**：锚定层常驻，Phase 1-4 全程可见。让 Router 和所有 Skill 在任意阶段都能感知 Prism 有哪些组件可用。
> **来源**：Prism Desktop — Web 2.5 Sticker Sheet (Figma fileKey: `OWKBE2BJBBanezKhapWx2Y`)
> **维护**：Prism 新增/废弃组件时由设计师更新。

## Buttons

| ID | 组件名 | 一句话描述 | 适用场景 |
|----|--------|-----------|---------|
| prism-basic-button | Basic Button | 主按钮，支持 Primary/Secondary/Tertiary(Ghost) 变体，min-h 32px | 表单提交、CTA、操作触发 |
| prism-icon-button | Icon Button | 图标圆形按钮 32×32px，支持 Primary(Filled)/Ghost | 工具栏操作、关闭、更多 |
| prism-split-button | Split Button | 带下拉分隔的按钮 | 主操作+次要操作组合 |
| prism-toggle-button | Toggle Button | 开关式按钮（on/off） | 视图模式切换 |
| prism-home-action-button | Home Action Button | 首页快捷操作按钮（图标+文字纵向堆叠） | 首页快捷入口 |
| prism-grabber-button | Grabber Button | 拖拽手柄按钮 18×18px | 可拖拽列表项 |
| prism-info-button | Info Button | 信息提示触发按钮 18×18px | Tooltip 触发 |
| prism-inline-icon-button | Inline Icon Button | 行内关闭/操作按钮 | 标签关闭、行内操作 |

## Form Controls

| ID | 组件名 | 一句话描述 | 适用场景 |
|----|--------|-----------|---------|
| prism-text-input | Text Input | 单行文本输入，含 Label + 输入区，总高 54px | 表单字段 |
| prism-textarea | Text Area Input | 多行文本输入，总高 82px | 长文本输入 |
| prism-select | Select Input | 下拉选择输入，总高 54px | 选项选择 |
| prism-ghost-select | Ghost Select | 轻量无边框下拉 32px | 紧凑筛选 |
| prism-combo-input | Combo Input | 组合输入 32px | 复合输入场景 |
| prism-password-input | Password Input | 密码输入，总高 54px | 登录/注册 |
| prism-number-input | Number Input | 数字输入，总高 54px | 数量、金额 |
| prism-search-input | Search Input | 搜索输入 32px | 搜索功能 |
| prism-date-picker | Date Picker Input | 日期选择输入，总高 54px | 日期选择 |
| prism-checkbox-group | Checkbox Group | 复选框组 | 多选场景 |
| prism-radio-group | Radio Group | 单选按钮组 | 互斥选择 |
| prism-toggle | Toggle (Switch) | 开关控件 16px 高 | 设置项启用/禁用 |

## Data Display

| ID | 组件名 | 一句话描述 | 适用场景 |
|----|--------|-----------|---------|
| prism-accordion | Accordion | 折叠面板，min-h 40px/行 | 分组设置、FAQ |
| prism-avatar | Avatar | 用户头像 32×32px 圆形 | 用户标识 |
| prism-avatar-group | Avatar Group | 头像组（堆叠显示） | 参与者列表 |
| prism-divider | Divider | 分割线 1px | 内容分隔 |
| prism-list-item | List Item | 列表项（含 leading/content/trailing 插槽）32px | 菜单、设置列表 |
| prism-inline-tag | Inline Tag | 行内标签 | 分类标记 |
| prism-text-badge | Text Badge | 文字徽章 ~16px 高 | 状态标记、计数 |
| prism-notifier | Notifier | 通知点/数字 8px/16px | 未读提示 |
| prism-code-snippet | Code Snippet | 代码片段展示 | 代码展示 |
| prism-carousel | Carousel | 图片轮播（单张/多张） | 图片展示 |

## Navigation

| ID | 组件名 | 一句话描述 | 适用场景 |
|----|--------|-----------|---------|
| prism-tab-bar | Tab Bar | 选项卡切换（下划线指示器），min-h 32/40px | 内容分类、视图切换 |
| prism-breadcrumbs | Breadcrumbs | 面包屑导航 h 18px | 层级页面导航 |
| prism-segmented-control | Segmented Control | 分段控件（药丸形），h 32px | 视图模式切换 |
| prism-chip-bar | Chip Bar | 标签条/筛选条 h 32px | 快速筛选 |
| prism-pagination | Pagination | 分页控件 h 32px | 列表/表格分页 |
| prism-anchor | Anchor | 锚点导航 | 页内定位 |
| prism-step-progress | Step Progress Indicator | 步骤进度指示器（水平/垂直） | 流程引导 |
| prism-link | Link | 链接文字 h 18px | 导航跳转 |

## Feedback

| ID | 组件名 | 一句话描述 | 适用场景 |
|----|--------|-----------|---------|
| prism-banner | Banner | 横幅通知（含图标、文字、操作、关闭），h 68px | 全局提示、公告 |
| prism-notification | Notification | 浮动通知卡片 h 74px，圆角 16px，阴影 dropShadow-md | 操作反馈、状态变更 |
| prism-dialog | Dialog | 模态对话框 w 448px，圆角 32px | 确认操作、表单填写 |
| prism-dialog-overlay | Dialog Overlay | 对话框遮罩层 | 配合 Dialog 使用 |
| prism-info-popover | Info Popover | 信息气泡（4 方向），w 310-344px | 信息补充说明 |
| prism-tooltip | Tooltip | 悬浮提示 | 图标说明、简短提示 |
| prism-loading-indicator | Loading Indicator | 加载指示器（含背景遮罩） | 内容加载中 |

## Input Enhancement

| ID | 组件名 | 一句话描述 | 适用场景 |
|----|--------|-----------|---------|
| prism-menu | Menu | 下拉菜单面板 w 98-184px | 操作菜单 |
| prism-menu-item | Menu Item | 菜单项 h 32px | 菜单内选项 |
| prism-dropdown-menu | Dropdown Menu | 下拉菜单组合（触发器+Menu） | 操作菜单触发 |
| prism-date-dropdown | Date Picker Dropdown | 日期选择下拉 280×336px | 日期选择 |
| prism-time-picker | Time Picker | 时间选择器 176×242px | 时间选择 |
| prism-emoji-picker | Emoji Picker | 表情选择器 334×380px | 表情输入 |
| prism-color-picker | Color Picker | 颜色选择器 | 颜色选择 |
| prism-slider | Slider | 滑块（单值）h 24px | 数值调节 |
| prism-slider-range | Slider Range | 范围滑块 h 24px | 范围选择 |

## Content

| ID | 组件名 | 一句话描述 | 适用场景 |
|----|--------|-----------|---------|
| prism-scroll-view | Scroll View | 带滚动条内容容器 | 可滚动区域 |
| prism-file-uploader | File Uploader | 文件上传区（拖拽+列表） | 文件上传 |
| prism-drag-and-drop | Drag and Drop | 拖拽排序列表 | 可排序列表 |
| prism-linear-progress | Linear Progress | 线性进度条 | 进度展示 |

## Deprecated（禁止使用）

- Toggle button group → 使用独立 Toggle button
- Info popover button → 使用 Info button + Popover 组合
- Base: checkbox (legacy) → 使用新 Checkbox 组件
- List item - Parts (legacy) → 使用新 Table cell
