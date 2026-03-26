# ZDS Input

## Tailwind 组合

### 基础输入框
- `w-full bg-white border border-[#E8E8ED] rounded-lg px-3 py-2 text-sm text-[#232333] placeholder-[#ACACB9] transition-all duration-150`

### 状态
- **Focus**: `focus:border-[#0B5CFF] focus:ring-1 focus:ring-[#0B5CFF] focus:outline-none`
- **Error**: `border-[#E02D3C] focus:ring-[#E02D3C]`
- **Disabled**: `bg-[#F7F8FA] text-[#ACACB9] cursor-not-allowed`

### 带标签
```
Label + Input 组合
├── Label: `block text-sm font-medium text-[#232333] mb-1`
├── Input: 基础输入框样式
├── Helper text（可选）: `text-xs text-[#6E6E7E] mt-1`
└── Error text（可选）: `text-xs text-[#E02D3C] mt-1`
```

### 变体
- **Textarea**: 同样式，追加 `min-h-[80px] resize-y`
- **Select**: 追加 `appearance-none` + 右侧下拉箭头 SVG 背景
- **Search**: 左侧搜索图标 + `pl-10`

## HTML 示例
```html
<div>
  <label class="block text-sm font-medium text-[#232333] mb-1">Label</label>
  <input type="text" placeholder="Placeholder..."
    class="w-full bg-white border border-[#E8E8ED] rounded-lg px-3 py-2 text-sm text-[#232333] placeholder-[#ACACB9] focus:border-[#0B5CFF] focus:ring-1 focus:ring-[#0B5CFF] focus:outline-none transition-all duration-150" />
  <p class="text-xs text-[#6E6E7E] mt-1">Helper text goes here</p>
</div>
```
