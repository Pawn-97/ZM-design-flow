# ZDS Button

## Tailwind 组合

### 变体
- **Primary**: `bg-[#0B5CFF] text-white rounded-lg px-4 py-2 text-sm font-medium hover:bg-[#0047CC] transition-all duration-150`
- **Secondary**: `bg-white text-[#232333] border border-[#E8E8ED] rounded-lg px-4 py-2 text-sm font-medium hover:bg-[#F0F0F5] transition-all duration-150`
- **Ghost**: `bg-transparent text-[#0B5CFF] rounded-lg px-4 py-2 text-sm font-medium hover:bg-[#EBF0FF] transition-all duration-150`
- **Danger**: `bg-[#E02D3C] text-white rounded-lg px-4 py-2 text-sm font-medium hover:bg-[#C4232F] transition-all duration-150`

### 尺寸
- **sm**: `px-3 py-1.5 text-xs rounded-lg`
- **md**: `px-4 py-2 text-sm rounded-lg`（默认）
- **lg**: `px-6 py-3 text-base rounded-lg`

### 状态
- **Disabled**: 追加 `opacity-50 cursor-not-allowed`
- **Loading**: 内容替换为 `<svg class="animate-spin h-4 w-4" ...>` spinner
- **Focus**: 追加 `focus:ring-2 focus:ring-[#0B5CFF] focus:ring-offset-2`

### 图标按钮
- 左图标：`<span class="mr-2">icon</span>` + 按钮文字
- 纯图标：`p-2 rounded-lg`（方形）

## HTML 示例
```html
<button class="bg-[#0B5CFF] text-white rounded-lg px-4 py-2 text-sm font-medium hover:bg-[#0047CC] transition-all duration-150">
  Primary Action
</button>
```
