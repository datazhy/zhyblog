---
layout:       post
title:        "For $2 a Month, AI Translates the X Creators I Follow and Delivers Their Posts to Feishu"
subtitle:     "Why I Rejected the Official API and Built a Self-Hosted X Monitor, Translator, and Daily Intelligence Brief"
description:  "The official X API was too expensive, so I built a self-hosted alternative: near-real-time webhook ingestion for original posts, DeepSeek translation and analysis, Feishu delivery, and a daily morning intelligence brief—all for about $2 per month."
date:         2026-08-13 12:00:00 +0800
author:       "Zhy"
catalog:      true
header-style: text
lang:         en
permalink:    /en/2026/08/13/x-monitor-feishu/
translation_url: /2026/08/13/x-monitor-feishu/
cover:        /img/covers/x-monitor-feishu.png
tags:
    - Open Source
    - Python
    - AI
    - Docker
    - Self-hosting
---
## Why I Built It: My Watchlist Became Impossible to Keep Up With

I follow a group of high-quality creators on X, most of whom write about U.S. stocks and technology. Over time, however, keeping up with the feed became a burden:

- **There is simply too much content**: dozens of accounts can publish hundreds of posts a day, and reading everything can take all morning;
- **Reading in English takes longer**, so I am more likely to skip long posts;
- **Important signals get buried** under reposts, replies, and everyday chatter;
- **By the next day, I forget** what everyone was discussing, let alone notice a cross-day signal such as “this topic has come up for three days in a row.”

This kind of information is also time-sensitive. When certain accounts mention a ticker, the market may react before the opening bell. Seeing the post in real time and seeing it two hours later are completely different experiences.

What I wanted was simple: **deliver only original posts, translate them into Chinese automatically, summarize the important ones, and send me a recap the following morning.**

I built the system incrementally with a vibe-coding workflow. It has now been running reliably for a while, and the code is open source:

