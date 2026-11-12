#!/usr/bin/env python3
# Generate complete HTML drafts for the 出海独立站怎么选服务器 cluster.
# Does not deploy or modify /workspace/fwqabc.

from __future__ import annotations

import html
import json
import re
from pathlib import Path
from urllib.parse import quote

from bs4 import BeautifulSoup

ROOT = Path("/workspace/fwqabc-cluster")
LIVE_KNOWLEDGE = Path("/tmp/fwqabc-live/knowledge_cn2-gia.html")
AFTERFOOTER = Path("/tmp/fwqabc-extract/k-cn2-afterfooter.html")

SITE = "https://fwqabc.com"
PUBLISHER = {
    "@type": "Organization",
    "name": "fwqabc 出海ABC",
    "logo": {"@type": "ImageObject", "url": f"{SITE}/favicon.ico"},
}
OG_IMAGE = f"{SITE}/brand/og-default-1200x630.jpg"
DATE_ISO = "2026-11-12T15:30:00+08:00"
DATE_VISIBLE = "2026年11月12日"
CHECK_DATE = "2026-11-12（北京时间）"
STYLESHEET = "/assets/css/stylesheet.457ed999efbc904d07ed65e66f03860267045989ce8bf517433b08f035f863ba.css"
INTEGRITY = "sha256-RX7Zme+8kE0H7WXmbwOGAmcEWYnOi/UXQzsI8DX4Y7o="
THEME_JS = (
    'localStorage.getItem("pref-theme")==="dark"?document.querySelector("html").dataset.theme="dark":'
    'localStorage.getItem("pref-theme")==="light"?document.querySelector("html").dataset.theme="light":'
    'window.matchMedia("(prefers-color-scheme: dark)").matches?document.querySelector("html").dataset.theme="dark":'
    'document.querySelector("html").dataset.theme="light"'
)
NOSCRIPT = (
    "<noscript><style>#theme-toggle,.top-link{display:none}</style>"
    "<style>@media(prefers-color-scheme:dark){:root{--theme:#131720;--entry:#1a2130;--primary:#ecf0f3;"
    "--secondary:#a7b0bd;--tertiary:#2a3342;--content:#ecf0f3;--code-block-bg:#1a2130;--code-bg:#1c2330;"
    "--border:#2c3544;color-scheme:dark}.list{background:var(--theme)}.toc{background:var(--entry)}}"
    "</style></noscript>"
)
CHEVRON = (
    '<svg class="feather feather-chevron-right" fill="none" stroke="currentColor" '
    'stroke-linecap="round" stroke-linejoin="round" stroke-width="2" viewBox="0 0 24 24">'
    "<polyline points=\"9 18 15 12 9 6\"></polyline></svg>"
)


def load_chrome():
    soup = BeautifulSoup(LIVE_KNOWLEDGE.read_text(), "html.parser")
    lang = soup.header.select_one("a.lang-switch")
    if lang:
        lang["href"] = f"{SITE}/en/"
    return str(soup.header), str(soup.footer), AFTERFOOTER.read_text()


def anchor_id(text: str) -> str:
    return re.sub(r"\s+", "", text)


def href_id(text: str) -> str:
    return quote(anchor_id(text), safe="").lower()


def heading(tag: str, text: str) -> str:
    aid = anchor_id(text)
    return (
        f'<{tag} id="{html.escape(aid, quote=True)}">{html.escape(text)}'
        f'<a class="anchor" hidden="" aria-hidden="true" href="#{html.escape(aid, quote=True)}">#</a>'
        f"</{tag}>"
    )


def toc_html(items: list) -> str:
    """items: list of str or (str, list[str])"""
    lis = []
    for item in items:
        if isinstance(item, tuple):
            title, children = item
            inner = "".join(
                f'<li><a href="#{href_id(c)}" aria-label="{html.escape(c, quote=True)}">{html.escape(c)}</a></li>'
                for c in children
            )
            lis.append(
                f'<li><a href="#{href_id(title)}" aria-label="{html.escape(title, quote=True)}">{html.escape(title)}</a><ul>{inner}</ul></li>'
            )
        else:
            lis.append(
                f'<li><a href="#{href_id(item)}" aria-label="{html.escape(item, quote=True)}">{html.escape(item)}</a></li>'
            )
    return (
        '<details class="toc" open="">'
        '<summary accesskey="c" title="(Alt + C)"><span class="title">目录</span></summary>'
        f'<div class="inner"><ul>{"".join(lis)}</ul></div></details>'
    )


def table(headers, rows) -> str:
    thead = "".join(f"<th>{h}</th>" for h in headers)
    body = []
    for row in rows:
        tds = []
        for h, cell in zip(headers, row):
            tds.append(f'<td data-label="{html.escape(re.sub("<.*?>", "", h), quote=True)}">{cell}</td>')
        body.append("<tr>" + "".join(tds) + "</tr>")
    return (
        '<div class="art-tbl"><table class="art-table">'
        f"<thead><tr>{thead}</tr></thead><tbody>{''.join(body)}</tbody></table></div>"
    )


def faq_html(faqs) -> str:
    blocks = []
    for q, a in faqs:
        blocks.append(
            f'<details open=""><summary>Q：{html.escape(q)}</summary><p>A：{a}</p></details>'
        )
    return f'<div class="faq">{"".join(blocks)}</div>'


def related_html(links) -> str:
    # links: (href, title, date_visible)
    lis = []
    for href, title, date in links:
        if date:
            lis.append(f'<li><a href="{href}">{html.escape(title)}</a><small>{html.escape(date)}</small></li>')
        else:
            lis.append(f'<li><a href="{href}">{html.escape(title)}</a></li>')
    return (
        '<nav class="related" aria-label="相关文章"><h2>相关文章</h2>'
        f"<ul>{''.join(lis)}</ul>"
        '<p class="back-picks">'
        '<a href="/knowledge/chuhai-independent-site-server/">« 出海独立站怎么选服务器</a> · '
        '<a href="/knowledge/">知识库</a> · '
        '<a href="/#map">出海成本地图</a> · '
        '<a href="/tools/server-sizing/">配置下限</a> · '
        '<a href="/tools/network-lines/">线路对照</a>'
        "</p></nav>"
    )


def tweet_url(title: str, url: str) -> str:
    from urllib.parse import urlencode
    return "https://twitter.com/intent/tweet?" + urlencode({"text": title, "url": url})


def jsonld_scripts(art, text_body: str, word_count: int) -> str:
    url = art["url"]
    crumbs = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "知识库", "item": f"{SITE}/knowledge/"},
            {"@type": "ListItem", "position": 2, "name": art["title"], "item": url},
        ],
    }
    faq = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": q,
                "acceptedAnswer": {"@type": "Answer", "text": re.sub(r"<[^>]+>", "", a)},
            }
            for q, a in art["faqs"]
        ],
    }
    posting = {
        "@context": "https://schema.org",
        "@type": "BlogPosting",
        "headline": art["title"],
        "name": art["title"],
        "description": art["description"],
        "keywords": art.get("keywords", ""),
        "articleBody": text_body,
        "wordCount": word_count,
        "inLanguage": "zh-CN",
        "image": OG_IMAGE,
        "datePublished": DATE_ISO,
        "dateModified": DATE_ISO,
        "mainEntityOfPage": {"@type": "WebPage", "@id": url},
        "publisher": PUBLISHER,
    }
    parts = []
    for obj in (faq, crumbs, posting):
        parts.append(
            '<script type="application/ld+json">'
            + json.dumps(obj, ensure_ascii=False, separators=(",", ":"))
            + "</script>"
        )
    return "".join(parts)


def chips_html(chips) -> str:
    # chips: list of ("cat", text) or ("tag", href, text)
    bits = ['<div class="post-chips">']
    for chip in chips:
        if chip[0] == "cat":
            bits.append(f'<span class="cat-chip">{html.escape(chip[1])}</span>')
        else:
            bits.append(f'<a class="tag-chip" href="{chip[1]}">{chip[2]}</a>')
    bits.append("</div>")
    return "".join(bits)


def post_footer(art) -> str:
    tags = art.get("tags") or []
    tag_ul = ""
    if tags:
        items = "".join(f'<li><a href="{href}">{html.escape(name)}</a></li>' for href, name in tags)
        tag_ul = f'<ul class="post-tags">{items}</ul>'
    notice = ""
    if art.get("has_affiliate"):
        notice = (
            '<p class="aff-notice">本文含推广链接，详见 <a href="/disclosure/">推广披露</a>。'
            "通过链接购买我们可能获得佣金，不影响你的价格。</p>"
        )
    return f'<footer class="post-footer">{notice}{tag_ul}</footer>'


def count_zh_chars(text: str) -> int:
    t = re.sub(r"\s+", "", text)
    return len(t)


def plain_text(html_str: str) -> str:
    soup = BeautifulSoup(html_str, "html.parser")
    return re.sub(r"\n{3,}", "\n\n", soup.get_text("\n", strip=True)).strip()


