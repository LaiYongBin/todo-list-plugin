#!/usr/bin/env python3
"""Todo List Manager — MySQL CRUD + DingTalk notifications"""

import os, sys, json, time, hmac, hashlib, base64
import urllib.parse, urllib.request
from datetime import date

# ── 环境变量 ──────────────────────────────────────────────
DB_HOST   = os.environ['LYB_SKILL_MYSQL_ADDRESS']
DB_PORT   = int(os.environ.get('LYB_SKILL_MYSQL_PORT', '3306'))
DB_USER   = os.environ['LYB_SKILL_MYSQL_USERNAME']
DB_PASS   = os.environ['LYB_SKILL_MYSQL_PASSWORD']
DB_NAME   = os.environ['LYB_SKILL_MYSQL_MY_PERSONAL_DATABASE']
DT_URL    = os.environ['LYB_SKILL_ALIYUN_ROBOT_ADDRESS']
DT_SECRET = os.environ['LYB_SKILL_ALIYUN_ROBOT_SECRET']

USER_ID = 1  # 个人使用，固定 user_id

# ── 数据库 ───────────────────────────────────────────────
def get_conn():
    import mysql.connector
    return mysql.connector.connect(
        host=DB_HOST, port=DB_PORT,
        user=DB_USER, password=DB_PASS,
        database=DB_NAME, charset='utf8mb4'
    )

# ── 钉钉通知 ─────────────────────────────────────────────
def _signed_url():
    ts  = str(round(time.time() * 1000))
    raw = f'{ts}\n{DT_SECRET}'.encode('utf-8')
    sig = base64.b64encode(
        hmac.new(DT_SECRET.encode('utf-8'), raw, hashlib.sha256).digest()
    )
    return f"{DT_URL}&timestamp={ts}&sign={urllib.parse.quote_plus(sig)}"

def send_dingtalk(text: str):
    payload = json.dumps({
        "msgtype": "markdown",
        "markdown": {"title": "📋 待办事项", "text": text}
    }).encode('utf-8')
    req = urllib.request.Request(
        _signed_url(), data=payload,
        headers={'Content-Type': 'application/json'}
    )
    urllib.request.urlopen(req, timeout=10)

# ── 格式化 ───────────────────────────────────────────────
def _fmt(idx, row):
    mark = "✅" if row['status'] == 2 else "☐"
    due  = f"（截止：{row['due_time'].strftime('%m-%d')}）" if row.get('due_time') else ""
    return f"{idx}. {mark} {row['title']}{due}"

def _today_summary(conn):
    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT id, title, status, due_time FROM todo_list
        WHERE user_id=%s AND is_deleted=0 AND DATE(create_time)=CURDATE()
        ORDER BY status ASC, priority DESC, id ASC
    """, (USER_ID,))
    rows = cur.fetchall(); cur.close()
    if not rows:
        return ""
    lines = ["**今日待办：**"] + [_fmt(i, r) for i, r in enumerate(rows, 1)]
    return "\n\n".join(lines)

# ── 命令实现 ─────────────────────────────────────────────
def cmd_list_today():
    conn = get_conn()
    cur  = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT id, title, status, due_time, finished_at FROM todo_list
        WHERE user_id=%s AND is_deleted=0 AND DATE(create_time)=CURDATE()
        ORDER BY status ASC, priority DESC, id ASC
    """, (USER_ID,))
    rows = cur.fetchall(); cur.close(); conn.close()
    print(json.dumps(rows, default=str))

def cmd_list_all():
    conn = get_conn()
    cur  = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT id, title, status, due_time, finished_at FROM todo_list
        WHERE user_id=%s AND is_deleted=0 AND status != 2
        ORDER BY priority DESC, due_time ASC, id ASC
    """, (USER_ID,))
    rows = cur.fetchall(); cur.close(); conn.close()
    print(json.dumps(rows, default=str))

def cmd_add(title, due_date=None):
    conn = get_conn()
    cur  = conn.cursor()
    cur.execute("""
        INSERT INTO todo_list (user_id, title, status, priority, due_time)
        VALUES (%s, %s, 0, 1, %s)
    """, (USER_ID, title, due_date))
    conn.commit()
    todo_id = cur.lastrowid

    md = f"## ✅ 已添加待办\n\n**{title}**"
    if due_date:
        md += f"\n\n截止时间：{due_date}"
    summary = _today_summary(conn)
    if summary:
        md += f"\n\n---\n\n{summary}"

    cur.close(); conn.close()
    send_dingtalk(md)
    print(f"OK:{todo_id}")

def cmd_complete(todo_id, title):
    conn = get_conn()
    cur  = conn.cursor()
    cur.execute("""
        UPDATE todo_list SET status=2, finished_at=NOW()
        WHERE id=%s AND user_id=%s
    """, (todo_id, USER_ID))
    conn.commit()

    md = f"## ✅ 待办已完成\n\n**{title}**"
    summary = _today_summary(conn)
    if summary:
        md += f"\n\n---\n\n{summary}"

    cur.close(); conn.close()
    send_dingtalk(md)
    print("OK")

def cmd_delete(todo_id, title):
    conn = get_conn()
    cur  = conn.cursor()
    cur.execute("""
        UPDATE todo_list SET is_deleted=1
        WHERE id=%s AND user_id=%s
    """, (todo_id, USER_ID))
    conn.commit()

    md = f"## 🗑️ 待办已删除\n\n~~{title}~~"
    summary = _today_summary(conn)
    if summary:
        md += f"\n\n---\n\n{summary}"

    cur.close(); conn.close()
    send_dingtalk(md)
    print("OK")

# ── 入口 ─────────────────────────────────────────────────
if __name__ == '__main__':
    action = sys.argv[1] if len(sys.argv) > 1 else ''
    if   action == 'list-today': cmd_list_today()
    elif action == 'list-all':   cmd_list_all()
    elif action == 'add':        cmd_add(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None)
    elif action == 'complete':   cmd_complete(int(sys.argv[2]), sys.argv[3])
    elif action == 'delete':     cmd_delete(int(sys.argv[2]), sys.argv[3])
    else:
        print(f"Unknown action: {action}", file=sys.stderr); sys.exit(1)
