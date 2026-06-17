import os
import requests
from datetime import datetime, timezone, timedelta

NOTION_API_KEY = os.environ["NOTION_API_KEY"]
DATABASE_ID = "2b483529-e400-809b-b46b-f941aa812036"

JST = timezone(timedelta(hours=9))

HEADERS = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28",
}


def get_today_jst():
    return datetime.now(JST).strftime("%Y-%m-%d")


def query_overdue_tasks(today):
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    payload = {
        "filter": {
            "and": [
                {
                    "or": [
                        {"property": "ステータス", "status": {"equals": "未着手"}},
                        {"property": "ステータス", "status": {"equals": "進行中"}},
                    ]
                },
                {
                    "property": "実行日",
                    "date": {"before": today},
                },
            ]
        }
    }

    tasks = []
    has_more = True
    start_cursor = None

    while has_more:
        if start_cursor:
            payload["start_cursor"] = start_cursor

        res = requests.post(url, headers=HEADERS, json=payload)
        res.raise_for_status()
        data = res.json()

        tasks.extend(data["results"])
        has_more = data.get("has_more", False)
        start_cursor = data.get("next_cursor")

    return tasks


def reschedule_task(page_id, current_count, today):
    url = f"https://api.notion.com/v1/pages/{page_id}"
    new_count = (current_count or 0) + 1

    payload = {
        "properties": {
            "実行日": {"date": {"start": today}},
            "リスケ": {"number": new_count},
        }
    }

    res = requests.patch(url, headers=HEADERS, json=payload)
    res.raise_for_status()
    return new_count


def main():
    today = get_today_jst()
    print(f"本日の日付（JST）: {today}")
    print("期限切れタスクを検索中...")

    tasks = query_overdue_tasks(today)

    if not tasks:
        print("期限切れタスクはありません。")
        return

    print(f"{len(tasks)}件の期限切れタスクを発見しました。")

    for task in tasks:
        page_id = task["id"]

        title_list = task["properties"].get("タイトル", {}).get("title", [])
        title = title_list[0]["plain_text"] if title_list else "無題"

        current_count = task["properties"].get("リスケ", {}).get("number") or 0

        new_count = reschedule_task(page_id, current_count, today)
        print(f"リスケ完了: 「{title}」 → {today}（リスケ回数: {new_count}回）")

    print(f"完了: {len(tasks)}件のタスクをリスケしました。")


if __name__ == "__main__":
    main()
