# ZDS Table

## Tailwind 组合

### 容器
- 表格容器: `w-full overflow-x-auto`
- 表格: `w-full text-sm`

### 表头
- `<thead>`: `bg-[#F7F8FA]`
- `<th>`: `text-left text-xs font-medium text-[#6E6E7E] uppercase tracking-wider px-4 py-3`

### 表行
- `<tr>`: `border-b border-[#E8E8ED] hover:bg-[#F7F8FA] transition-colors`
- `<td>`: `px-4 py-3 text-sm text-[#3E3E4F]`

### 变体
- **斑马纹**: `<tr>` 奇数行追加 `bg-[#FAFBFC]`
- **可选中行**: 追加 `cursor-pointer`，选中时 `bg-[#EBF0FF]`
- **紧凑**: `<th>` 和 `<td>` 改为 `px-3 py-2`

### 排序图标
- 可排序列标题追加 `cursor-pointer hover:text-[#232333]`
- 升序/降序用 `▲` / `▼` 字符或 SVG 图标

### 空状态
- 表格无数据时显示 `[ZDS:zds-empty-state]`，放在 `<tbody>` 内 `<tr><td colspan="全部列数">` 中

## HTML 示例
```html
<div class="w-full overflow-x-auto">
  <table class="w-full text-sm">
    <thead class="bg-[#F7F8FA]">
      <tr>
        <th class="text-left text-xs font-medium text-[#6E6E7E] uppercase tracking-wider px-4 py-3">Name</th>
        <th class="text-left text-xs font-medium text-[#6E6E7E] uppercase tracking-wider px-4 py-3">Status</th>
      </tr>
    </thead>
    <tbody>
      <tr class="border-b border-[#E8E8ED] hover:bg-[#F7F8FA] transition-colors">
        <td class="px-4 py-3 text-sm text-[#3E3E4F]">Item name</td>
        <td class="px-4 py-3 text-sm text-[#3E3E4F]">Active</td>
      </tr>
    </tbody>
  </table>
</div>
```
