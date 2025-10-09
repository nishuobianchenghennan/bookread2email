# main.py (V2.0 - 智能集成版)

import json
import os
import book_parser
import ai_analyzer
import email_sender
import config


def generate_reading_plan_if_needed():
    """
    检查阅读计划是否存在，如果不存在，则自动生成。
    这是 plan.py 功能的完美集成。
    """
    plan_path = os.path.join(book_parser.BASE_DIR, config.READING_PLAN_FILE)

    # 【核心逻辑】检查文件是否存在
    if os.path.exists(plan_path):
        print(f"阅读计划文件 '{config.READING_PLAN_FILE}' 已存在，跳过生成步骤。")
        return True  # 返回 True 表示计划已就绪

    # --- 如果文件不存在，则执行生成逻辑 ---
    print(f"--- 未找到阅读计划，现在开始自动生成 ---")

    book_toc = book_parser.get_book_toc()
    if not book_toc:
        print("错误：无法获取书籍目录，计划生成失败。")
        return False  # 返回 False 表示计划生成失败

    plan = []
    for i, unit in enumerate(book_toc):
        plan.append({
            "day": i + 1,
            "title": unit.get("title", "未知标题"),
            "status": "pending"
        })

    try:
        with open(plan_path, 'w', encoding='utf-8') as f:
            json.dump(plan, f, ensure_ascii=False, indent=4)
        print(f"成功生成阅读计划！共 {len(plan)} 天。")
        print(f"计划已保存至: {plan_path}")
        return True  # 返回 True 表示计划已成功生成
    except Exception as e:
        print(f"错误：无法写入计划文件，{e}")
        return False


def main_workflow():
    """主工作流程 - 每日执行版"""
    print(f"--- 每日文章深度分析工作流启动 ---")
    print(f"目标书籍: {config.BOOK_FILENAME}")

    # 1. 检查并按需生成阅读计划
    plan_ready = generate_reading_plan_if_needed()
    if not plan_ready:
        print("工作流因无法准备阅读计划而终止。")
        return

    # 2. 加载阅读计划 (此时我们确信它一定存在)
    plan_path = os.path.join(book_parser.BASE_DIR, config.READING_PLAN_FILE)
    with open(plan_path, 'r', encoding='utf-8') as f:
        reading_plan = json.load(f)

    # 3. 读取当前进度
    progress_path = os.path.join(book_parser.BASE_DIR, config.PROGRESS_FILE)
    try:
        with open(progress_path, 'r', encoding='utf-8') as f:
            # 健壮性增强：确保文件不为空
            progress_content = f.read()
            if not progress_content:
                current_index = 0
            else:
                current_index = json.loads(progress_content).get('current_unit_index', 0)
    except (FileNotFoundError, json.JSONDecodeError):
        current_index = 0

    # 4. 检查是否已完成所有计划
    if current_index >= len(reading_plan):
        print("恭喜！您已经完成了所有的阅读计划！")
        email_sender.send_email(
            f"阅读报告：已完成《{config.BOOK_FILENAME}》",
            "祝贺！您已完成了本书的所有阅读计划。"
        )
        return

    # 5. 获取当天的阅读任务
    today_task = reading_plan[current_index]
    print(f"\n今天的阅读任务 (第 {today_task['day']} 天): 《{today_task['title']}》")

    # 6. 读取对应内容
    full_toc = book_parser.get_book_toc()
    content, title, is_finished = book_parser.read_unit_content(full_toc, current_index)

    if is_finished or not content:
        print(f"无法读取 '{title}' 的内容，或书籍已读完。工作流终止。")
        return

    # 7. AI分析
    analysis_report = ai_analyzer.get_analysis_from_ai(content, title)

    # 8. 发送邮件
    email_subject = f"深度分析报告 (第 {today_task['day']} 天) - 《{title}》"
    email_sender.send_email(email_subject, analysis_report)

    # 9. 更新进度
    with open(progress_path, 'w', encoding='utf-8') as f:
        json.dump({'current_unit_index': current_index + 1}, f, indent=4)
    print("进度已更新至下一天。")


if __name__ == "__main__":
    main_workflow()
    print("\n--- 工作流执行完毕 ---")