> **[github.com/datazhy/x-monitor-feishu](https://github.com/datazhy/x-monitor-feishu)** — MIT licensed; stars, issues, and pull requests are welcome

---

## The First Roadblock: The Official API Was Too Expensive

My first instinct was to use the official X API. The conclusion was straightforward: **for an individual developer, it was not economically viable.**

The free tier’s read quota was too low to be useful. The next tier started at about $200 per month, with higher tiers costing thousands. Paying hundreds of dollars each month just to monitor a few dozen accounts made no sense for a personal project.

I therefore switched to a third-party data provider and chose **TwitterAPI.io**. It is pay-as-you-go, has no minimum commitment, and **supports filter rules plus webhooks**. That last feature is important: I do not need to build my own polling loop. When a post matches a rule, the service calls my webhook.

Based on actual usage, the entire system costs about **$2 per month**, including AI translation and analysis—roughly two orders of magnitude cheaper than a $200 monthly plan.

---

## What the Finished System Looks Like

**Real-time post delivery** — English posts are shown as Chinese translations while preserving the original paragraph structure; longer posts also include an AI-generated analysis:

![X tweet monitoring sample message pushed to Feishuqun, including Chinese translation and AI analysis](/img/in-post/x-monitor-sample-tweet.svg)

**A daily “Yesterday’s Signals” brief at 9:00 a.m.** — It starts with the tickers mentioned the previous day, followed by the main narrative, the three most important developments, topic heat, and multi-day trends:

![Daily Intelligence Morning Post Feishu interactive card sample, including stock mentions, main conclusions and topic popularity](/img/in-post/x-monitor-sample-report.svg)

<sub>The two images above are mockups using fictional data; their layout matches the production messages.</sub>

---

## Overall Architecture

```
TwitterAPI.io Filter Rule (webhook)
        │  HTTPS + a long random secret
        ▼
FastAPI receiver ──► SQLite (tweet_id deduplication + idempotent delivery)
        │
        ├─► Real-time flow: translation + AI analysis (DeepSeek) → Feishu (route creators to different groups)
        │
        └─► Generate a daily brief at 09:00 Beijing time:
              Denoise / classify / aggregate all posts (low-cost model)
            → Python calculates hard metrics (heat / trend / persistence / anomalies / ticker mentions)
            → Writing (stronger model) → Feishu interactive card
```

The stack is deliberately simple: **FastAPI + SQLite + APScheduler + Docker**. A small 1-vCPU, 1-GB server is enough. The LLM layer needs only one DeepSeek API key for translation, per-post analysis, and daily-brief writing.

### Three Design Principles Worth Highlighting

**1. Let the cheaper model process the full stream; reserve the stronger model for filtered highlights.**

The daily brief is generated in two stages. A low-cost model first denoises, classifies, and aggregates the previous day’s posts. A stronger model then writes from that compressed result. Feeding every raw post directly to the stronger model would multiply the cost without producing a comparable improvement in quality.

**2. Calculate deterministic metrics in Python; never ask the model to invent them.**

Metrics such as topic heat, consecutive-day counts, and posting-volume spikes are calculated in code. Ticker mentions are extracted from cashtags such as `$MU` with regular expressions and ranked by frequency. **The model only fills in the company name.**

I made this a hard rule after being burned by plausible-looking hallucinated numbers: if a value can be calculated, the model must not guess it.

**3. Filter noise at the API layer, not after downloading it.**

The filter rule includes `-is:retweet -is:reply -is:quote`, so reposts, replies, and quoted posts are excluded at the source. This keeps the feed focused and lowers the bill because fewer posts are returned. A second local filter acts as a safeguard.

---

## Real-World Cost: Polling, Not AI, Is the Main Expense

This was the most counterintuitive lesson from the project.

TwitterAPI.io is usage-based, but one detail is easy to miss: **each rule check consumes credits**. In my testing, one check cost about 14 credits, **even when it returned zero posts**.

The practical cost formula is therefore `number of rules × polling frequency`. Shorter intervals cost more; billing is not based only on the number of posts returned.

One representative bill (18 creators, 4 rules, 10-minute intervals, about 55 posts per day):

| Item | 7-day spend | Share |
|---|---|---|
| TwitterAPI rule checks | $0.24 | 59% |
| Posts returned by TwitterAPI | $0.06 | 15% |
| DeepSeek (translation, analysis, and daily brief) | $0.10 | 26% |
| **Total** | **$0.40** | About **$1.70 per month** |

**About 60% of the cost goes to asking whether any new posts exist; AI accounts for only about a quarter.**

To reduce costs further, the most effective steps are to lengthen the polling interval and consolidate rules—not to switch to a cheaper model, which can save only part of the 26% AI share.

The project includes a `cost.py` script that estimates spending from measured token usage and rule-check counts, then sends a cost report to the monitoring group every seven days. Model pricing can also be calibrated in `.env` against the real bill. **For self-hosted services, cost visibility matters as much as functionality**; otherwise, spending can quietly drift upward.

---

## Reliability Work

The biggest risk with a self-hosted service is not a visible failure—it is a silent failure that goes unnoticed. Reliability therefore took more work than the core feature set:

- **Deduplication and idempotency**: a unique `tweet_id` index plus delivery records prevents duplicate messages after a container restart;
- **Retries on failure**: failed deliveries retry after 1, 5, 15, 30, and 60 minutes; exhausted retries enter a dead-letter queue and trigger an alert;
- **Daily heartbeat checks**: verify rule status, API keys, account balance, webhook connectivity, and the delivery queue, then alert on anomalies;
- **Handle-change detection**: compare `user_id` values monthly so a creator changing their username does not silently break monitoring;
- **A separate monitoring group**: heartbeat, cost, and failure messages go through a dedicated Feishu bot instead of cluttering the content channel.

---

## Deployment

Prerequisites: a Docker-enabled server (1 vCPU and 1 GB of RAM is enough), a domain managed by Cloudflare, a TwitterAPI.io key, a DeepSeek key, and a Feishu group bot.

Then a command:

```bash
git clone https://github.com/datazhy/x-monitor-feishu.git x-monitor
cd x-monitor
bash deploy/install.sh
```

The script will check the Docker environment, generate `.env`, automatically generate the webhook secret, prompt you to fill in the configuration one by one, build the startup container, and perform health checks.

Caddy automatically issues and renews the HTTPS certificate through **Cloudflare DNS-01**. It listens on a separate port (8443 by default) and **does not occupy ports 80 or 443**, so existing services are unaffected.

The remaining external setup—adding a Cloudflare A record, entering the webhook URL in the TwitterAPI.io console, and listing creators in `config/rules.yml`—is documented in the README.

One important caveat: **the Cloudflare A record must be set to DNS only**. Enabling the proxied “orange cloud” blocks the non-standard port and prevents webhook delivery.

---

## Limitations and Notes

- **SQLite** is sufficient for a single self-hosted instance. At larger scale, replace it with PostgreSQL by swapping the `db.py` implementation.
- **Feishu** is currently the primary delivery channel. The architecture leaves room for other channels, but they are not fully implemented.
- DeepSeek is the default LLM, but translation, analysis, and daily-brief generation can each use a different provider. Any service compatible with the OpenAI `/chat/completions` protocol can be configured by changing the base URL.
- This system only aggregates and summarizes information. Prompts explicitly prohibit trading recommendations and fabricated numbers, but AI-generated content can still be wrong. Verify important claims against the original post.

---

## Final Thoughts

The motivation was personal: I simply did not want to miss updates from a few creators. After building it, however, I found that the hard parts were not API integration, but cost accounting, failure detection, and preventing the model from producing plausible nonsense.

If you have a similar need—not necessarily for U.S. stocks; the same approach works for X creators in any field—you are welcome to try it or submit an issue or pull request:

> **[github.com/datazhy/x-monitor-feishu](https://github.com/datazhy/x-monitor-feishu)**

---

## Related Resources

1. [datazhy/x-monitor-feishu](https://github.com/datazhy/x-monitor-feishu) — Source code of this project (MIT)
2. [TwitterAPI.io](https://twitterapi.io/) — The third-party tweet data source used in this article, billed by volume
3. [DeepSeek Open Platform](https://platform.deepseek.com/) — LLM used for translation, item-by-item analysis and morning newspaper writing

The cost data in this article comes from actual billing on my account (18 creators, four rules, and a 10-minute polling interval).
The costs for different configurations will vary significantly.