# ZDS Card

## Tailwind 组合
- **基础卡片**: `bg-white rounded-xl shadow-sm border border-[#E8E8ED] p-6`
- **紧凑卡片**: `bg-white rounded-xl shadow-sm border border-[#E8E8ED] p-4`
- **可点击卡片**: 追加 `cursor-pointer hover:shadow-md hover:border-[#0B5CFF] transition-all duration-150`
- **选中卡片**: 追加 `border-[#0B5CFF] ring-1 ring-[#0B5CFF]`

## 内部结构
```
Card
├── Header（可选）: `flex items-center justify-between pb-4 border-b border-[#E8E8ED] mb-4`
│   ├── Title: `text-lg font-semibold text-[#232333]`
│   └── Action: 右侧操作按钮/链接
├── Body: 卡片主内容区域
└── Footer（可选）: `flex items-center justify-end pt-4 border-t border-[#E8E8ED] mt-4 gap-3`
```

## HTML 示例
```html
<div class="bg-white rounded-xl shadow-sm border border-[#E8E8ED] p-6">
  <div class="flex items-center justify-between pb-4 border-b border-[#E8E8ED] mb-4">
    <h3 class="text-lg font-semibold text-[#232333]">Card Title</h3>
  </div>
  <div><!-- Body content --></div>
</div>
```
