import os
import hashlib
import requests
from bs4 import BeautifulSoup
from pathlib import Path

DISCORD_WEBHOOK = os.environ["DISCORD_WEBHOOK"]
HASH_FILE = "stamp_last_hash.txt"
URL = "https://www.post.japanpost.jp/enjoy/culture/stamp/fuke/"


def fetch_page_content():
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    res = requests.get(URL, headers=headers, timeout=10)
    res.raise_for_status()
    soup = BeautifulSoup(res.content, "html.parser")

    for tag in soup(["script", "style", "nav", "header", "footer", "noscript"]):
        tag.decompose()

    main = (
        soup.find("main")
        or soup.find("div", id="main")
        or soup.find("div", id="content")
        or soup.find("div", class_="content")
        or soup.body
    )
    return main.get_text(separator="\n", strip=True) if main else ""


def load_hash():
    p = Path(HASH_FILE)
    return p.read_text().strip() if p.exists() else ""


def save_hash(h):
    Path(HASH_FILE).write_text(h + "\n")


def compute_hash(text):
    return hashlib.sha256(text.encode()).hexdigest()


def notify_discord():
    content = (
        "📮 **日本郵便 風景印ページが更新されました！**\n"
        f"🔗 {URL}"
    )
    requests.post(DISCORD_WEBHOOK, json={"content": content})
    print("Discord通知を送信しました")


if __name__ == "__main__":
    text = fetch_page_content()
    if not text:
        print("ページの取得に失敗しました")
        raise SystemExit(1)

    new_hash = compute_hash(text)
    old_hash = load_hash()

    if not old_hash:
        print("初回実行: ハッシュを保存しました")
        save_hash(new_hash)
    elif new_hash != old_hash:
        print("更新を検出しました！Discord に通知します")
        notify_discord()
        save_hash(new_hash)
    else:
        print("更新なし")
