# ZDS Empty State

## Tailwind 组合

### 容器
- `flex flex-col items-center justify-center py-16 text-center`

### 内部结构
```
Empty State
├── 插画区域: `w-40 h-40 bg-[#F7F8FA] rounded-xl mb-6 flex items-center justify-center`
│   └── 插画/图标（用 emoji 或 SVG 占位）
├── 标题: `text-lg font-semibold text-[#232333] mb-2`
├── 描述: `text-sm text-[#6E6E7E] mb-6 max-w-sm`
└── CTA 按钮（可选）: [ZDS:zds-button] Primary 变体
```

### 变体
- **表格空状态**: 嵌入 `<tr><td colspan="N">` 中，容器改为 `py-12`
- **卡片空状态**: 嵌入卡片内部，容器改为 `py-8`
- **无 CTA**: 纯提示型，不含按钮

## HTML 示例
```html
<div class="flex flex-col items-center justify-center py-16 text-center">
  <div class="w-40 h-40 bg-[#F7F8FA] rounded-xl mb-6 flex items-center justify-center">
    <span class="text-4xl">📭</span>
  </div>
  <h3 class="text-lg font-semibold text-[#232333] mb-2">No items yet</h3>
  <p class="text-sm text-[#6E6E7E] mb-6 max-w-sm">Get started by creating your first item.</p>
  <button class="bg-[#0B5CFF] text-white rounded-lg px-4 py-2 text-sm font-medium hover:bg-[#0047CC] transition-all duration-150">
    Create Item
  </button>
</div>
```