def render(art: dict, header: str, footer: str, afterfooter: str) -> str:
    url = art["url"]
    body = art["body"]
    faq_txt = "\n".join(q + " " + re.sub(r"<[^>]+>", "", a) for q, a in art["faqs"])
    text_body = plain_text(body) + "\n" + faq_txt
    chars = count_zh_chars(text_body)
    minutes = max(1, round(chars / 400))
    title = art["title"]
    desc = art["description"]

    crumbs = (
        '<nav class="breadcrumbs" aria-label="Breadcrumb" role="navigation">'
        f'<a href="/">首页</a>{CHEVRON}'
        f'<a href="/knowledge/">知识库</a>{CHEVRON}'
        "</nav>"
    )
    actions = (
        '<div class="post-actions">'
        f'<button class="btn-ghost" type="button" data-copy-url="{html.escape(url, quote=True)}">复制链接</button>'
        f'<a class="btn-ghost" href="{html.escape(tweet_url(title, url), quote=True)}" target="_blank" rel="noopener">分享到 X</a>'
        "</div>"
        '<script defer="" src="/js/post-actions.js"></script>'
    )
    main = f"""<main class="main">
<article class="post-single knowledge-entry">
<header class="post-header post-band">
{crumbs}
{chips_html(art["chips"])}
<h1 class="post-title entry-hint-parent">{html.escape(title)}</h1>
<div class="post-description">{html.escape(desc)}</div>
<div class="post-meta"><span title="{DATE_ISO}">{DATE_VISIBLE}</span> · <span>约 {minutes} 分钟阅读</span></div>
{actions}
</header>
{toc_html(art["toc"])}
<div class="post-content md-content">
{body}
{heading("h2", "常见问题")}
{faq_html(art["faqs"])}
</div>
{related_html(art["related"])}
{post_footer(art)}
</article>
</main>"""

    ld = jsonld_scripts(art, text_body, chars)
    head = f"""<!doctype html>
<html lang="zh-CN" dir="auto" data-theme="auto"><head>
<meta charset="utf-8">
<meta http-equiv="X-UA-Compatible" content="IE=edge">
<meta name="viewport" content="width=device-width,initial-scale=1,shrink-to-fit=no">
<meta name="robots" content="index, follow">
<meta name="twitter:site" content="@chuhaiABC">
<title>{html.escape(title)} | fwqabc 出海ABC</title>
<meta name="keywords" content="{html.escape(art.get('keywords', ''))}">
<meta name="description" content="{html.escape(desc)}">
<meta name="author" content="">
<link rel="canonical" href="{url}">
<link crossorigin="anonymous" href="{STYLESHEET}" integrity="{INTEGRITY}" rel="preload stylesheet" as="style">
<link rel="icon" href="{SITE}/favicon.ico">
<link rel="icon" type="image/png" sizes="16x16" href="{SITE}/favicon-32x32.png">
<link rel="icon" type="image/png" sizes="32x32" href="{SITE}/favicon-32x32.png">
<link rel="apple-touch-icon" href="{SITE}/apple-touch-icon.png">
<link rel="manifest" href="{SITE}/site.webmanifest">
<link rel="mask-icon" href="{SITE}/android-chrome-512x512.png">
<meta name="theme-color" content="#2f394c">
<meta name="msapplication-TileColor" content="#2e2e33">
<link rel="alternate" hreflang="zh-CN" href="{url}">
<link rel="alternate" hreflang="x-default" href="{url}">
{NOSCRIPT}
<script>{THEME_JS}</script>
<link rel="preload" href="/fonts/inter-latin-400-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/fonts/inter-latin-600-normal.woff2" as="font" type="font/woff2" crossorigin>
<meta property="og:url" content="{url}">
<meta property="og:site_name" content="fwqabc 出海ABC">
<meta property="og:title" content="{html.escape(title, quote=True)}">
<meta property="og:description" content="{html.escape(desc, quote=True)}">
<meta property="og:locale" content="zh_CN">
<meta property="og:type" content="article">
<meta property="article:section" content="knowledge">
<meta property="article:published_time" content="{DATE_ISO}">
<meta property="article:modified_time" content="{DATE_ISO}">
<meta property="og:image" content="{OG_IMAGE}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="{OG_IMAGE}">
<meta name="twitter:title" content="{html.escape(title, quote=True)}">
<meta name="twitter:description" content="{html.escape(desc, quote=True)}">
{ld}
<link rel="stylesheet" href="/assets/css/ux-20261112.css">
</head>"""
    page = (
        head
        + f'<body id="top">{header}{main}{footer}{afterfooter}</body></html>\n'
    )
    art["_chars"] = chars
    art["_minutes"] = minutes
    return page


# Article bodies are filled after this skeleton when the file is extended.
ARTICLES: list[dict] = []

# ---------------------------------------------------------------------------
# Article 1: Hub
# ---------------------------------------------------------------------------

HUB_BODY = f"""
<blockquote>核对日期：{CHECK_DATE}。这是给中国中小企业、个体户、源头工厂做海外独立站时的选型顺序，不是优惠汇总。文中的线路含义引用本站已发布的线路页；自治系统名称在 {CHECK_DATE} 对照过 IPinfo 与 PeeringDB 公开登记；付款周期的例子来自搬瓦工官网公开目录（同日核对）。没有自购新的性能测试，本文不下新的速度或丢包结论。</blockquote>

{heading("h2", "先说结论")}
<p>先看访客主要在哪，再决定要不要精品线路，然后选靠近访客的机房，最后用同一方案核对月付、年付和续费条件。不要先被套餐名或活动价带着走。</p>
<p>可以按下面五步走：</p>
<ol>
<li>分清访客主要在中国大陆，还是在目标市场（美国、欧洲、东南亚等），两边都有也要先写清楚，不能混成“外贸站所以一定要 CN2”。</li>
<li>只有大陆访客占比高、又在意晚高峰稳定性，或国内团队要经常从大陆访问后台时，再进入精品线路的判断；访客主要在海外时，普通国际线路往往就够。详见 <a href="/knowledge/domestic-visitors-cn2/">国内访客为主，独立站该不该上 CN2</a> 和 <a href="/knowledge/premium-line-when/">独立站要不要上精品线路</a>。</li>
<li>机房先靠近主要访客，而不是靠近你所在的城市。配置先看本站 <a href="/tools/server-sizing/">配置下限估算</a>，不要一上来就买很高的套餐。</li>
<li>比价时看同一方案的月付和年付差额，并核对续费是不是同一档标价，而不是只看首期。见 <a href="/knowledge/monthly-vs-yearly-vps/">年付和月付差多少，续费会不会更贵</a>。</li>
<li>上线前后，用目标市场的访问路径做验收。本站目前公开发布的境外体检是 <a href="/cases/rfkey-overseas-check-2026-11/">RF-KEY射频元器件商城海外访问实测</a>；没有自购实测，就不会在这里补充性能数字。</li>
</ol>
<p>服务器只是出海成本里的一笔。先立主体、再开门面、把货送出去、把钱收回来，地图在 <a href="/#map">首页出海成本地图</a>。这一组文章只展开“开门面”里的服务器和网络。</p>

{heading("h2", "先问访客在哪")}
<p>独立站的服务器，首先是给访客打开的，其次才是给你自己维护的。把访客写成“国内外都有，所以全都要最好”，后面的线路和机房都会失去判断标准。</p>
{table(
    ["主要访客", "先看什么", "再读哪一篇"],
    [
        ["主要在中国大陆，例如国内询盘、国内分公司或需要大陆打开后台", "要不要 CN2 GIA，以及联通、移动访客要不要对照 9929 / CMIN2", '<a href="/knowledge/domestic-visitors-cn2/">国内访客为主，该不该上 CN2</a>'],
        ["主要在海外目标市场", "机房靠近访客，普通国际线路通常即可；先解决页面体积、HTTPS 和多语言，再谈换线路", '<a href="/knowledge/overseas-visitors-server/">访客主要在海外时怎么选</a>'],
        ["大陆和海外都有，且都要经常访问", "按占比和高峰时段拆开看，可能是一台靠近海外访客的机器，再另作大陆访问或后台方案；不要默认买一条最贵的线路就两端都合适", '<a href="/knowledge/premium-line-when/">要不要上精品线路</a>'],
        ["还不确定", "先看统计、询盘来源和你真正要服务的市场；不确定时不要先给线路下结论", '<a href="/tools/network-lines/">线路对照工具</a>'],
    ],
)}
<p>本站 <a href="/tools/network-lines/">线路对照</a> 的规则只来自三篇线路页，不补充延迟或丢包数字：大陆电信访客去读 CN2 GIA，联通去读 9929，移动去读 CMIN2；主要不在中国大陆时，这三篇谈的是大陆回程，不替你选线路。</p>

{heading("h2", "配置先看下限，再去比价")}
<p>本站 <a href="/tools/server-sizing/">配置下限估算</a> 把常见独立站写成这样的起步假设（不是实测评分，也不是“越多越好”）：</p>
{table(
    ["工作负载", "起步下限", "工具里的上调假设"],
    [
        ["静态展示站", "1 vCPU / 1024 MB", "月访问量大于 10 万次时，内存改为 2048 MB"],
        ["CMS（一个站点，带数据库，例如常见的独立站建站程序）", "1 vCPU / 2048 MB", "月访问量大于 5 万次时，改为 2 vCPU / 4096 MB"],
        ["小型 JSON API", "2 vCPU / 2048 MB", "按峰值再上调；超过工具上限时不估算多台机器"],
    ],
)}
<p>工具写明：留空表示“不知道”，不是 0；超过 1000 万次/月或 1000 次/秒时，这张表不给配置。算出下限后，再去 <a href="/servers/">服务器比价</a> 里筛内存和 vCPU 都不低于该下限的套餐。未知配置会被排除，因为未知不等于达标。</p>
<p><a href="/cases/rfkey-overseas-check-2026-11/">RF-KEY射频元器件商城</a> 的公开结论也和这个顺序一致：2026-11-02，本站用自购的搬瓦工洛杉矶普通线路月付机器（4 核 4 GB，$19.99/月，核对价见该文）从美国加州访问公开页面，页面可以打开；完整加载偏慢的主要原因是首页图片体积，报告写明单靠升级服务器解决不了这一项。业务和访问量变大、或大陆访问明显偏慢时，再考虑更高配置或大陆优化线路。</p>

<figure class="shot">
<img src="/img/cases/rfkey-2026-11/cover.webp" alt="RF-KEY射频元器件商城中文首页，从美国加州 VPS 浏览器冷加载时的截图" width="800" height="500" loading="lazy" decoding="async">
<figcaption>已发布案例截图：RF-KEY射频元器件商城中文首页，从美国加州 VPS 冷加载。来源：<a href="/cases/rfkey-overseas-check-2026-11/">海外访问实测</a>（测试时间 2026-11-02，北京时间），不是为本文新截的图。</figcaption>
</figure>

{heading("h2", "线路、地区和付款周期怎么接起来")}
<ul>
<li>线路：CN2 GIA、9929、CMIN2 各适合哪类大陆访客，见 <a href="/knowledge/premium-line-when/">独立站要不要上精品线路</a>。详细定义仍在 <a href="/routes/cn2-gia/">CN2 GIA</a>、<a href="/routes/9929/">9929</a>、<a href="/routes/cmin2/">CMIN2</a> 原线路页。</li>
<li>地区：访客在美国就先看美国机房，在东南亚就先看新加坡等靠近访客的节点。本站比价页按地区列出已收录套餐，例如 <a href="/servers/regions/united-states/">美国</a>、<a href="/servers/regions/singapore/">新加坡</a>、<a href="/servers/regions/japan/">日本</a>、<a href="/servers/regions/hong-kong/">中国香港</a>、<a href="/servers/regions/germany/">德国</a>、<a href="/servers/regions/united-kingdom/">英国</a>。</li>
<li>付款周期：年付常常比把月付买满 12 个月更省，但要核对是不是同一档标价、退款是否包含续费、首期优惠会不会在续费时消失。例子和算法见 <a href="/knowledge/monthly-vs-yearly-vps/">年付和月付</a>。</li>
</ul>
<p>想先用免费额度做试验，可以读 <a href="/free/free-cloud-credits-2026/">免费服务器与新用户赠金汇总 2026</a> 和 <a href="/free/oracle-cloud-always-free-guide-2026/">Oracle Cloud Always Free 申请指南</a>，并以这两篇自己的核对日期为准；免费机有额度、区域和回收规则，不能直接当成正式独立站的默认方案。</p>

{heading("h2", "使用时要注意什么")}
<ul>
<li>商家宣传里的线路名称，要对照自治系统登记和结算页写明的内容，不要把广告语当成已经实测。</li>
<li>本站线路页写明：表现因机房、时段和所在地区而异，实测完成前不给速度结论。本文遵守同一条。</li>
<li>活动价、库存和优惠码会变。本站优惠文章各有自己的核对日期，例如 <a href="/deals/bandwagonhost-coupon-2026/">搬瓦工方案对比</a> 的目录核对应以该文页面为准；本文不把任何活动写成今天仍在进行。</li>
<li>含推广的跳转会标明。结论按适不适合排，不按佣金排。</li>
</ul>
""".strip()

