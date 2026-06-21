#!/usr/bin/env python3
"""
GitHub Actions シークレットを設定するスクリプト。

使い方:
  GITHUB_TOKEN=ghp_xxx python3 scripts/set_github_secret.py \
      --repo katsu11475/morning-news-bot \
      --name NOTION_API_KEY \
      --value ntn_xxx

環境変数:
  GITHUB_TOKEN  - repo スコープ付きの GitHub Personal Access Token
"""

import argparse
import base64
import json
import os
import sys
import urllib.request

from nacl import encoding, public


def get_repo_public_key(owner: str, repo: str, token: str) -> dict:
    url = f"https://api.github.com/repos/{owner}/{repo}/actions/secrets/public-key"
    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    })
    with urllib.request.urlopen(req) as res:
        return json.loads(res.read())


def encrypt_secret(public_key_b64: str, secret_value: str) -> str:
    pk = public.PublicKey(public_key_b64.encode(), encoding.Base64Encoder())
    box = public.SealedBox(pk)
    encrypted = box.encrypt(secret_value.encode())
    return base64.b64encode(encrypted).decode()


def set_secret(owner: str, repo: str, name: str, encrypted_value: str, key_id: str, token: str):
    url = f"https://api.github.com/repos/{owner}/{repo}/actions/secrets/{name}"
    payload = json.dumps({
        "encrypted_value": encrypted_value,
        "key_id": key_id,
    }).encode()
    req = urllib.request.Request(url, data=payload, method="PUT", headers={
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "Content-Type": "application/json",
        "X-GitHub-Api-Version": "2022-11-28",
    })
    with urllib.request.urlopen(req) as res:
        return res.status


def main():
    parser = argparse.ArgumentParser(description="GitHub Actions secret setter")
    parser.add_argument("--repo", required=True, help="owner/repo 形式")
    parser.add_argument("--name", required=True, help="シークレット名")
    parser.add_argument("--value", help="シークレット値（省略時は環境変数 SECRET_VALUE を使用）")
    args = parser.parse_args()

    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        print("エラー: 環境変数 GITHUB_TOKEN が設定されていません", file=sys.stderr)
        sys.exit(1)

    secret_value = args.value or os.environ.get("SECRET_VALUE")
    if not secret_value:
        print("エラー: --value または環境変数 SECRET_VALUE でシークレット値を指定してください", file=sys.stderr)
        sys.exit(1)

    owner, repo = args.repo.split("/", 1)

    print(f"公開鍵を取得中: {owner}/{repo}")
    key_data = get_repo_public_key(owner, repo, token)

    print("シークレットを暗号化中...")
    encrypted = encrypt_secret(key_data["key"], secret_value)

    print(f"シークレット '{args.name}' を設定中...")
    status = set_secret(owner, repo, args.name, encrypted, key_data["key_id"], token)

    if status in (201, 204):
        print(f"完了: '{args.name}' を設定しました。")
    else:
        print(f"警告: ステータスコード {status}", file=sys.stderr)


if __name__ == "__main__":
    main()
