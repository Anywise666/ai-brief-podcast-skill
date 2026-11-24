#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""当 git push 因代理/网络不可用时，改走 GitHub REST API 推送本地最新提交。

背景：Windows 本地代理可能间歇性拦截 github.com 的 git 传输（SSL handshake /
CONNECT 502），但 api.github.com 往往仍可用。本脚本从 git 凭据取 token，
走 Git Data API（blob base64 → tree → commit → update ref）完成推送，
支持二进制文件（mp3），最后 fetch + reset --soft 对齐本地分支。

由 ensure_today.sh 在 git push 失败后自动调用，也可单独运行。

输出：PUSH_OK <sha> / NO_CHANGES / PUSH_FAILED <原因>
用法：python scripts/push_via_api.py
"""
import base64
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.dirname(HERE)
API = "https://api.github.com"


def run(cmd):
    return subprocess.run(cmd, cwd=WORK, capture_output=True, text=True)


def get_token():
    p = subprocess.run(["git", "credential", "fill"],
                       input="protocol=https\nhost=github.com\n\n",
                       capture_output=True, text=True)
    cred = {}
    for line in p.stdout.splitlines():
        if "=" in line:
            k, v = line.split("=", 1)
            cred[k] = v
    return cred.get("password", "")


def get_owner_repo():
    """从 git remote origin 解析 owner/repo，支持 https 与 git@ 两种写法。"""
    url = run(["git", "remote", "get-url", "origin"]).stdout.strip()
    m = re.search(r"github\.com[:/]([^/]+)/([^/.]+?)(?:\.git)?$", url)
    if not m:
        raise RuntimeError("无法从 origin 解析 owner/repo: " + url)
    return m.group(1), m.group(2)


TOKEN = get_token()
if not TOKEN:
    print("PUSH_FAILED 无法获取 GitHub 凭据")
    sys.exit(1)

H = {"Authorization": "Bearer " + TOKEN,
     "Accept": "application/vnd.github+json",
     "User-Agent": "ai-brief-podcast-fallback/1.1",
     "X-GitHub-Api-Version": "2022-11-28"}


def req(method, path, data=None):
    url = API + path
    body = json.dumps(data).encode() if data is not None else None
    r = urllib.request.Request(url, data=body, headers=H, method=method)
    last = None
    for a in range(5):
        try:
            with urllib.request.urlopen(r, timeout=45) as resp:
                return json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            last = "HTTP %d %s" % (e.code, e.read().decode()[:200])
            if e.code < 500:
                raise RuntimeError(last)
        except Exception as e:
            last = repr(e)[:150]
        time.sleep(2 * (a + 1))
    raise RuntimeError(last or "unknown")


def main():
    owner, repo = get_owner_repo()
    branch = run(["git", "branch", "--show-current"]).stdout.strip() or "main"
    print("  API target: %s/%s@%s" % (owner, repo, branch))

    ref = req("GET", "/repos/%s/%s/git/ref/heads/%s" % (owner, repo, branch))
    sha = ref["object"]["sha"]
    commit = req("GET", "/repos/%s/%s/git/commits/%s" % (owner, repo, sha))
    base_tree = commit["tree"]["sha"]

    # 本地 HEAD 相对父提交的变更文件（兜底脚本先 commit 再调用本脚本）
    # core.quotepath=false：否则 git 会把中文文件名转义成八进制（\344\270...），
    # 导致 os.path.isfile 找不到文件而静默跳过（曾漏推 listing/README-上架说明.md）
    out = run(["git", "-c", "core.quotepath=false", "diff-tree",
               "--no-commit-id", "--name-only", "-r", "HEAD"]).stdout
    files = [f for f in out.splitlines() if f.strip()]
    if not files:
        print("NO_CHANGES")
        return

    items = []
    for path in files:
        full = os.path.join(WORK, path)
        if not os.path.isfile(full):
            continue
        raw = open(full, "rb").read()
        blob = req("POST", "/repos/%s/%s/git/blobs" % (owner, repo),
                   {"content": base64.b64encode(raw).decode(), "encoding": "base64"})
        items.append({"path": path, "mode": "100644", "type": "blob", "sha": blob["sha"]})
    if not items:
        print("PUSH_FAILED 无有效文件")
        return

    tree = req("POST", "/repos/%s/%s/git/trees" % (owner, repo),
               {"base_tree": base_tree, "tree": items})
    msg = run(["git", "log", "-1", "--pretty=%B"]).stdout.strip()
    new_commit = req("POST", "/repos/%s/%s/git/commits" % (owner, repo),
                     {"message": msg or "Fallback update (via API)",
                      "tree": tree["sha"], "parents": [sha]})
    req("PATCH", "/repos/%s/%s/git/refs/heads/%s" % (owner, repo, branch),
        {"sha": new_commit["sha"], "force": False})

    # 对齐本地：内容已在远端，soft reset 后 index 与 HEAD 一致，工作区干净
    run(["git", "fetch", "origin", branch])
    run(["git", "reset", "--soft", "origin/" + branch])
    print("PUSH_OK", new_commit["sha"][:10])


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("PUSH_FAILED", repr(e)[:200])
        sys.exit(1)
