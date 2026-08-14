#!/usr/bin/env python3
"""构建后图片优化：懒加载 + 显式尺寸（消除 CLS）+ 异步解码。

只改 _site 里的产物，不动文章源文件。
- 首图保持 eager（LCP 不受影响），其余 loading="lazy"
- 补 width/height，浏览器可提前预留空间，避免累积布局偏移（CLS）
用法：bundle exec jekyll build && python3 scripts/optimize-images.py
"""
import re
import struct
import subprocess
import sys
from pathlib import Path

SITE = Path("_site")
_dim_cache = {}


def png_size(data):
    if data[:8] == b"\x89PNG\r\n\x1a\n" and data[12:16] == b"IHDR":
        return struct.unpack(">II", data[16:24])
    return None


def jpeg_size(data):
    i = 2
    while i < len(data) - 9:
        if data[i] != 0xFF:
            i += 1
            continue
        marker = data[i + 1]
        if marker in (0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7,
                      0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF):
            h, w = struct.unpack(">HH", data[i + 5:i + 9])
            return w, h
        seg = struct.unpack(">H", data[i + 2:i + 4])[0]
        i += 2 + seg
    return None


def svg_size(path):
    try:
        txt = path.read_text(encoding="utf-8", errors="ignore")[:2000]
        m = re.search(r'viewBox="[\d.]+\s+[\d.]+\s+([\d.]+)\s+([\d.]+)"', txt)
        if m:
            return int(float(m.group(1))), int(float(m.group(2)))
    except Exception:
        pass
    return None


def dimensions(src):
    """src 形如 /img/in-post/x.png"""
    if src in _dim_cache:
        return _dim_cache[src]
    p = SITE / src.lstrip("/")
    result = None
    if p.exists():
        try:
            if p.suffix.lower() == ".svg":
                result = svg_size(p)
            else:
                data = p.read_bytes()
                result = png_size(data) or jpeg_size(data)
        except Exception:
            result = None
    _dim_cache[src] = result
    return result


def main():
    if not SITE.exists():
        print("❌ 未找到 _site，请先执行 jekyll build")
        return 1

    changed = lazified = sized = 0

    for html in SITE.rglob("*.html"):
        text = html.read_text(encoding="utf-8")
        original = text
        # 只处理正文区域的图片，避开导航/页头的装饰图
        seen = {"n": 0}

        def repl(m):
            tag = m.group(0)
            if "loading=" in tag or "data-no-opt" in tag:
                return tag
            src_m = re.search(r'src="([^"]+)"', tag)
            if not src_m:
                return tag
            src = src_m.group(1)
            if src.startswith(("http://", "https://", "data:")):
                return tag

            seen["n"] += 1
            add = []
            # 首张图不懒加载，避免拖慢 LCP
            if seen["n"] > 1:
                add.append('loading="lazy"')
                nonlocal_counter["lazy"] += 1
            add.append('decoding="async"')

            if "width=" not in tag and "height=" not in tag:
                dim = dimensions(src)
                if dim:
                    add.append(f'width="{dim[0]}" height="{dim[1]}"')
                    nonlocal_counter["size"] += 1

            # 去掉结尾的 ">" 以及 XHTML 风格的自闭合斜杠，避免拼出 `" / loading=...`
            body = tag[:-1].rstrip()
            if body.endswith("/"):
                body = body[:-1].rstrip()
            return body + " " + " ".join(add) + ">"

        nonlocal_counter = {"lazy": 0, "size": 0}
        # 仅在文章/页面正文容器内替换
        body_pat = re.compile(r'(<div class="[^"]*post-container[^"]*">)(.*?)(</article>|</div>\s*</div>\s*</div>)',
                              re.S)

        def body_repl(bm):
            inner = re.sub(r"<img\b[^>]*>", repl, bm.group(2))
            return bm.group(1) + inner + bm.group(3)

        text = body_pat.sub(body_repl, text)

        if text != original:
            html.write_text(text, encoding="utf-8")
            changed += 1
            lazified += nonlocal_counter["lazy"]
            sized += nonlocal_counter["size"]

    print(f"✅ 处理 {changed} 个页面：懒加载 {lazified} 张，补充尺寸 {sized} 张")
    return 0


if __name__ == "__main__":
    sys.exit(main())