HUB_FAQS = [
    ("独立站一定要买海外服务器吗？",
     "要看访客和业务发生在哪。站点主要服务海外客户，机器通常放在靠近访客的地区，避免只把服务器放在自己身边。若访客和操作都在中国大陆，海外机器不是自动正确的答案。主体、域名和收款还要单独看，地图在首页出海成本地图。"),
    ("访客在国内和海外都有，买一条精品线路能不能两端都顾到？",
     "不一定。精品线路讨论的主要是中国大陆回程，不自动等于海外目标市场也会更快。两边都有访问需求时，按占比和高峰拆开看，不要默认最贵的线路就两端都合适。本站没有为“一条线路覆盖全球”做过实测，因此不下这个结论。"),
    ("先买便宜的月付，以后再升级，可以吗？",
     "可以，尤其是站点还在试验内容和市场的时候。先用配置下限估算起步，月付方便停掉或改方案。等访问来源稳定，再决定要不要换地区、换线路或改年付。RF-KEY射频元器件商城那次境外体检也说明：页面资源过大时，先减重，而不是先升级机器。"),
    ("免费云服务器能不能先用来建独立站？",
     "可以用来熟悉流程或做短时试验，但要把额度、可用区、闲置回收和验证条件看完，并以本站免费机指南各自的核对日期和官方页面为准。正式对外卖货的独立站，还要另外核对地域、备份、邮件发送和售后时段的运维条件，不能把免费机直接写成默认方案。"),
    ("这篇和比价页、优惠汇总是什么关系？",
     "这篇只给判断顺序。算出配置下限、选定地区和线路类型之后，再去服务器比价筛选套餐；核对某一家的标价或活动时，再打开对应的商家或优惠文章，并看该文的核对日期。不要反过来先从活动列表倒推需求。"),
]

# ---------------------------------------------------------------------------
# Article 2: domestic CN2
# ---------------------------------------------------------------------------

DOM_BODY = f"""
<blockquote>核对日期：{CHECK_DATE}。线路含义以本站 <a href="/routes/cn2-gia/">CN2 GIA 线路页</a> 为准。AS4809 的公开登记在同日对照了 <a href="https://ipinfo.io/AS4809" rel="noopener noreferrer" target="_blank">IPinfo AS4809</a> 和 <a href="https://www.peeringdb.com/net/7941" rel="noopener noreferrer" target="_blank">PeeringDB</a>（API 查询 <a href="https://www.peeringdb.com/api/net?asn=4809" rel="noopener noreferrer" target="_blank">asn=4809</a>）。没有自购针对本文的速度实测，因此不写延迟、丢包或“会更快多少”。</blockquote>

{heading("h2", "先说结论")}
<p>独立站的主要访客、询盘对象或需要经常打开的后台在中国大陆，并且你在意晚高峰是否稳定，本站线路页才把 CN2 GIA 写成更相关的选项。访客主要在海外目标市场时，不必因为“这是外贸独立站”就先上 CN2；那种情况请读 <a href="/knowledge/overseas-visitors-server/">访客主要在海外时，服务器怎么选</a>。</p>
<p>CN2 GIA 通常比普通国际线路更贵。值不值得买，先看访客是不是在大陆，而不是看套餐名好不好听。</p>

{heading("h2", "CN2 GIA 在本站和公开登记里指什么")}
<p>本站线路页的写法是：CN2 是中国电信的下一代承载网，自治系统号 AS4809；商家说的 CN2 GIA，一般指去程和回程都走 CN2 的高等级国际线路。</p>
<p>{CHECK_DATE} 的公开登记与这个说法相符，但不等于本站做了线路实测：</p>
<ul>
<li>IPinfo 页面标题为 “AS4809 China Telecom Next Generation Carrier Network”，页面中可见 WHOIS 网络名 CHINATELECOM-CORE-WAN-CN2、描述 China Telecom Next Generation Carrier Network。</li>
<li>PeeringDB 将 AS4809 登记为 “China Telecom / CN2”。</li>
</ul>
<p>判断框架的短页是 <a href="/knowledge/cn2-gia/">CN2 GIA：先看适不适合</a>，完整说明仍在 <a href="/routes/cn2-gia/">原线路页</a>。本文不另写一套定义。</p>

{heading("h2", "该不该上：先对照访客，而不是对照身份")}
{table(
    ["你的情况", "本站已经写明的判断", "还不能从本文得出的结论"],
    [
        ["访客主要在国内，外贸或企业站要给大陆用户打开，或国内团队需要较稳定的后台访问", "线路页把这类用途写成 CN2 GIA 的适合场景", "不会因此得到某个机房、某个时段的延迟数字"],
        ["访客主要在海外，只是公司在国内、偶尔要从国内登后台", "线路页写明：访客主要在海外时，普通国际线路或 BGP 往往就够，价格也更低", "国内登后台会慢多少，没有实测，不能用一句“必须上 CN2”代替"],
        ["大陆访客里电信用户占比高，并且在意晚高峰", "更应先读 CN2 GIA；联通、移动要分别对照 9929 和 CMIN2", "不能把 CN2 GIA 写成对三网都同样适用"],
        ["还不知道访客来自哪家运营商", '先看访问统计和询盘来源，再进入 <a href="/tools/network-lines/">线路对照</a>', "不确定时不猜测该买哪一条"],
    ],
)}
<p>联通、移动以及“要不要上精品线路”的对照，见 <a href="/knowledge/premium-line-when/">独立站要不要上精品线路</a>。工具页也写明：本站套餐目录里有标明 CN2 GIA 的方案；目前没有把套餐标成 AS9929 或 CMIN2。没有标出来，不等于市场上不存在，只说明目录还没有这样归类，不能当成已经核实的库存。</p>

{heading("h2", "怎么确认商家说的是 CN2 GIA")}
<ol>
<li>看结算页或官方说明是否写明 CN2 GIA，而不是只写“CN2”“优化回程”“大陆加速”这类较宽的词。</li>
<li>对照公开的 AS4809 登记，以及商家是否同时给出去程和回程说明。本站线路页提醒：不要把宣传语当成实测。</li>
<li>同一商家的不同机房也可能不同。例如本站在搬瓦工方案里区分了普通线路、CN2 GIA-E、亚洲 CN2 GIA 和洛杉矶 E-Commerce SLA，不能互相替代。具体标价以 <a href="/deals/bandwagonhost-coupon-2026/">搬瓦工 2026 优惠码与方案对比</a> 文内的核对日期和官网结算页为准，本文不重报一遍活动是否仍在进行。</li>
<li>表现因机房、时段和所在地区而异。本站线路页写明实测完成前不给速度结论，本文同样不补数字。</li>
</ol>

{heading("h2", "使用时要注意什么")}
<ul>
<li>CN2 和 CN2 GIA 不是自动等同的说法。只看到“CN2”两个字，还不能写成已经买到去程和回程都走 AS4809 的方案。</li>
<li>更贵不等于已经验证过适合你的访客。先用访客来源判断，再决定要不要看这类方案。</li>
<li>如果大陆和海外都要服务，一台 CN2 机器也不自动解决海外目标市场的访问；海外侧仍要按 <a href="/knowledge/overseas-visitors-server/">海外访客怎么选</a> 来看地区和页面本身。</li>
<li>独立站常见的慢，不一定来自线路。RF-KEY射频元器件商城的境外体检里，公开页面可以打开，完整加载偏慢的主因是图片体积。那种问题要先处理页面，而不是先换 CN2。</li>
</ul>
""".strip()

