# ZDS Modal

## Tailwind 组合

### 遮罩层
- `fixed inset-0 bg-black/50 z-50 flex items-center justify-center`

### 弹窗面板
- `bg-white rounded-2xl shadow-lg w-full max-w-lg mx-4 overflow-hidden`

### 内部结构
```
Modal
├── Header: `flex items-center justify-between px-6 py-4 border-b border-[#E8E8ED]`
│   ├── Title: `text-lg font-semibold text-[#232333]`
│   └── Close button: `text-[#6E6E7E] hover:text-[#232333] p-1 rounded-lg hover:bg-[#F0F0F5]`
├── Body: `px-6 py-4`
└── Footer: `flex items-center justify-end gap-3 px-6 py-4 border-t border-[#E8E8ED]`
    ├── Cancel: [ZDS:zds-button] Secondary
    └── Confirm: [ZDS:zds-button] Primary
```

### 变体
- **小型弹窗**: `max-w-sm`
- **大型弹窗**: `max-w-2xl`
- **危险确认**: Footer Confirm 用 [ZDS:zds-button] Danger 变体
- **无 Footer**: 纯内容展示型弹窗

## HTML 示例
```html
<div class="fixed inset-0 bg-black/50 z-50 flex items-center justify-center">
  <div class="bg-white rounded-2xl shadow-lg w-full max-w-lg mx-4 overflow-hidden">
    <div class="flex items-center justify-between px-6 py-4 border-b border-[#E8E8ED]">
      <h2 class="text-lg font-semibold text-[#232333]">Modal Title</h2>
      <button class="text-[#6E6E7E] hover:text-[#232333] p-1 rounded-lg hover:bg-[#F0F0F5]">✕</button>
    </div>
    <div class="px-6 py-4">Body content</div>
    <div class="flex items-center justify-end gap-3 px-6 py-4 border-t border-[#E8E8ED]">
      <button class="bg-white text-[#232333] border border-[#E8E8ED] rounded-lg px-4 py-2 text-sm font-medium">Cancel</button>
      <button class="bg-[#0B5CFF] text-white rounded-lg px-4 py-2 text-sm font-medium">Confirm</button>
    </div>
  </div>
</div>
```
