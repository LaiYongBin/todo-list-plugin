# todo-list

Todo List 管理技能，支持自然语言操作待办事项，操作后自动发送钉钉通知。

## 功能

| 命令 / 触发 | 说明 |
|------------|------|
| `/todo-list-today` | 列出今日待办（含已完成），可交互标记完成/删除 |
| `/todo-list-add <内容>` | 添加待办，支持"后天完成"等自然语言截止时间 |
| `/todo-list-all` | 列出所有未完成待办，可交互操作 |
| 自然语言 | "添加xxx待办"/"今天有什么待办" 等均可自动触发 |

## 安装

```bash
# 第一步：添加 marketplace（已添加过可跳过）
/plugin marketplace add LaiYongBin/skills-chinese-marketplace

# 第二步：安装插件
/plugin install todo-list@skills-chinese-marketplace
```

## 安装后：部署 Python 脚本

插件系统仅自动安装 skills/ 和 commands/ 目录，脚本需手动复制：

```bash
mkdir -p ~/.claude/scripts
cp ~/Desktop/todo-list-plugin/scripts/todo_manager.py ~/.claude/scripts/
```

## 所需环境变量

```bash
# MySQL（参见 skill-env-vars）
export LYB_SKILL_MYSQL_ADDRESS=
export LYB_SKILL_MYSQL_PORT=3306
export LYB_SKILL_MYSQL_USERNAME=
export LYB_SKILL_MYSQL_PASSWORD=
export LYB_SKILL_MYSQL_MY_PERSONAL_DATABASE=

# 钉钉机器人（参见 skill-env-vars）
export LYB_SKILL_ALIYUN_ROBOT_ADDRESS=   # Webhook 完整 URL（含 access_token）
export LYB_SKILL_ALIYUN_ROBOT_SECRET=    # 签名密钥
```

## 依赖

```bash
pip install mysql-connector-python
```