DOM_FAQS = [
    ("外贸独立站是不是都该上 CN2 GIA？",
     "不是。关键是访客在哪。本站线路页把 CN2 GIA 写成更适合访客主要在国内、在意晚高峰的网站；访客主要在海外时，普通国际线路或 BGP 往往就够，价格也更低。"),
    ("商家写了 CN2，是不是就是 CN2 GIA？",
     "不一定。本站的用法是：CN2 GIA 一般指去程和回程都走中国电信 CN2（AS4809）。只写 CN2、优化线路或大陆加速，还需要对照结算页和公开登记，不能直接当成 GIA。"),
    ("上了 CN2 GIA，联通和移动也会一样稳吗？",
     "本站没有给出这个结论。联通访客应另外对照 9929，移动访客对照 CMIN2。不能把“对电信更相关”理解成对三网都同样适用，也没有三网实测数字可以引用。"),
    ("我只是偶尔从国内登后台，要不要为此买 CN2？",
     "要看频率和你能否接受偶发不稳定。线路页把“需要稳定访问的后台”列为适合场景之一，但本文没有实测国内登海外机器的耗时，不能写成“偶尔登录也必须买”。访客主力在海外时，仍应优先按海外访客来选机房。"),
    ("怎样确认自己买到的是这条线路？",
     "先看官方结算页是否写明 CN2 GIA，再对照 AS4809 的公开登记。本站在自购实测完成前不给速度结论，也不把宣传截图当成路径证明。"),
]

# ---------------------------------------------------------------------------
# Article 3: overseas visitors
# ---------------------------------------------------------------------------

OVS_BODY = f"""
<blockquote>核对日期：{CHECK_DATE}。地区和线路的判断顺序来自本站线路页、线路对照工具和配置下限工具。案例结论只引用已发布的 <a href="/cases/rfkey-overseas-check-2026-11/">RF-KEY射频元器件商城海外访问实测</a>（测试时间 2026-11-02，北京时间），不补充未公开发表的地址、源站 IP、后台或商品价格信息。本文没有新的自购实测，也不把那一次加州测试点的结果写成全球都适用。</blockquote>

{heading("h2", "先说结论")}
<p>独立站的主要访客在海外目标市场时，先把机器放在靠近访客的地区，再用本站配置下限估算起步配置；普通国际线路通常即可，不必只为“在国内打开更顺”而先上精品线路。</p>
<p>页面打得开、打得快，往往先取决于图片、跳转、缓存和内容是否面向目标市场，而不是先换一条大陆回程线路。RF-KEY射频元器件商城那次境外体检的结论，就是这个顺序的一个已发布例子。</p>

{heading("h2", "先靠近访客，再谈线路")}
<p>本站 <a href="/routes/cn2-gia/">CN2 GIA 线路页</a> 写明：访客主要在海外时，普通国际线路或 BGP 往往就够，价格也更低。<a href="/tools/network-lines/">线路对照</a> 也写明：主要不在中国大陆，或大陆访客但人在海外时，那三篇谈的是大陆回程，不替你选线路。</p>
{table(
    ["目标访客主要在", "机房可以先看", "线路上先记住什么"],
    [
        ["美国或北美", '<a href="/servers/regions/united-states/">美国</a>、<a href="/servers/regions/canada/">加拿大</a> 等靠近访客的节点', "先看普通国际线路是否足够；CN2 / 9929 / CMIN2 不是这一步的默认选项"],
        ["西欧、英国", '<a href="/servers/regions/germany/">德国</a>、<a href="/servers/regions/united-kingdom/">英国</a>、<a href="/servers/regions/netherlands/">荷兰</a>、<a href="/servers/regions/france/">法国</a> 等', "同样先按地区选，再看配置和流量是否够用"],
        ["东南亚", '<a href="/servers/regions/singapore/">新加坡</a> 等靠近访客的节点；是否还要看日本或中国香港，要另核延迟和内容合规，本文不给未实测的快慢结论', "亚洲机房里的 CN2 GIA 方案主要仍是面向大陆回程的讨论，不能直接写成“新加坡访客也必须买 CN2”"],
        ["日本、韩国、澳大利亚等", '先看对应地区的已收录套餐，例如 <a href="/servers/regions/japan/">日本</a>、<a href="/servers/regions/south-korea/">韩国</a>、<a href="/servers/regions/australia/">澳大利亚</a>', "以靠近访客为准，不要因为国内访问习惯倒推机房"],
        ["还在试探多个市场", "先选当前询盘最多的地区，用月付起步，避免一上来年付锁死地区", '见 <a href="/knowledge/monthly-vs-yearly-vps/">年付和月付</a>'],
    ],
)}
<p>比价目录按地区做了归类，选地区时以目录和结算页为准。本文不把某个城市写成对整个大洲都合适。</p>

{heading("h2", "配置和页面：先够用，再升级")}
<p>一个带数据库的独立站，本站 <a href="/tools/server-sizing/">配置下限估算</a> 的起步假设是 1 vCPU / 2048 MB；月访问量大于 5 万次时，工具才把假设上调到 2 vCPU / 4096 MB。这是下限估算，不是评分。</p>
<p>2026-11-02，本站用自购的搬瓦工洛杉矶 USCA_2 月付方案（4 核 / 4 GB / 80 GB，月流量 3 TB，目录价 $19.99/月）在美国加州直接访问 RF-KEY射频元器件商城的公开页面。该文已经写明的结论包括：</p>
<ul>
<li>当时 5 个公开页面在该测试点可以打开并显示实际内容，15 次 HTTPS 传输返回 200。</li>
<li>中文首页桌面冷加载的 LCP 中位数是 2.16 秒，热加载 1.00 秒；完整加载中位数约 12 秒，主要拖尾来自首页图片体积，不是先升级服务器就能消除。</li>
<li>建议先给轮播图和产品图减重，再处理 HTTP 未跳转到 HTTPS、英文页金额和图片文字等问题；业务和访问量变大，或大陆访问明显偏慢时，再考虑更高配置或大陆优化线路。</li>
<li>报告只代表指定美国加州机房测试机和那次时段，不代表全球用户体验或完整交易流程已经验收通过。</li>
</ul>
<p>引用这些结论，是为了说明：访客在海外时，先检查页面和站点配置，再决定要不要换线路或升配。完整数据和截图在原案例页。</p>

<figure class="shot">
<img src="/img/cases/rfkey-2026-11/home-zh-desktop.webp" alt="RF-KEY射频元器件商城中文首页桌面冷加载境外实测截图" width="1440" height="1000" loading="lazy" decoding="async">
<figcaption>已发布案例截图：RF-KEY射频元器件商城中文首页，桌面冷加载（美国加州 VPS，2026-11-02）。来源：<a href="/cases/rfkey-overseas-check-2026-11/">海外访问实测</a>，不是为本文新截的图。</figcaption>
</figure>

{heading("h2", "国内团队要登后台时怎么处理")}
<p>很多源头工厂的独立站，访客在海外，但改商品、回邮件、看订单的人在国内。这是两件需求，不要合并成“所以必须买精品线路”。</p>
<ul>
<li>访客路径：仍按目标市场选机房和普通线路，优先保证客户打开商品和结账页面。</li>
<li>后台路径：如果国内登录明显不稳，再单独评估是否需要精品线路、是否把后台与前台分开、是否只用必要时段访问。本站没有为“国内登海外后台”发表过专门实测，因此这里不写会慢多少，也不把 CN2 写成唯一做法。</li>
<li>若大陆客户也会经常访问前台，转到 <a href="/knowledge/domestic-visitors-cn2/">国内访客为主，该不该上 CN2</a> 和 <a href="/knowledge/premium-line-when/">要不要上精品线路</a>，按占比判断。</li>
</ul>

{heading("h2", "使用时要注意什么")}
<ul>
<li>不要用你在国内浏览器里的手感，代替目标市场的验收。</li>
<li>不要把一次测试点的结果推广到所有国家和所有运营商。RF-KEY 案例把局限写在了方法一节，引用时一并遵守。</li>
<li>HTTPS 跳转、多语言校对、图片体积这些问题，换机房或换线路通常解决不了。</li>
<li>需要看付款周期或续费时，用 <a href="/knowledge/monthly-vs-yearly-vps/">年付和月付</a> 的核对方法，不要只看首期活动价。</li>
</ul>
""".strip()

