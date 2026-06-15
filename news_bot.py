import os
import requests
from datetime import datetime, timezone, timedelta

NEWSAPI_KEY = os.environ["NEWSAPI_KEY"]
DISCORD_WEBHOOK = os.environ["DISCORD_WEBHOOK"]

TOPICS = [
    ("M&A", 'M&A OR 買収 OR 合併'),
    ("AI", 'AI OR 人工知能 OR 生成AI'),
    ("国内政治", '政治 OR 国会 OR 内閣'),
    ("経済", '経済 OR GDP OR 景気'),
    ("金融", '金融 OR 日銀 OR 金利 OR 株価'),
]

def get_top_article(query):
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": query,
        "language": "ja",
        "sortBy": "publishedAt",
        "pageSize": 1,
        "apiKey": NEWSAPI_KEY,
    }
    res = requests.get(url, params=params)
    articles = res.json().get("articles", [])
    return articles[0] if articles else None

def send_to_discord(items):
    jst = timezone(timedelta(hours=9))
    today = datetime.now(jst).strftime("%Y年%m月%d日")

    content = f"**📰 おはようございます！{today}のニュース**\n"
    content += "━━━━━━━━━━━━━━━━━━━━\n\n"

    for label, article in items:
        if article:
            title = article.get("title", "タイトルなし")
            description = article.get("description") or "説明なし"
            url = article.get("url", "")
            content += f"**【{label}】**\n"
            content += f"📌 {title}\n"
            content += f"{description[:100]}{'...' if len(description) > 100 else ''}\n"
            content += f"🔗 {url}\n\n"
        else:
            content += f"**【{label}】**\n"
            content += "⚠️ 記事が取得できませんでした\n\n"

    content += "━━━━━━━━━━━━━━━━━━━━"

    requests.post(DISCORD_WEBHOOK, json={"content": content})
    print("Discord送信完了")

if __name__ == "__main__":
    items = []
    for label, query in TOPICS:
        article = get_top_article(query)
        items.append((label, article))
    send_to_discord(items)
