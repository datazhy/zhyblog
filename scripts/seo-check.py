#!/usr/bin/env python3
"""构建后 SEO 检查。

用法：先 `bundle exec jekyll build`，再运行本脚本。
逐项对照 SEO 重构要求做静态校验，返回码非 0 表示存在失败项。
"""
import json
import re
import sys
from pathlib import Path

SITE = Path("_site")
ORIGIN = "https://zhanghangyu.com"
OLD_HOSTS = ("zhy.win", "www.zhanghangyu.com")

results = []


def check(name, ok, detail=""):
    results.append((name, ok, detail))


def html_files():
    return sorted(SITE.rglob("*.html"))


def article_files():
    """文章页：/YYYY/MM/DD/slug/index.html"""
    return [p for p in html_files()
            if re.search(r"/\d{4}/\d{2}/\d{2}/[^/]+/index\.html$", str(p))]


def main():
    if not SITE.exists():
        print("❌ 未找到 _site，请先执行 jekyll build")
        return 1

    pages = html_files()
    articles = article_files()

    # 1. 每页只有一个 canonical
    bad = [str(p) for p in pages
           if len(re.findall(r'<link[^>]+rel="canonical"', p.read_text(encoding="utf-8"))) != 1]
    check("1. 每页恰有一个 canonical", not bad, f"异常: {bad[:3]}")

    # 2. canonical 为 HTTPS non-www
    bad = []
    for p in pages:
        m = re.search(r'<link[^>]+rel="canonical"[^>]+href="([^"]+)"', p.read_text(encoding="utf-8"))
        if m and not m.group(1).startswith(ORIGIN):
            bad.append(f"{p}: {m.group(1)}")
    check("2. canonical 均为 https non-www", not bad, f"异常: {bad[:3]}")

    # 3. 页面存在非空 title
    bad = [str(p) for p in pages
           if not (re.search(r"<title>(.+?)</title>", p.read_text(encoding="utf-8"), re.S) or [None])]
    bad = [str(p) for p in pages
           if not re.search(r"<title>\s*\S.*?</title>", p.read_text(encoding="utf-8"), re.S)]
    check("3. 所有页面有非空 title", not bad, f"异常: {bad[:3]}")

    # 4. 文章存在 description
    bad = []
    for p in articles:
        m = re.search(r'<meta name="description" content="([^"]*)"', p.read_text(encoding="utf-8"))
        if not m or not m.group(1).strip():
            bad.append(str(p))
    check("4. 文章均有非空 description", not bad, f"异常: {bad[:3]}")

    # 5. 文章仅一个 H1
    bad = []
    for p in articles:
        n = len(re.findall(r"<h1[\s>]", p.read_text(encoding="utf-8")))
        if n != 1:
            bad.append(f"{p.parent.name}: {n} 个")
    check("5. 文章页只有一个 H1", not bad, f"异常: {bad[:5]}")

    # 6. BlogPosting JSON-LD 可解析
    bad = []
    for p in articles:
        blocks = re.findall(r'<script type="application/ld\+json">(.*?)</script>',
                            p.read_text(encoding="utf-8"), re.S)
        types = []
        for b in blocks:
            try:
                types.append(json.loads(b).get("@type"))
            except Exception as e:
                bad.append(f"{p.parent.name}: 解析失败 {e}")
        if "BlogPosting" not in types:
            bad.append(f"{p.parent.name}: 缺 BlogPosting")
    check("6. 文章 BlogPosting JSON-LD 可解析", not bad, f"异常: {bad[:3]}")

    # 7. 首页 WebSite JSON-LD 可解析
    home = (SITE / "index.html").read_text(encoding="utf-8")
    ok = False
    for b in re.findall(r'<script type="application/ld\+json">(.*?)</script>', home, re.S):
        try:
            if json.loads(b).get("@type") == "WebSite":
                ok = True
        except Exception:
            pass
    check("7. 首页 WebSite JSON-LD 可解析", ok)

    # 8. About ProfilePage JSON-LD 可解析
    about = SITE / "about" / "index.html"
    ok = False
    if about.exists():
        for b in re.findall(r'<script type="application/ld\+json">(.*?)</script>',
                            about.read_text(encoding="utf-8"), re.S):
            try:
                if json.loads(b).get("@type") == "ProfilePage":
                    ok = True
            except Exception:
                pass
    check("8. About ProfilePage JSON-LD 可解析", ok)

    # 9. sitemap 不出现旧域名
    sm = SITE / "sitemap.xml"
    locs = re.findall(r"<loc>([^<]+)</loc>", sm.read_text(encoding="utf-8")) if sm.exists() else []
    bad = [u for u in locs if any(h in u for h in OLD_HOSTS) or u.startswith("http://")]
    check("9. sitemap 无旧域名/http", sm.exists() and not bad, f"异常: {bad[:3]}")

    # 10. 内部链接不出现旧域名
    bad = []
    for p in pages:
        t = p.read_text(encoding="utf-8")
        for h in OLD_HOSTS:
            if re.search(r'href="https?://' + re.escape(h), t):
                bad.append(f"{p}: {h}")
    check("10. 内部链接无旧域名", not bad, f"异常: {bad[:3]}")

    # 11. 不存在意外 noindex（offline.html 是有意为之）
    bad = []
    for p in pages:
        if "noindex" in p.read_text(encoding="utf-8") and p.name != "offline.html":
            bad.append(str(p))
    check("11. 无意外 noindex", not bad, f"异常: {bad[:3]}")

    # 12. sitemap 中的 URL 在构建产物中存在
    bad = []
    for u in locs:
        rel = u.replace(ORIGIN, "").lstrip("/")
        cand = SITE / rel if rel.endswith(".html") else SITE / rel / "index.html"
        if not cand.exists():
            bad.append(u)
    check("12. sitemap URL 均有对应产物", not bad, f"缺失: {bad[:3]}")

    # 13. offline.html 已排除出 sitemap
    check("13. offline.html 不在 sitemap", not any("offline" in u for u in locs))

    # 14. 文章 title 使用统一后缀
    bad = []
    for p in articles:
        m = re.search(r"<title>(.*?)</title>", p.read_text(encoding="utf-8"), re.S)
        if m and "｜张航宇的博客" not in m.group(1):
            bad.append(f"{p.parent.name}: {m.group(1)[:40]}")
    check("14. 文章 title 使用统一品牌后缀", not bad, f"异常: {bad[:3]}")

    width = max(len(n) for n, _, _ in results)
    failed = 0
    for name, ok, detail in results:
        mark = "✅" if ok else "❌"
        print(f"{mark} {name.ljust(width)}" + ("" if ok else f"   {detail}"))
        if not ok:
            failed += 1

    print(f"\n共 {len(results)} 项，失败 {failed} 项"
          f"（页面 {len(pages)}，文章 {len(articles)}，sitemap {len(locs)}）")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
