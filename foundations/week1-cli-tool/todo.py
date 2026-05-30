# todo.py - 命令行待办工具
# Week 1 Day 7 项目

import json
import os
import sys
from datetime import datetime

# 在 Windows 控制台（默认 GBK）下输出 emoji/中文不报错
# Python 3.7+ 才有 reconfigure；try/except 兼容更老版本
try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

# ============================================================
# 数据文件路径（和 todo.py 同目录）
# ============================================================
DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tasks.json")


# ============================================================
# 第一部分：数据层（文件读写）
# ============================================================

def load_tasks():
    """
    从 DATA_FILE 加载任务列表
    - 文件不存在：返回空列表 []
    - JSON 格式错误：打印提示，返回空列表 []
    """
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        print("⚠️ 数据文件损坏，已重置为空列表")
        return []


def save_tasks(tasks):
    """
    把任务列表保存到 DATA_FILE
    - 使用 json.dump，ensure_ascii=False，indent=2
    """
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2)


# ============================================================
# 第二部分：任务操作函数
# ============================================================

def get_next_id(tasks):
    """
    返回下一个可用的任务 ID（当前最大 ID + 1，从 1 开始）
    - tasks 为空时返回 1
    """
    if not tasks:
        return 1
    return max(t["id"] for t in tasks) + 1


def add_task(title, priority="normal"):
    """
    添加新任务
    """
    tasks = load_tasks()
    new_id = get_next_id(tasks)
    task = {
        "id": new_id,
        "title": title,
        "priority": priority,
        "done": False,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    tasks.append(task)
    save_tasks(tasks)
    print(f"✅ 已添加任务 #{new_id}: {title} ({priority})")


def format_task(task):
    """把单个任务格式化成显示字符串"""
    status = "✓" if task["done"] else " "
    priority = task.get("priority", "normal")
    return f"  [{status}] #{task['id']} {task['title']} ({priority})"


def list_tasks(filter_mode="pending"):
    """
    列出任务
    - filter_mode: "all" 全部 | "done" 已完成 | "pending" 待完成（默认）
    """
    tasks = load_tasks()

    if filter_mode == "done":
        filtered = [t for t in tasks if t["done"]]
        header = "已完成任务："
        empty_msg = "（暂无已完成任务）"
    elif filter_mode == "all":
        filtered = tasks
        header = "所有任务："
        empty_msg = "（暂无任务，使用 add 命令添加）"
    else:  # pending
        filtered = [t for t in tasks if not t["done"]]
        header = "待办任务："
        empty_msg = "🎉 暂无待办任务"

    if not filtered:
        print(empty_msg)
        return

    print(header)
    for t in filtered:
        print(format_task(t))


def complete_task(task_id):
    """
    标记任务为已完成
    """
    tasks = load_tasks()
    for t in tasks:
        if t["id"] == task_id:
            if t["done"]:
                print(f"ℹ️ 任务 #{task_id} 已经是完成状态")
                return
            t["done"] = True
            save_tasks(tasks)
            print(f"✅ 任务 #{task_id} 已完成！")
            return
    print(f"❌ 任务不存在: ID={task_id}")


def delete_task(task_id):
    """
    删除任务
    """
    tasks = load_tasks()
    for i, t in enumerate(tasks):
        if t["id"] == task_id:
            tasks.pop(i)
            save_tasks(tasks)
            print(f"🗑️ 任务 #{task_id} 已删除")
            return
    print(f"❌ 任务不存在: ID={task_id}")


def show_stats():
    """
    显示统计信息
    """
    tasks = load_tasks()
    total = len(tasks)
    done = sum(1 for t in tasks if t["done"])
    pending = total - done
    print(f"📊 统计：总计 {total} 个任务，已完成 {done} 个，待完成 {pending} 个")


# ============================================================
# 第三部分：命令行解析（main 函数）
# ============================================================

def print_help():
    """打印帮助信息"""
    print("""
命令行待办工具 - 使用说明
--------------------------
python todo.py add <标题> [--priority high/normal/low]  添加任务
python todo.py list [--all | --done | --pending]        列出任务
python todo.py done <id>                                标记完成
python todo.py delete <id>                              删除任务
python todo.py stats                                    查看统计
python todo.py help                                     显示帮助
""")


def parse_priority(args):
    """从参数列表里解析 --priority 值，未指定则返回 'normal'"""
    if "--priority" in args:
        idx = args.index("--priority")
        if idx + 1 < len(args):
            value = args[idx + 1]
            if value in ("high", "normal", "low"):
                return value
            print(f"⚠️ 无效优先级：{value}，已使用 normal")
    return "normal"


def main():
    """
    解析命令行参数并调用对应函数
    """
    if len(sys.argv) < 2:
        print_help()
        return

    command = sys.argv[1]

    if command == "add":
        # ["todo.py", "add", "标题", "--priority", "high"] 或 ["todo.py", "add", "标题"]
        if len(sys.argv) < 3:
            print("❌ 请提供任务标题，例如：python todo.py add \"学习Python\"")
            return
        title = sys.argv[2]
        priority = parse_priority(sys.argv[3:])
        add_task(title, priority)

    elif command == "list":
        # ["todo.py", "list"] | ["todo.py", "list", "--all"] | "--done" | "--pending"
        filter_mode = "pending"
        if len(sys.argv) >= 3:
            flag = sys.argv[2]
            if flag == "--all":
                filter_mode = "all"
            elif flag == "--done":
                filter_mode = "done"
            elif flag == "--pending":
                filter_mode = "pending"
            else:
                print(f"❌ 未知参数：{flag}，可用：--all | --done | --pending")
                return
        list_tasks(filter_mode)

    elif command == "done":
        if len(sys.argv) < 3:
            print("❌ 请提供任务 ID，例如：python todo.py done 1")
            return
        try:
            task_id = int(sys.argv[2])
        except ValueError:
            print(f"❌ 任务 ID 必须是整数：{sys.argv[2]}")
            return
        complete_task(task_id)

    elif command == "delete":
        if len(sys.argv) < 3:
            print("❌ 请提供任务 ID，例如：python todo.py delete 1")
            return
        try:
            task_id = int(sys.argv[2])
        except ValueError:
            print(f"❌ 任务 ID 必须是整数：{sys.argv[2]}")
            return
        delete_task(task_id)

    elif command == "stats":
        show_stats()

    elif command == "help":
        print_help()

    else:
        print(f"❌ 未知命令: {command}，输入 'help' 查看帮助")


# ============================================================
# 程序入口
# ============================================================
if __name__ == "__main__":
    main()
