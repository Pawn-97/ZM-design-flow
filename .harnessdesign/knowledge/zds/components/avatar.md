# ZDS Avatar

## Tailwind 组合

### 尺寸
- **xs**: `w-6 h-6 rounded-full`
- **sm**: `w-8 h-8 rounded-full`
- **md**: `w-10 h-10 rounded-full`（默认）
- **lg**: `w-12 h-12 rounded-full`
- **xl**: `w-16 h-16 rounded-full`

### 变体
- **图片**: `<img class="w-10 h-10 rounded-full object-cover" />`
- **首字母**: `w-10 h-10 rounded-full bg-[#EBF0FF] text-[#0B5CFF] flex items-center justify-center text-sm font-medium`
- **带边框**: 追加 `ring-2 ring-white`（用于头像堆叠）

### Avatar 组
- 容器: `flex -space-x-2`
- 每个 avatar 追加 `ring-2 ring-white`
- 溢出计数: `w-10 h-10 rounded-full bg-[#F0F0F5] text-[#6E6E7E] flex items-center justify-center text-xs font-medium ring-2 ring-white`

### 带状态指示器
- 在线：右下角 `<span class="absolute bottom-0 right-0 w-2.5 h-2.5 bg-[#12805C] rounded-full ring-2 ring-white"></span>`
- 容器需 `relative`

## HTML 示例
```html
<!-- 图片头像 -->
<img class="w-10 h-10 rounded-full object-cover" src="avatar.jpg" alt="User" />

<!-- 首字母头像 -->
<div class="w-10 h-10 rounded-full bg-[#EBF0FF] text-[#0B5CFF] flex items-center justify-center text-sm font-medium">
  GD
</div>

<!-- 头像组 -->
<div class="flex -space-x-2">
  <img class="w-8 h-8 rounded-full object-cover ring-2 ring-white" src="1.jpg" />
  <img class="w-8 h-8 rounded-full object-cover ring-2 ring-white" src="2.jpg" />
  <div class="w-8 h-8 rounded-full bg-[#F0F0F5] text-[#6E6E7E] flex items-center justify-center text-xs font-medium ring-2 ring-white">+3</div>
</div>
```
