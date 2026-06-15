import os
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta

DISCORD_WEBHOOK = os.environ["DISCORD_WEBHOOK"]

TOPICS = [
    ("M&A・経済",   "https://news.google.com/rss/search?q=M%26A+買収+合併&hl=ja&gl=JP&ceid=JP:ja"),
    ("AI",         "https://news.google.com/rss/search?q=AI+人工知能+生成AI&hl=ja&gl=JP&ceid=JP:ja"),
    ("国内政治",    "https://news.google.com/rss/search?q=政治+国会+内閣&hl=ja&gl=JP&ceid=JP:ja"),
    ("経済",       "https://news.google.com/rss/search?q=経済+景気+GDP&hl=ja&gl=JP&ceid=JP:ja"),
    ("金融",       "https://news.google.com/rss/search?q=金融+日銀+金利+株価&hl=ja&gl=JP&ceid=JP:ja"),
]

def get_top_article(url):
    res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    root = ET.fromstring(res.content)
    item = root.find(".//item")
    if item is None:
        return None
    title = item.findtext("title") or "タイトルなし"
    link  = item.findtext("link") or ""
    return {"title": title, "url": link}

def send_to_discord(items):
    jst = timezone(timedelta(hours=9))
    today = datetime.now(jst).strftime("%Y年%m月%d日")

    content = f"**📰 おはようございます！{today}のニュース**\n"
    content += "━━━━━━━━━━━━━━━━━━━━\n\n"

    for label, article in items:
        if article:
            content += f"**【{label}】**\n"
            content += f"📌 {article['title']}\n"
            content += f"🔗 {article['url']}\n\n"
        else:
            content += f"**【{label}】**\n⚠️ 記事が取得できませんでした\n\n"

    content += "━━━━━━━━━━━━━━━━━━━━"
    requests.post(DISCORD_WEBHOOK, json={"content": content})
    print("Discord送信完了")

if __name__ == "__main__":
    items = [(label, get_top_article(url)) for label, url in TOPICS]
    send_to_discord(items)
