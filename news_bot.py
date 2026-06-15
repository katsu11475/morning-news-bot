import os
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta

DISCORD_WEBHOOK = os.environ["DISCORD_WEBHOOK"]

TOPICS = [
    ("M&A", [
        "https://maonline.jp/feed",
        "https://toyokeizai.net/list/feed/rss",
        "https://jp.reuters.com/rssFeed/businessNews",
    ]),
    ("AI", [
        "https://www.itmedia.co.jp/news/rss/2.0/itmedianews.xml",
        "https://www.zdnet.com/topic/artificial-intelligence/rss.xml",
        "https://pc.watch.impress.co.jp/data/rss/1.0/pcw/feed.rdf",
    ]),
    ("国内政治", [
        "https://www3.nhk.or.jp/rss/news/cat4.xml",
        "https://www.asahi.com/rss/asahi/newsheadlines.rdf",
    ]),
    ("経済", [
        "https://jp.reuters.com/rssFeed/businessNews",
        "https://www.bbc.com/japanese/topics/ckdxnx2s4gxt/rss.xml",
    ]),
    ("金融", [
        "https://jp.reuters.com/rssFeed/businessNews",
        "https://www.bloomberg.co.jp/feeds/bbiz",
    ]),
]

def get_top_article(rss_urls):
    headers = {"User-Agent": "Mozilla/5.0"}
    for url in rss_urls:
        try:
            res = requests.get(url, headers=headers, timeout=5)
            root = ET.fromstring(res.content)
            item = root.find(".//item")
            if item is not None:
                title = item.findtext("title") or "タイトルなし"
                link  = item.findtext("link") or ""
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
    items = [(label, get_top_article(urls)) for label, urls in TOPICS]
    send_to_discord(items)
