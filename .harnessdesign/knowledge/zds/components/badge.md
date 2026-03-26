# ZDS Badge / Tag

## Tailwind 组合

### 变体
- **Default**: `inline-flex items-center bg-[#F0F0F5] text-[#6E6E7E] text-xs font-medium px-2.5 py-0.5 rounded-full`
- **Primary**: `inline-flex items-center bg-[#EBF0FF] text-[#0B5CFF] text-xs font-medium px-2.5 py-0.5 rounded-full`
- **Success**: `inline-flex items-center bg-[#E8F5E9] text-[#12805C] text-xs font-medium px-2.5 py-0.5 rounded-full`
- **Warning**: `inline-flex items-center bg-[#FFF8E1] text-[#F5A623] text-xs font-medium px-2.5 py-0.5 rounded-full`
- **Danger**: `inline-flex items-center bg-[#FDECEA] text-[#E02D3C] text-xs font-medium px-2.5 py-0.5 rounded-full`

### 带图标
- 左侧小圆点：`<span class="w-1.5 h-1.5 rounded-full bg-current mr-1.5"></span>`

### 可删除
- 右侧叉号：追加 `pr-1.5` + `<button class="ml-1 hover:text-current/80">✕</button>`

## HTML 示例
```html
<span class="inline-flex items-center bg-[#EBF0FF] text-[#0B5CFF] text-xs font-medium px-2.5 py-0.5 rounded-full">
  <span class="w-1.5 h-1.5 rounded-full bg-current mr-1.5"></span>
  Active
</span>
```
