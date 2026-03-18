# /todo-list-all

列出所有未完成的待办事项（跨日期），并支持后续交互操作。

## 执行步骤

### 第一步：获取数据

```bash
python3 ~/.claude/scripts/todo_manager.py list-all
```

### 第二步：格式化展示

将 JSON 解析后展示，**在上下文中保留 序号→{id, title} 映射**：

```
全部未完成待办（共X项）：
1. ☐ 写PPT（截止：03-20）
2. ☐ 回复邮件
3. ☐ 整理文档（截止：03-25）
```

若无数据：回复"当前没有未完成的待办事项 🎉"

### 第三步：等待交互

提示用户：
> 可说"第X个完成"或直接回复数字标记完成，说"删除第X个"逻辑删除

### 第四步：处理交互指令

根据上下文中的 序号→id 映射执行：

**标记完成**（用户说 "1" / "第1个完成" / "完成第1个"）：
```bash
python3 ~/.claude/scripts/todo_manager.py complete {id} "{title}"
```

**逻辑删除**（用户说 "删除第1个" / "删除1"）：
```bash
python3 ~/.claude/scripts/todo_manager.py delete {id} "{title}"
```

操作完成后重新展示更新后的列表，并告知已发送钉钉通知。
