# ZDS Sidebar

## Tailwind 组合

### 容器
- **展开态**: `w-60 h-screen bg-white border-r border-[#E8E8ED] flex flex-col`
- **折叠态**: `w-16 h-screen bg-white border-r border-[#E8E8ED] flex flex-col`

### 内部结构
```
Sidebar
├── Logo 区域: `px-4 py-4 border-b border-[#E8E8ED]`
├── Nav 列表: `flex-1 overflow-y-auto py-2`
│   └── Nav Item（见下方）
└── Bottom 区域（可选）: `px-4 py-4 border-t border-[#E8E8ED]`
    └── 用户头像/设置入口
```

### Nav Item
- **默认**: `flex items-center gap-3 px-4 py-2 text-sm text-[#6E6E7E] rounded-lg mx-2 hover:bg-[#F0F0F5] transition-colors cursor-pointer`
- **激活**: `flex items-center gap-3 px-4 py-2 text-sm text-[#0B5CFF] font-medium bg-[#EBF0FF] rounded-lg mx-2`
- **分组标题**: `px-4 py-2 text-xs font-medium text-[#ACACB9] uppercase tracking-wider mt-4`

### 折叠态 Nav Item
- 只显示图标：`flex items-center justify-center p-2 rounded-lg mx-2`
- Tooltip 显示完整文字

## HTML 示例
```html
<aside class="w-60 h-screen bg-white border-r border-[#E8E8ED] flex flex-col">
  <div class="px-4 py-4 border-b border-[#E8E8ED]">
    <span class="text-lg font-bold text-[#232333]">Logo</span>
  </div>
  <nav class="flex-1 overflow-y-auto py-2">
    <a class="flex items-center gap-3 px-4 py-2 text-sm text-[#0B5CFF] font-medium bg-[#EBF0FF] rounded-lg mx-2">
      <span>🏠</span> Dashboard
    </a>
    <a class="flex items-center gap-3 px-4 py-2 text-sm text-[#6E6E7E] rounded-lg mx-2 hover:bg-[#F0F0F5] transition-colors cursor-pointer">
      <span>📋</span> Tasks
    </a>
  </nav>
</aside>
```
