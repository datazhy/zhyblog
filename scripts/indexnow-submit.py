#!/usr/bin/env python3
"""Submit the live sitemap URLs to IndexNow after a Cloudflare Pages deploy."""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path


INDEXNOW_ENDPOINT = "https://api.indexnow.org/indexnow"
CLOUDFLARE_APP_SLUG = "cloudflare-workers-and-pages"
USER_AGENT = "zhanghangyu.com IndexNow publisher/1.0"


def request(url: str, *, data: bytes | None = None, headers: dict[str, str] | None = None):
    merged_headers = {"User-Agent": USER_AGENT}
    if headers:
        merged_headers.update(headers)
    return urllib.request.urlopen(
        urllib.request.Request(url, data=data, headers=merged_headers), timeout=30
    )


def wait_for_cloudflare_deploy(timeout_seconds: int) -> None:
    repository = os.environ.get("GITHUB_REPOSITORY")
    commit_sha = os.environ.get("GITHUB_SHA")
    token = os.environ.get("GITHUB_TOKEN")
    if not repository or not commit_sha:
        raise RuntimeError("GITHUB_REPOSITORY and GITHUB_SHA are required")

    api_url = (
        f"https://api.github.com/repos/{repository}/commits/{commit_sha}/check-runs"
        "?filter=latest&per_page=100"
    )
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"

    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        with request(api_url, headers=headers) as response:
            checks = json.load(response).get("check_runs", [])
        cloudflare_checks = [
            check
            for check in checks
            if (check.get("app") or {}).get("slug") == CLOUDFLARE_APP_SLUG
        ]
        if cloudflare_checks:
            check = cloudflare_checks[0]
            status = check.get("status")
            conclusion = check.get("conclusion")
            print(f"Cloudflare Pages: status={status}, conclusion={conclusion}")
            if status == "completed":
                if conclusion == "success":
                    return
                raise RuntimeError(f"Cloudflare Pages deployment ended with {conclusion}")
        else:
            print("Cloudflare Pages check has not appeared yet")
        time.sleep(10)

    raise TimeoutError("Timed out waiting for the Cloudflare Pages deployment")


def read_sitemap(sitemap_url: str, expected_host: str) -> list[str]:
    cache_buster = urllib.parse.urlencode({"indexnow": int(time.time())})
    separator = "&" if "?" in sitemap_url else "?"
    with request(f"{sitemap_url}{separator}{cache_buster}") as response:
        root = ET.fromstring(response.read())

    urls = []
    for element in root.findall("{http://www.sitemaps.org/schemas/sitemap/0.9}url"):
        loc = element.find("{http://www.sitemaps.org/schemas/sitemap/0.9}loc")
        if loc is None or not loc.text:
            continue
        url = loc.text.strip()
        parsed = urllib.parse.urlparse(url)
        if parsed.scheme != "https" or parsed.netloc != expected_host:
            raise ValueError(f"Sitemap URL is outside https://{expected_host}: {url}")
        urls.append(url)

    if not urls:
        raise ValueError("No URLs found in the live sitemap")
    if len(urls) > 10_000:
        raise ValueError("IndexNow accepts at most 10,000 URLs per request")
    return urls


def verify_live_key(host: str, key: str, timeout_seconds: int) -> str:
    key_location = f"https://{host}/{key}.txt"
    deadline = time.monotonic() + timeout_seconds
    last_error = "key file is not live yet"
    while time.monotonic() < deadline:
        cache_buster = urllib.parse.urlencode({"indexnow": int(time.time())})
        try:
            with request(
                f"{key_location}?{cache_buster}", headers={"Cache-Control": "no-cache"}
            ) as response:
                body = response.read().decode("utf-8").strip()
            if body == key:
                return key_location
            last_error = "live key file content does not match the local key"
        except (OSError, urllib.error.HTTPError) as error:
            last_error = str(error)
        time.sleep(5)
    raise RuntimeError(f"IndexNow key verification failed: {last_error}")


def submit(host: str, key: str, key_location: str, urls: list[str]) -> int:
    payload = json.dumps(
        {
            "host": host,
            "key": key,
            "keyLocation": key_location,
            "urlList": urls,
        }
    ).encode("utf-8")
    try:
        with request(
            INDEXNOW_ENDPOINT,
            data=payload,
            headers={"Content-Type": "application/json; charset=utf-8"},
        ) as response:
            status = response.status
    except urllib.error.HTTPError as error:
        status = error.code

    if status not in (200, 202):
        raise RuntimeError(f"IndexNow rejected the request with HTTP {status}")
    return status


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="zhanghangyu.com")
    parser.add_argument("--sitemap", default="https://zhanghangyu.com/sitemap.xml")
    parser.add_argument("--key-file", required=True, type=Path)
    parser.add_argument("--wait-for-cloudflare", action="store_true")
    parser.add_argument("--deploy-timeout", type=int, default=600)
    parser.add_argument("--key-timeout", type=int, default=90)
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    key = args.key_file.read_text(encoding="utf-8").strip()
    if not 8 <= len(key) <= 128 or any(not (c.isalnum() or c == "-") for c in key):
        raise ValueError("IndexNow key must be 8-128 letters, numbers, or dashes")

    if args.wait_for_cloudflare:
        wait_for_cloudflare_deploy(args.deploy_timeout)

    urls = read_sitemap(args.sitemap, args.host)
    key_location = f"https://{args.host}/{key}.txt"
    payload = {
        "host": args.host,
        "key": key,
        "keyLocation": key_location,
        "urlList": urls,
    }
    if args.dry_run:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        print(f"Dry run: {len(urls)} URLs would be submitted")
        return 0

    key_location = verify_live_key(args.host, key, args.key_timeout)
    status = submit(args.host, key, key_location, urls)
    print(f"IndexNow accepted {len(urls)} URLs with HTTP {status}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        print(f"IndexNow submission failed: {error}", file=sys.stderr)
        raise SystemExit(1)