OVS_FAQS = [
    ("访客主要在海外，还要不要买 CN2 GIA？",
     "不是默认要买。本站线路页写明：访客主要在海外时，普通国际线路或 BGP 往往就够，价格也更低。只有大陆访客或国内后台访问也成为明确需求时，再进入精品线路的判断。"),
    ("机房是不是离我越近越好？",
     "不是。独立站首先要靠近访客。你在国内维护，并不等于机器应该放在离你最近的地方。国内维护不便是单独的问题，不能倒过来决定客户的访问路径。"),
    ("一台普通线路的 4 核 4 GB 机器够不够做独立站？",
     "要看站点类型和访问量。配置下限工具给带数据库的单个 CMS 站点的起步假设是 1 vCPU / 2048 MB。RF-KEY射频元器件商城那次体检表明，4 核 4 GB 的月付机器足够完成公开页面访问检查，但那是单次、单点的结论，不能写成所有独立站的配置标准。"),
    ("海外访问慢，是不是先升级服务器？",
     "先看慢在什么地方。RF-KEY 案例里，公开页面可以打开，完整加载偏慢的主因是首页图片体积，报告写明单靠升级服务器解决不了。应先处理图片、缓存、跳转和内容，再考虑升配或换线路。"),
    ("可以从国内直接判断海外客户的打开速度吗？",
     "不能把国内访问手感当成目标市场的结果。本站已发布的境外体检，是在自购的美国加州测试机上直接访问公开页面，并且写明了方法和局限。没有同类实测时，本文不会编造其他地区的速度。"),
]

# ---------------------------------------------------------------------------
# Article 4: premium lines
# ---------------------------------------------------------------------------

PREM_BODY = f"""
<blockquote>核对日期：{CHECK_DATE}。三条线路的适用说法以本站 <a href="/routes/cn2-gia/">CN2 GIA</a>、<a href="/routes/9929/">9929</a>、<a href="/routes/cmin2/">CMIN2</a> 线路页和 <a href="/tools/network-lines/">线路对照</a> 为准。自治系统名称在同日对照了 IPinfo 与 PeeringDB 公开登记。搬瓦工 E-Commerce+SLA 产品说明中的线路表述，来自官网公开目录 <a href="https://bandwagonhost.com/order/catalog.json" rel="noopener noreferrer" target="_blank">bandwagonhost.com/order/catalog.json</a> 的同日快照。没有自购线路实测，本文不写延迟、丢包或“哪条更快”。</blockquote>

{heading("h2", "先说结论")}
<p>精品线路不是独立站的默认配置。先确认有足够多的中国大陆访客，或国内访问稳定性已经成为明确需求，再按访客所用的网络分别看：电信对照 CN2 GIA（AS4809），联通对照 9929（AS9929），移动对照 CMIN2（常见 AS58807）。</p>
<p>访客主要在海外时，先读 <a href="/knowledge/overseas-visitors-server/">访客主要在海外时怎么选</a>，不必为了“做外贸”先上这三条线。本站也没有实测证明“买一条最贵的线，三网和海外就都会更快”。</p>

{heading("h2", "三条线分别是什么，适合什么时候看")}
{table(
    ["线路", "公开登记（2026-11-12 核对）", "本站线路页已经写明的适合场景", "还不能从本文得出的结论"],
    [
        ['CN2 GIA<br>常见 AS4809',
         'IPinfo：China Telecom Next Generation Carrier Network（CHINATELECOM-CORE-WAN-CN2）；PeeringDB：China Telecom / CN2。来源：<a href="https://ipinfo.io/AS4809" rel="noopener noreferrer" target="_blank">ipinfo.io/AS4809</a>、<a href="https://www.peeringdb.com/net/7941" rel="noopener noreferrer" target="_blank">PeeringDB net/7941</a>',
         "一般指去程和回程都走 CN2 的高等级国际线路，通常比普通国际线路更贵；适合访客主要在国内、在意晚高峰的网站，以及需要较稳定访问的后台",
         "不会给出具体机房的延迟，也不能写成对联通、移动同样适用"],
        ['9929<br>AS9929',
         'IPinfo 与 PeeringDB 均登记为 CHINA UNICOM Industrial Internet Backbone / China Unicom Industrial Internet Backbone。来源：<a href="https://ipinfo.io/AS9929" rel="noopener noreferrer" target="_blank">ipinfo.io/AS9929</a>、<a href="https://www.peeringdb.com/net/19957" rel="noopener noreferrer" target="_blank">PeeringDB net/19957</a>',
         "商家标注 9929 的方案，通常对联通用户的晚高峰更友好；想让三网尽量均衡时，可以和 CN2 GIA、CMIN2 一起看",
         "不能理解成对所有运营商都同样好；本站没有其他运营商的实测结论"],
        ['CMIN2<br>常见 AS58807',
         'IPinfo：China Mobile International Limited；PeeringDB：China Mobile International - NII，又称 CMIN2。来源：<a href="https://ipinfo.io/AS58807" rel="noopener noreferrer" target="_blank">ipinfo.io/AS58807</a>、<a href="https://www.peeringdb.com/net/22581" rel="noopener noreferrer" target="_blank">PeeringDB net/22581</a>',
         "商家标注 CMIN2 的方案，通常面向移动用户优化回程，适合访客以移动用户为主的网站",
         "页面没有把 CMIN2 写成对电信或联通同样更优，也没有速度实测"],
    ],
)}
<p>短判断页见 <a href="/knowledge/cn2-gia/">CN2 GIA：先看适不适合</a>、<a href="/knowledge/as9929/">AS9929：先看适不适合</a>、<a href="/knowledge/cmin2/">CMIN2：先看适不适合</a>。详细正文仍在原线路页，本文不复制那段文字。</p>

{heading("h2", "什么时候值得看，什么时候不必先看")}
{table(
    ["情况", "建议", "依据"],
    [
        ["大陆电信访客为主，或国内打开前台、后台的稳定性很重要", "先读 CN2 GIA", '线路页与 <a href="/knowledge/domestic-visitors-cn2/">该不该上 CN2</a>'],
        ["大陆联通访客为主", "先读 9929，不要只看 CN2 的宣传", "线路页；线路对照工具"],
        ["大陆移动访客为主", "先读 CMIN2", "线路页；线路对照工具"],
        ["希望三网都尽量照顾到", "把三条说明放在一起看，核对商家是否分别写明，而不是只买一个名称", "9929 线路页提到可与 CN2 GIA、CMIN2 组合选择；本文没有“一条线覆盖三网”的实测"],
        ["访客主要在海外目标市场", "不必先上精品线路", "CN2 GIA 线路页：普通国际线路或 BGP 往往就够"],
        ["还不知道访客用哪家运营商", "先看统计，不猜测", "线路对照工具：不确定时不猜测，三篇都给出链接"],
    ],
)}

{heading("h2", "目录里能核对到什么，核对不到什么")}
<p><a href="/tools/network-lines/">线路对照</a> 写明：目录里有标明 CN2 GIA 的套餐；目前没有把套餐标成 AS9929；目前没有把套餐标成 CMIN2。这只说明本站目录的标注范围，不是市场上有没有这类产品的最终调查。</p>
<p>本站线路页在讨论收录方案时写过：搬瓦工洛杉矶 E-Commerce SLA 系列，官方把其联通线路标为 Premium（AS10099，即常说的 9929/10099 精品网），并标注移动 CMIN2 优化。{CHECK_DATE} 再核对该公司公开目录里 “E-Commerce+SLA” 产品说明，可见其将 USA-China routing 写为：China Telecom CN2 GIA/CTGNet AS4809/AS23764、China Unicom Premium AS10099、China Mobile CMIN2 AS58807。这是商家官方产品说明，不是本站的路径实测。</p>
<p>需要单独说清的是：AS9929 和 AS10099 在公开登记里是两个网络。同日 IPinfo 与 PeeringDB 将 AS10099 登记为 China Unicom Global（<a href="https://ipinfo.io/AS10099" rel="noopener noreferrer" target="_blank">ipinfo.io/AS10099</a>、<a href="https://www.peeringdb.com/net/7268" rel="noopener noreferrer" target="_blank">PeeringDB net/7268</a>）。本站线路页把商家标注的 Unicom Premium AS10099 写成常说的 9929/10099 精品网，但这不等于两个自治系统已经在实测里被证明是同一条路径。没有自购实测前，下单时仍以商家说明和你自己的核对为准，不要把两个 AS 号直接写成一回事。</p>
<p>具体套餐价格、机房和是否有优惠，见 <a href="/deals/bandwagonhost-coupon-2026/">搬瓦工 2026 优惠码与方案对比</a>，并以该文自己的核对日期和官网结算页为准。本文不把任何活动写成当天仍有效。</p>

<figure class="shot">
<img src="/img/promos/bandwagonhost-cn2-gia-e.webp" alt="搬瓦工官网 CN2 GIA-E 方案购物车页面截图" width="640" height="400" loading="lazy" decoding="async">
<figcaption>已发布的官网购物车截图，截于 2026-11-01，用于说明要在官方结算页核对线路和价格。来源：<a href="/deals/bandwagonhost-coupon-2026/">搬瓦工方案对比</a>。本文没有重截此图，价格以官网当前结算页为准。</figcaption>
</figure>

{heading("h2", "使用时要注意什么")}
<ul>
<li>先有大陆访客或国内访问需求，再谈精品线路；顺序不要反过来。</li>
<li>宣传语、参数表和实际路径可能不是同一件事。确认时看结算页写明的线路名称，并对照公开 AS 登记。</li>
<li>线路页均写明：表现因机房和地区而异，本站实测完成前不给结论。</li>
<li>页面慢不一定是线路问题。独立站要同时检查图片、跳转和内容，参见 <a href="/cases/rfkey-overseas-check-2026-11/">RF-KEY射频元器件商城海外访问实测</a>。</li>
</ul>
""".strip()

