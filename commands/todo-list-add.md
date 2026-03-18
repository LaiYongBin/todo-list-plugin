# /todo-list-add

添加一条新待办事项，支持自然语言截止时间，完成后发送钉钉通知。

## 用法

```
/todo-list-add 写PPT
/todo-list-add 写PPT 后天
/todo-list-add 写季度报告 下周五
```

也可直接在对话中说"添加xxx待办，后天完成"触发。

## 执行步骤

### 第一步：解析参数

从命令参数或对话内容中提取：

- **title**：待办事项的具体内容（必填）
- **due_date**：截止日期（可选），自然语言转 `YYYY-MM-DD`

  | 用户说 | 转换规则 |
  |--------|---------|
  | 今天 | 当天日期 |
  | 明天 | today + 1 |
  | 后天 | today + 2 |
  | 大后天 | today + 3 |
  | 下周一～日 | 下周对应星期 |
  | 具体日期（3月20日） | 直接转换 |

### 第二步：执行脚本

```bash
# 无截止时间
python3 ~/.claude/scripts/todo_manager.py add "title"

# 有截止时间
python3 ~/.claude/scripts/todo_manager.py add "title" "YYYY-MM-DD"
```

### 第三步：回复用户

脚本输出 `OK:{id}` 表示成功，回复：

> 已添加待办：**{title}**（截止：{due_date}）✅
> 已发送钉钉通知。

若脚本报错，展示错误信息并提示检查环境变量配置。
