import os
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta

DISCORD_WEBHOOK = os.environ["DISCORD_WEBHOOK"]

TOPICS = [
    ("M&A", [
        "https://maonline.jp/feed",
        "https://toyokeizai.net/list/feed/rss",
        "https://feeds.reuters.com/reuters/JPbusiness",
    ]),
    ("AI", [
        "https://rss.itmedia.co.jp/rss/2.0/aiplus.xml",
        "https://xtech.nikkei.com/rss/xtech-it.rdf",
        "https://wired.jp/feed/",
    ]),
    ("国内政治", [
        "https://www3.nhk.or.jp/rss/news/cat4.xml",
        "https://www.asahi.com/rss/asahi/newsheadlines.rdf",
    ]),
    ("経済", [
        "https://toyokeizai.net/list/feed/rss",
        "https://feeds.reuters.com/reuters/JPeconomics",
        "https://www.asahi.com/rss/asahi/newsheadlines.rdf",
    ]),
    ("金融", [
        "https://www3.nhk.or.jp/rss/news/cat5.xml",
        "https://www.jiji.com/rss/ranking.rdf",
        "https://feeds.reuters.com/reuters/JPbusiness",
    ]),
]

def get_top_article(rss_urls, used_urls):
    headers = {"User-Agent": "Mozilla/5.0"}
    for url in rss_urls:
        try:
            res = requests.get(url, headers=headers, timeout=5)
            root = ET.fromstring(res.content)
            for item in root.findall(".//item"):
                title = item.findtext("title") or "タイトルなし"
                link  = item.findtext("link") or ""
                if link and link not in used_urls:
                    used_urls.add(link)
                    source = url.split("/")[2].replace("www.", "")
                    return {"title": title, "url": link, "source": source}
        except Exception:
            continue
    return None

def send_to_discord(items):
    jst = timezone(timedelta(hours=9))
    today = datetime.now(jst).strftime("%Y年%m月%d日")

    content = f"**📰 おはようございます！{today}のニュース**\n"
    content += "━━━━━━━━━━━━━━━━━━━━\n\n"

    for label, article in items:
        if article:
            content += f"**【{label}】** `{article['source']}`\n"
            content += f"📌 {article['title']}\n"
            content += f"🔗 {article['url']}\n\n"
        else:
            content += f"**【{label}】**\n⚠️ 記事が取得できませんでした\n\n"

    content += "━━━━━━━━━━━━━━━━━━━━"
    requests.post(DISCORD_WEBHOOK, json={"content": content})
    print("Discord送信完了")

if __name__ == "__main__":
    used_urls = set()
    items = [(label, get_top_article(urls, used_urls)) for label, urls in TOPICS]
    send_to_discord(items)