PREM_FAQS = [
    ("独立站是不是都要上精品线路？",
     "不是。先看访客是不是主要在中国大陆，以及你是否在意大陆访问的稳定性。访客主要在海外时，本站线路页写明普通国际线路或 BGP 往往就够。"),
    ("CN2 GIA、9929、CMIN2 怎么分？",
     "按大陆访客常用的网络来分：电信对照 CN2 GIA（AS4809），联通对照 9929（AS9929），移动对照 CMIN2（常见 AS58807）。不能把其中一条写成对三网都同样适用。公开登记名称已在 2026-11-12 核对，速度如何仍要等实测，本文不给数字。"),
    ("买了标注三网优化的方案，是不是就不用再分运营商了？",
     "商家产品说明可以把多条线路写在一起，例如搬瓦工公开目录里的 E-Commerce+SLA 说明同时列出了 CN2 GIA、Unicom Premium 和 CMIN2。这是官方文字，不是本站实测。本站目录目前也没有把套餐标成 AS9929 或 CMIN2。是否符合你的访客结构，仍要对照结算页，并不能从宣传推出三网都已经验证。"),
    ("9929 和 AS10099 是不是同一条线？",
     "公开登记里这是两个自治系统：AS9929 为联通工业互联网骨干网，AS10099 为 China Unicom Global。本站线路页在介绍搬瓦工方案时，把官方标注的 Unicom Premium AS10099 写成常说的 9929/10099 精品网。没有路径实测前，不应把两个 AS 号直接等同。"),
    ("本站比价目录里为什么看不到 9929、CMIN2 套餐？",
     "线路对照工具写明：目录里有标明 CN2 GIA 的套餐，目前没有把套餐标成 AS9929 或 CMIN2。这是目录标注范围，不是对全市场库存的结论。"),
]

# ---------------------------------------------------------------------------
# Article 5: monthly vs yearly
# ---------------------------------------------------------------------------

MON_BODY = f"""
<blockquote>核对日期：{CHECK_DATE}。下面的搬瓦工标价来自官网公开产品目录 <a href="https://bandwagonhost.com/order/catalog.json" rel="noopener noreferrer" target="_blank">bandwagonhost.com/order/catalog.json</a>（官网首页提供的 “Plans, prices &amp; availability (JSON)” 链接），价格单位是整个付款周期的美元美分，不是折算月费。条款来自同日取得的 <a href="https://bandwagonhost.com/terms-of-service.php" rel="noopener noreferrer" target="_blank">Terms of Service</a>。目录没有单独的“续费价”字段。以结算页为准。本站较早的方案整理见 <a href="/deals/bandwagonhost-coupon-2026/">搬瓦工 2026 优惠码与方案对比</a>，该文目录核对日期是 2026-11-01（北京时间），与本文不是同一次核对。</blockquote>

{heading("h2", "先说结论")}
<p>先在同一家商家、同一方案、同一机房下，比较“年付一次付清”和“月付买满 12 个月”的标价，再看续费是不是仍按这档标价走。不要只看首期活动价。</p>
<p>以搬瓦工 2026-11-12 的公开目录为例：多个常规方案的年付，大约比月付乘以 12 低约 16%–20%；没有月付、只有季付的方案，也可以把年付和季付乘以 4 比较。这份目录没有单独列出续费价。官方条款允许在账单门户取消续费，并且 30 天退款只适用于新购、不包括续费。条款里没有写“续费会自动比首期更贵”。若你买的是首期优惠、秒杀或赠金，到期后按什么价格续，必须看当时结算页和活动规则，不能用目录标价代替。</p>

{heading("h2", "怎么算年付和月付的差额")}
<p>目录自己说明：Prices are USD cents for the full billing period, not monthly equivalents. Availability can change before checkout. 因此比较时要用同一付款周期的标价做换算，而不是把年付直接当成“每月只要多少”再去和别的商家月费混比。</p>
<p>算法很直接：</p>
<ul>
<li>有月付和年付时：年付标价，对比月付标价 × 12。</li>
<li>没有月付、只有季付和年付时：年付标价，对比季付标价 × 4。</li>
<li>半年付同理，用半年付 × 2 去对比年付。</li>
</ul>
<p>2026-11-12 从公开目录里核对到的例子如下。配置与本站 2026-11-01 那篇方案整理里列出的档位一致，当日标价也一致；这只说明这两次看到的目录价相同，不保证之后不变。</p>
{table(
    ["方案（公开目录名称）", "配置（目录）", "目录标价", "换算成一年后怎么比"],
    [
        ["Basic VPS / 80G KVM - PROMO（pid 46）", "4 核 / 4 GB / 80 GB，月流量 3 TB", "$19.99/月 · $199.99/年", "月付 × 12 = $239.88；年付少付 $39.89，约 16.6%"],
        ["E-Commerce VPS / SPECIAL 40G KVM PROMO V5（pid 88，常说的 CN2 GIA-E 入门档）", "3 核 / 2 GB / 40 GB，月流量 2 TB", "无月付；$89.99/季 · $299.99/年", "季付 × 4 = $359.96；年付少付 $59.97，约 16.7%"],
        ["E-Commerce VPS / SPECIAL 80G KVM PROMO V5（pid 89）", "4 核 / 4 GB / 80 GB，月流量 3 TB", "$56.99/月 · $549.99/年", "月付 × 12 = $683.88；年付少付 $133.89，约 19.6%"],
        ["Ultra VPS / 大阪或新加坡 CN2 GIA 入门档（大阪 pid 134、新加坡 pid 173，2 核 / 2 GB）", "2 核 / 2 GB / 40 GB，月流量 500 GB", "$49.99/月 · $499.99/年", "月付 × 12 = $599.88；年付少付 $99.89，约 16.7%"],
        ["Ultra VPS / 香港 CN2 GIA 入门档（HK_8）", "2 核 / 2 GB / 40 GB，月流量 500 GB", "$89.99/月 · $899.99/年", "月付 × 12 = $1,079.88；年付少付 $179.89，约 16.7%"],
    ],
)}
<p>从这张表可以读出三件实际的事：年付确有固定差额，但不同方案不是同一个百分比；CN2 GIA-E 的入门档在这份目录里没有月付，只有季付、半年付和年付，不能假装它有 $xx/月再去做对比；产品名称里带有 PROMO 或 SPECIAL，在这份公开目录里是常规在售 SKU 的名称，本文不把它解释成限时秒杀，是否仍可下单以结算页为准。</p>

<figure class="shot">
<img src="/img/promos/bandwagonhost-cn2-gia-e.webp" alt="搬瓦工官网 CN2 GIA-E 方案购物车页面截图" width="640" height="400" loading="lazy" decoding="async">
<figcaption>已发布的官网购物车截图，截于 2026-11-01。图中价格如与今天目录或结算页不一致，以官网当前页面为准。来源：<a href="/deals/bandwagonhost-coupon-2026/">搬瓦工方案对比</a>。</figcaption>
</figure>
<p>若要到官网核对该档 CN2 GIA-E 入门方案的结算价，可使用下面的跳转。链接含推广，不改变你应付的价格，也不改变上文按目录算出的差额。</p>
<p><a class="go-btn go-btn-lg" href="/go/bandwagonhost/" rel="sponsored nofollow noopener" target="_blank">去官网核对并下单</a><br>
<small class="cta-note">含推广 · 跳转到搬瓦工官方订购（CN2 GIA-E 相关方案）· 价格以结算页为准</small></p>

{heading("h2", "续费会不会更贵")}
<p>就搬瓦工这份 2026-11-12 的公开目录而言：每个方案按付款周期给出标价，没有名为 renewal 或“续费价”的字段，因此不能从目录推出“续费一定更贵”或“续费一定和首期一样”。</p>
<p>同日核对的官方 Terms of Service 里，与续费、退款直接有关的表述包括：</p>
<ul>
<li>You may cancel service renewal at any time in the billing portal.（可在账单门户取消续费。）</li>
<li>申请退款的条件之一是：Service for which you are requesting a refund is a new order (not a renewal) and was ordered 30 or fewer days ago。也就是 30 天退款针对新购，不包括续费。</li>
</ul>
<p>条款里没有出现“renewal is charged at a higher price”或类似表述。所以对这类按目录周期标价的常规方案，目前能核实的是：年付和月付的差额来自首期标价算法；续费是不是同一档价，要在账单或结算页再看一眼；退款窗口不覆盖续费。</p>
<p>下面几种情况，续费完全可能和你首次付款不一样，而且本文没有在今天的官方页面里逐条核实它们的到期价，因此只提醒你去核，不填数字：</p>
<ul>
<li>首月或首年折扣、优惠码只作用于首期。</li>
<li>秒杀、限量或赠金活动，到期后回到常规价。本站若有整理，以那篇文章自己的核对日期为准，例如 <a href="/deals/raksmart-2026-double11-black-friday/">RakSmart 2026 双11 黑五活动规则</a>，不代表今天活动仍在进行。</li>
<li>免费额度或新用户赠金用尽，见 <a href="/free/free-cloud-credits-2026/">免费服务器与新用户赠金汇总</a> 各条目的官方规则。</li>
</ul>

{heading("h2", "独立站应该月付还是年付")}
{table(
    ["更适合先看哪种", "常见原因", "要注意什么"],
    [
        ["月付（或只有季付时的较短周期）", "市场还在试，机房和线路还没定，可能要搬迁或停掉", "把月付买满一年，通常会比同年付更贵；要先能接受这个差额"],
        ["年付", "访客来源和方案已经稳定，希望按目录标价少付一年的周期差", "先确认该方案有年付；退款通常不含续费；中途要换机房时，先看商家是否允许迁移"],
        ["先月付，稳定后再改年付", "用较短周期做验收，例如先看目标市场能否打开、后台能否维护", "改周期时以当时结算页为准，不能默认能补回已经付过的月费差额"],
    ],
)}
<p>如果你还在按 <a href="/knowledge/chuhai-independent-site-server/">出海独立站怎么选服务器</a> 的顺序选地区和线路，通常先不要把年付锁死在一个还没验收的机房上。RF-KEY射频元器件商城那次体检用的就是月付方案，方便按测试需要使用；这并不等于所有已经稳定的站点都该月付。</p>

{heading("h2", "使用时要注意什么")}
<ul>
<li>不同商家的周期折扣不同，不能把上述 16%–20% 套到别的商家。没有核到的官网目录，本文不填数字。</li>
<li>目录价、购物车价、续费通知里的价格可能在不同时间不一致，下单和到期前都要再看结算页。</li>
<li>优惠码是否还能用，以官网校验结果为准。本站 2026-11-01 的搬瓦工整理写过当时没有可确认的公开优惠码，那是该文自己的核对，不是今天的复查。</li>
<li>现金流出海团队很敏感：年付省下的是周期差，不是质量承诺，也不能替代备份和到期提醒。</li>
</ul>
""".strip()

