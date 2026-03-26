# Deviation Alert Templates

> These templates define the "Fail Loud" mechanism. When `validate_transition.py`
> detects a state mismatch or missing pre-condition, the alert is injected into
> the conversation via Hook or Skill SOP instruction.
>
> Design principle: **Designer sees the problem in 3 seconds, without reading JSON.**

---

## Alert Type 1: State Skip Detected

Triggered when AI attempts to transition to a state that doesn't match `expected_next_state`.

```markdown
⚠️ 工作流偏差检测
──────────────────
预期下一步：{expected_next_state}（{expected_description}）
实际状态：AI 尝试进入 {actual_target}

缺失前置条件：
{for each error:}
- ❌ {error_message}
{end for}

已自动阻止状态转换。请确认上一阶段是否已完成。
```

## Alert Type 2: Missing Approval

Triggered when AI attempts to proceed past a `[STOP AND WAIT FOR APPROVAL]` point
without designer confirmation recorded in `task-progress.json`.

```markdown
⚠️ 审批缺失
──────────────────
当前阶段：{current_state}（{description}）
此阶段需要设计师确认后才能继续。

状态：approved_by = null（未记录设计师确认）

请确认当前阶段的产出物，然后告诉我可以继续。
```

## Alert Type 3: Artifact Missing

Triggered when the required output files for the current state don't exist or are empty.

```markdown
⚠️ 产出物缺失
──────────────────
当前阶段 "{current_state}" 要求以下产出物：
{for each missing artifact:}
- ❌ {artifact_name}（未找到或为空）
{end for}

这些文件必须存在才能进入下一阶段。
```

## Alert Type 4: Archive Quality Warning

Triggered by `verify_archive.py` when an archive file doesn't meet integrity requirements.
This is a warning (non-blocking) — the archive is already written.

```markdown
⚠️ 归档质量警告
──────────────────
文件：{archive_file}
类型：{archive_type}

发现以下问题：
{for each error:}
- ⚠️ {error_message}
{end for}

建议在继续之前修复上述问题，以确保后续阶段可以正确回引归档内容。
```

## Alert Type 5: Phase Skip Attempt (Write Gate)

Triggered by `hook_pre_write.py` when AI attempts to write an artifact that belongs
to a future phase.

```markdown
⚠️ 写入拦截
──────────────────
AI 尝试写入 "{file_name}"，该文件属于 "{target_state}" 阶段。
当前状态：{current_state}

这看起来像是一次阶段跳跃。请按照工作流顺序完成当前阶段后再生成此文件。
```

---

## Usage in Skill SOP

Skill SOP should include this general instruction near the top:

```markdown
## 工作流护栏

在执行任何状态转换之前，你必须：
1. 运行 `python3 scripts/validate_transition.py <task_dir> <target_state>`
2. 如果验证失败，使用 deviation-alerts.md 中对应的模板输出警告
3. 不要在验证失败后继续执行——等待设计师确认或修复问题
4. 如果验证通过，使用 phase-summary-cards.md 中的模板输出完成小结
```
