# Todo List 技能

## 触发时机（自动触发）

当用户说以下内容时，自动使用本技能处理：

- "添加xxx待办" / "帮我记一个xxx任务"
- "添加xxx，后天完成" / "明天要xxx" 等含截止时间的自然语言
- "今天有什么待办" / "我的待办"
- 展示列表后，用户说 "第X个完成" / 直接回复数字 / "删除第X个"

---

## 脚本部署检查

**每次执行前，先确认脚本存在：**

```bash
ls ~/.claude/scripts/todo_manager.py
```

若不存在，告知用户："脚本未找到，请重新安装 todo-list 插件，或从插件目录手动复制 scripts/todo_manager.py 到 ~/.claude/scripts/"

---

## 自然语言处理规则

### 1. 添加待办

解析：**标题** + 可选**截止日期**（自然语言 → YYYY-MM-DD）

| 用户说 | 截止日期计算 |
|--------|------------|
| 今天完成 | 当天 |
| 明天完成 | today + 1天 |
| 后天完成 | today + 2天 |
| 下周X | 计算具体日期 |
| 不含日期 | 不传 due_date 参数 |

```bash
# 无截止时间
python3 ~/.claude/scripts/todo_manager.py add "标题"

# 有截止时间
python3 ~/.claude/scripts/todo_manager.py add "标题" "YYYY-MM-DD"
```

### 2. 查看今日待办

```bash
python3 ~/.claude/scripts/todo_manager.py list-today
```

将 JSON 结果格式化展示，**保留 id→序号 映射**供后续交互：

```
今日待办（共X项）：
1. ☐ 写PPT（截止：03-20）
2. ✅ 开会
3. ☐ 回复邮件
```

展示后提示：> 可说"第X个完成"/"X"标记完成，或"删除第X个"删除

### 3. 查看全部未完成

```bash
python3 ~/.claude/scripts/todo_manager.py list-all
```

格式同上，展示后同样支持交互。

### 4. 标记完成

用户说"1" / "第1个完成" / "完成第1个" → 查找序号1对应的 id 和 title：

```bash
python3 ~/.claude/scripts/todo_manager.py complete {id} "{title}"
```

### 5. 删除待办（逻辑删除）

用户说"删除第1个" / "删除1" → 查找序号1对应的 id 和 title：

```bash
python3 ~/.claude/scripts/todo_manager.py delete {id} "{title}"
```

---

## 环境变量依赖

参见 `skill-env-vars`（仅在创建/编辑技能时加载）：

| 变量名 | 用途 |
|--------|------|
| `LYB_SKILL_PG_ADDRESS` | PostgreSQL 地址 |
| `LYB_SKILL_PG_PORT` | PostgreSQL 端口 |
| `LYB_SKILL_PG_USERNAME` | PostgreSQL 用户名 |
| `LYB_SKILL_PG_PASSWORD` | PostgreSQL 密码 |
| `LYB_SKILL_PG_MY_PERSONAL_DATABASE` | 个人数据库名 |
| `LYB_SKILL_ALIYUN_ROBOT_ADDRESS` | 钉钉机器人 Webhook 地址 |
| `LYB_SKILL_ALIYUN_ROBOT_SECRET` | 钉钉机器人签名密钥 |

---

## 钉钉通知格式

所有操作后自动发送钉钉通知，操作结果 + 今日待办汇总（若有）：

- ✅ 已完成：绿色勾
- ☐ 未完成：方形框
- ~~删除的待办~~：删除线