MON_FAQS = [
    ("年付一定会比月付更便宜吗？",
     "要比较同一方案、同一机房的目录标价。搬瓦工 2026-11-12 公开目录里，文中列出的几个方案，年付大约比月付乘以 12（或季付乘以 4）低约 16%–20%。别的商家没有在本文核对，不能套用这个区间。有的方案根本没有月付，只能用它实际提供的周期来算。"),
    ("续费会不会更贵？",
     "搬瓦工这份公开目录没有单独的续费价字段；同日核对的服务条款也没有写续费会自动高于首期。能够核实的是：可以在账单门户取消续费，且 30 天退款不包括续费。首期优惠、秒杀或赠金到期后按什么价格续，要看当时结算页和活动规则，本文不填未核对的数字。"),
    ("CN2 GIA-E 入门档为什么没有月付？",
     "在 2026-11-12 的公开目录里，该档（pid 88，3 核 / 2 GB）提供的是季付、半年付和年付，没有 monthly。比较时应使用季付乘以 4 对年付，而不是自行假设一个未列出的月价。"),
    ("独立站刚上线，应该年付吗？",
     "如果地区、线路和访问来源还没验收稳定，通常更适合先用较短周期。年付的目录差额只有在你准备用满这一年、并且续费条件也核对过时，才值得优先考虑。"),
    ("目录价和结算页不一样怎么办？",
     "以官网结算页为准。公开目录自己也写明，下单前库存和价格可能变化。本站文章会注明核对日期，但不会代替你下单当时的页面。"),
]


def _rel(*items):
    return list(items)


ARTICLES.extend([
    dict(
        slug="chuhai-independent-site-server",
        title="出海独立站怎么选服务器",
        description="给中国中小企业、个体户和源头工厂的判断顺序：先看访客在哪，再决定要不要精品线路，然后选机房、配置和付款周期。不是优惠汇总。",
        keywords="出海独立站,选服务器,独立站服务器,CN2,年付月付",
        url=f"{SITE}/knowledge/chuhai-independent-site-server/",
        chips=[
            ("cat", "独立站选型"),
            ("tag", "/knowledge/", "知识库"),
            ("tag", "/tools/server-sizing/", "配置下限"),
            ("tag", "/tools/network-lines/", "线路对照"),
        ],
        toc=["先说结论", "先问访客在哪", "配置先看下限，再去比价", "线路、地区和付款周期怎么接起来", "使用时要注意什么", "常见问题"],
        body=HUB_BODY,
        faqs=HUB_FAQS,
        related=[
            (f"{SITE}/knowledge/domestic-visitors-cn2/", "国内访客为主，独立站该不该上 CN2", DATE_VISIBLE),
            (f"{SITE}/knowledge/overseas-visitors-server/", "独立站访客主要在海外时，服务器怎么选", DATE_VISIBLE),
            (f"{SITE}/knowledge/premium-line-when/", "独立站要不要上精品线路", DATE_VISIBLE),
            (f"{SITE}/knowledge/monthly-vs-yearly-vps/", "独立站服务器年付和月付差多少，续费会不会更贵", DATE_VISIBLE),
            (f"{SITE}/cases/rfkey-overseas-check-2026-11/", "RF-KEY射频元器件商城海外访问实测：搬瓦工洛杉矶 $19.99/月", "2026年11月2日"),
        ],
        tags=[("/tags/%E5%A4%96%E8%B4%B8%E7%8B%AC%E7%AB%8B%E7%AB%99/", "外贸独立站")],
        has_affiliate=False,
    ),
    dict(
        slug="domestic-visitors-cn2",
        title="国内访客为主，独立站该不该上 CN2",
        description="访客主要在中国大陆、又在意晚高峰时，本站才把 CN2 GIA 写成更相关的选项；访客主要在海外时，不必因为这是外贸站就先上 CN2。不含未实测的速度结论。",
        keywords="CN2 GIA,独立站,国内访客,AS4809",
        url=f"{SITE}/knowledge/domestic-visitors-cn2/",
        chips=[
            ("cat", "独立站选型"),
            ("tag", "/categories/lines/", "线路"),
            ("tag", "/categories/cn2-gia/", "CN2 GIA"),
            ("tag", "/knowledge/cn2-gia/", "判断框架"),
        ],
        toc=["先说结论", "CN2 GIA 在本站和公开登记里指什么", "该不该上：先对照访客，而不是对照身份", "怎么确认商家说的是 CN2 GIA", "使用时要注意什么", "常见问题"],
        body=DOM_BODY,
        faqs=DOM_FAQS,
        related=[
            (f"{SITE}/knowledge/chuhai-independent-site-server/", "出海独立站怎么选服务器", DATE_VISIBLE),
            (f"{SITE}/knowledge/premium-line-when/", "独立站要不要上精品线路", DATE_VISIBLE),
            (f"{SITE}/knowledge/overseas-visitors-server/", "独立站访客主要在海外时，服务器怎么选", DATE_VISIBLE),
            (f"{SITE}/knowledge/cn2-gia/", "CN2 GIA：先看适不适合", ""),
            (f"{SITE}/routes/cn2-gia/", "CN2 GIA 线路页", ""),
        ],
        tags=[("/tags/%E5%A4%96%E8%B4%B8%E7%8B%AC%E7%AB%8B%E7%AB%99/", "外贸独立站")],
        has_affiliate=False,
    ),
    dict(
        slug="overseas-visitors-server",
        title="独立站访客主要在海外时，服务器怎么选",
        description="访客主要在目标市场时，先把机器放在靠近访客的地区，普通国际线路通常即可；先处理页面体积和 HTTPS，再谈换线路。引用 RF-KEY射频元器件商城已发布的境外体检结论。",
        keywords="独立站,海外访客,选服务器,机房地区",
        url=f"{SITE}/knowledge/overseas-visitors-server/",
        chips=[
            ("cat", "独立站选型"),
            ("tag", "/servers/", "比价目录"),
            ("tag", "/tools/server-sizing/", "配置下限"),
            ("tag", "/cases/rfkey-overseas-check-2026-11/", "实测案例"),
        ],
        toc=["先说结论", "先靠近访客，再谈线路", "配置和页面：先够用，再升级", "国内团队要登后台时怎么处理", "使用时要注意什么", "常见问题"],
        body=OVS_BODY,
        faqs=OVS_FAQS,
        related=[
            (f"{SITE}/knowledge/chuhai-independent-site-server/", "出海独立站怎么选服务器", DATE_VISIBLE),
            (f"{SITE}/knowledge/domestic-visitors-cn2/", "国内访客为主，独立站该不该上 CN2", DATE_VISIBLE),
            (f"{SITE}/knowledge/monthly-vs-yearly-vps/", "独立站服务器年付和月付差多少，续费会不会更贵", DATE_VISIBLE),
            (f"{SITE}/cases/rfkey-overseas-check-2026-11/", "RF-KEY射频元器件商城海外访问实测：搬瓦工洛杉矶 $19.99/月", "2026年11月2日"),
            (f"{SITE}/tools/server-sizing/", "配置下限估算", ""),
        ],
        tags=[("/tags/%E5%A4%96%E8%B4%B8%E7%8B%AC%E7%AB%8B%E7%AB%99/", "外贸独立站"), ("/tags/%E5%AE%9E%E6%B5%8B/", "实测")],
        has_affiliate=False,
    ),
    dict(
        slug="premium-line-when",
        title="独立站要不要上精品线路",
        description="CN2 GIA、9929、CMIN2 分别在什么情况下值得看：先确认大陆访客需求，再按电信、联通、移动对照公开登记和本站线路页。没有实测，不写快慢数字。",
        keywords="精品线路,CN2 GIA,9929,CMIN2,独立站",
        url=f"{SITE}/knowledge/premium-line-when/",
        chips=[
            ("cat", "独立站选型"),
            ("tag", "/categories/lines/", "线路"),
            ("tag", "/categories/cn2-gia/", "CN2 GIA"),
            ("tag", "/categories/as9929/", "AS9929"),
            ("tag", "/categories/cmin2/", "CMIN2"),
        ],
        toc=["先说结论", "三条线分别是什么，适合什么时候看", "什么时候值得看，什么时候不必先看", "目录里能核对到什么，核对不到什么", "使用时要注意什么", "常见问题"],
        body=PREM_BODY,
        faqs=PREM_FAQS,
        related=[
            (f"{SITE}/knowledge/chuhai-independent-site-server/", "出海独立站怎么选服务器", DATE_VISIBLE),
            (f"{SITE}/knowledge/domestic-visitors-cn2/", "国内访客为主，独立站该不该上 CN2", DATE_VISIBLE),
            (f"{SITE}/knowledge/cn2-gia/", "CN2 GIA：先看适不适合", ""),
            (f"{SITE}/routes/cn2-gia/", "CN2 GIA 线路页", ""),
            (f"{SITE}/routes/9929/", "9929 线路页", ""),
            (f"{SITE}/routes/cmin2/", "CMIN2 线路页", ""),
        ],
        tags=[("/tags/%E5%A4%96%E8%B4%B8%E7%8B%AC%E7%AB%8B%E7%AB%99/", "外贸独立站")],
        has_affiliate=False,
    ),
    dict(
        slug="monthly-vs-yearly-vps",
        title="独立站服务器年付和月付差多少，续费会不会更贵",
        description="用同一方案比较年付和月付买满一年的差额，并说明公开目录里有没有单独的续费价。搬瓦工标价与条款核对于 2026-11-12。不以首期活动价代替续费条件。",
        keywords="VPS年付,月付,续费,独立站服务器",
        url=f"{SITE}/knowledge/monthly-vs-yearly-vps/",
        chips=[
            ("cat", "独立站选型"),
            ("tag", "/deals/bandwagonhost-coupon-2026/", "搬瓦工方案对比"),
            ("tag", "/tools/server-sizing/", "配置下限"),
        ],
        toc=["先说结论", "怎么算年付和月付的差额", "续费会不会更贵", "独立站应该月付还是年付", "使用时要注意什么", "常见问题"],
        body=MON_BODY,
        faqs=MON_FAQS,
        related=[
            (f"{SITE}/knowledge/chuhai-independent-site-server/", "出海独立站怎么选服务器", DATE_VISIBLE),
            (f"{SITE}/knowledge/overseas-visitors-server/", "独立站访客主要在海外时，服务器怎么选", DATE_VISIBLE),
            (f"{SITE}/deals/bandwagonhost-coupon-2026/", "搬瓦工 2026 优惠码与方案对比", "2026年11月1日"),
            (f"{SITE}/cases/rfkey-overseas-check-2026-11/", "RF-KEY射频元器件商城海外访问实测：搬瓦工洛杉矶 $19.99/月", "2026年11月2日"),
        ],
        tags=[("/tags/%E5%A4%96%E8%B4%B8%E7%8B%AC%E7%AB%8B%E7%AB%99/", "外贸独立站"), ("/tags/%E6%90%AC%E7%93%A6%E5%B7%A5/", "搬瓦工")],
        has_affiliate=True,
    ),
])


def write_snippets(stats):
    cards = []
    for art in ARTICLES:
        summary = art["description"]
        text = f"{art['title']} {summary}"
        cards.append(f'''    <article class="article-card" data-knowledge="independent-site" data-text="{html.escape(text, quote=True)}">
     <a href="/knowledge/{art['slug']}/">
      <div class="article-body">
       <p class="article-kicker">独立站选型</p>
       <h3>{html.escape(art['title'])}</h3>
       <p>{html.escape(summary)}</p>
      </div>
     </a>
    </article>''')
    index = f'''<!-- 插入知识库首页：1) 在 chip-row 增加下面这个按钮；2) 在 #knowledge-list 内、现有「三网与网络线路」分组之前或之后增加这一组。
     现有 /js/knowledge-filter.js 已按 data-knowledge-filter / data-knowledge 过滤，不必改脚本。
     同时建议把知识库页说明从“只用线路页整理判断框架”改成也覆盖独立站选型专题。 -->
<button class="chip" data-knowledge-filter="independent-site" type="button">独立站选型</button>

<section class="knowledge-group" data-knowledge-group="independent-site">
   <h2>独立站怎么选服务器</h2>
   <div class="article-grid">
{chr(10).join(cards)}
   </div>
</section>
'''
    (ROOT / "snippets" / "knowledge-index-cards.html").write_text(index, encoding="utf-8")

    sm_urls = "\n".join(
        f"<url><loc>{art['url']}</loc><lastmod>2026-11-12T15:30:00+08:00</lastmod><changefreq>weekly</changefreq></url>"
        for art in ARTICLES
    )
    (ROOT / "snippets" / "sitemap-knowledge-urls.xml").write_text(
        "<!-- Append these <url> entries to https://fwqabc.com/sitemap-knowledge.xml (do not invent /en/ equivalents in this pass). -->\n"
        + sm_urls + "\n",
        encoding="utf-8",
    )

    llms = [
        "## 独立站选型（稿件，待发布）",
        "",
        "- [出海独立站怎么选服务器](https://fwqabc.com/knowledge/chuhai-independent-site-server/)：先看访客在哪，再决定线路、机房、配置和付款周期",
        "- [国内访客为主，独立站该不该上 CN2](https://fwqabc.com/knowledge/domestic-visitors-cn2/)",
        "- [独立站访客主要在海外时，服务器怎么选](https://fwqabc.com/knowledge/overseas-visitors-server/)",
        "- [独立站要不要上精品线路](https://fwqabc.com/knowledge/premium-line-when/)：CN2 GIA / 9929 / CMIN2 何时相关",
        "- [独立站服务器年付和月付差多少，续费会不会更贵](https://fwqabc.com/knowledge/monthly-vs-yearly-vps/)",
        "",
    ]
    (ROOT / "snippets" / "llms.txt.fragment").write_text("\n".join(llms), encoding="utf-8")
    (ROOT / "snippets" / "stats.json").write_text(json.dumps(stats, ensure_ascii=False, indent=2), encoding="utf-8")


def main():
    header, footer, afterfooter = load_chrome()
    stats = []
    for art in ARTICLES:
        html_page = render(art, header, footer, afterfooter)
        dest = ROOT / "knowledge" / art["slug"] / "index.html"
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(html_page, encoding="utf-8")
        # basic sanity
        assert "ux-20261112.css" in html_page
        assert "优惠与文章" in html_page
        assert "关于本站" in html_page
        assert 'hreflang="en"' not in html_page or 'href="https://fwqabc.com/en/"' in html_page
        assert f"/en/knowledge/{art['slug']}/" not in html_page
        assert "最佳" not in html_page and "第一" not in html_page and "翻墙" not in html_page
        assert "最低成本" not in html_page and "最高质量" not in html_page
        stats.append({
            "slug": art["slug"],
            "title": art["title"],
            "url": art["url"],
            "path": str(dest),
            "bytes": dest.stat().st_size,
            "chars_zh_or_compact": art["_chars"],
            "reading_minutes": art["_minutes"],
            "has_affiliate": art["has_affiliate"],
        })
        print(f"wrote {dest} ({dest.stat().st_size} bytes, ~{art['_chars']} chars, {art['_minutes']} min)")
    write_snippets(stats)


if __name__ == "__main__":
    main()
