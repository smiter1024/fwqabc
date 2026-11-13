#!/usr/bin/env python3
"""Build surgical HTML patches from live templates. Do not use as a full-site publish."""
from __future__ import annotations

import json
import re
import shutil
from copy import deepcopy
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parent
TEMPL = Path("/tmp/fwqabc-templates")
OUT = ROOT / "out"

CASE_PATH = "/cases/cavityfilter-site-build-2026-11/"
PILLAR_PATH = "/knowledge/chuhai-independent-site/"
CASE_URL = "https://fwqabc.com" + CASE_PATH
PILLAR_URL = "https://fwqabc.com" + PILLAR_PATH
PUB = "2026-11-13T09:00:00+08:00"
PUB_DATE = "2026年11月13日"
LASTMOD_CLEANUP = "2026-11-12T21:42:00+08:00"
LASTMOD_NEW = PUB
NS = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}

CASE_TITLE = "康讯通独立站建站记录：从域名、服务器到上线（cavityfilter.com）"
CASE_DESC = "出海ABC为深圳康讯通搭建中英文独立站。本文记录域名注册、解析与企业邮箱、源站部署和站点结构，复核于 2026 年 11 月 13 日（北京时间）。本页不是访问测速，也不对服务器性能下结论。"
PILLAR_TITLE = "建站与独立站"
PILLAR_DESC = "说明出海独立站在展示站与卖货站、域名与企业邮箱、多语言以及上线维护上要先看清的事项，并连到已核对的康讯通建站记录和服务器选型说明。"

CASE_FAQS = [
    ("这是不是一次服务器测速？", "不是。本文核对的是域名、解析、证书、邮箱、跳转和站点结构。没有自购实测，不下性能结论。"),
    ("为什么不写服务器套餐和价格？", "公开可核对的是系统、Web 服务、网络归属和跳转行为。套餐品牌与标价没有可引用的公开结算页，按本站规则不写。"),
    ("域名在 Cloudflare 注册，是不是已经用了它的内容分发网络？", "不一定。本次复核时，解析在 Cloudflare，页面由源站直接返回。两者要分开看。"),
    ("复数域名是必须的吗？", "不是必须，但这次一并注册了 cavityfilters.com，并统一跳转到主站，避免客户多输入一个 s 时离开本站。"),
]
PILLAR_FAQS = [
    ("先买服务器，还是先定域名和站点类型？", "宜先确定站点是展示询价还是在线交易，并准备域名与对外邮箱，再按访客所在地选择服务器。机器只是开门面里的一笔，不能代替站点类型和联系方式。"),
    ("展示站要不要做成和电商平台一样的结算流程？", "不是必须。若当前只需要说明产品和接收询价，可以先做成展示与询价站，把收款放在合同或另行约定的通道。若要在网站上收款，再单独核对支付、税务和售后条件。没有核对过的通道费率，本页不写。"),
    ("域名和解析在同一家办理，是不是就够了？", "还要单独看邮箱能否用该域名发信，以及页面是否由源站或内容分发网络提供。康讯通这次是注册、解析在 Cloudflare，页面由源站直接提供，邮箱在 Zoho。这不是唯一做法。"),
    ("本页为什么不列建站平台或邮箱的报价表？", "没有在本页引用的公开结算页上逐项核对过这些价格。按本站规则，没有核实，不下价格结论。已核对的过程写在康讯通建站记录里。"),
]


def h(s: str) -> str:
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def set_meta(html: str, *, title: str, desc: str, url: str, keywords: str, og_image: str | None = None, og_type: str = "article") -> str:
    html = re.sub(r"<title>.*?</title>", f"<title>{h(title)} | fwqabc 出海ABC</title>", html, count=1, flags=re.S)

    def one(pattern, repl):
        nonlocal html
        html, n = re.subn(pattern, repl, html, count=1)
        if n == 0:
            raise SystemExit(f"meta miss: {pattern}")

    one(r'<meta name="?keywords"? content="[^"]*">', lambda m: re.sub(r'content="[^"]*"', f'content="{h(keywords)}"', m.group(0)))
    one(r'<meta name="?description"? content="[^"]*">', lambda m: re.sub(r'content="[^"]*"', f'content="{h(desc)}"', m.group(0)))
    one(r'<meta property="og:title" content="[^"]*">', f'<meta property="og:title" content="{h(title)}">')
    one(r'<meta property="og:description" content="[^"]*">', f'<meta property="og:description" content="{h(desc)}">')
    one(r'<meta property="og:url" content="[^"]*">', f'<meta property="og:url" content="{url}">')
    one(r'<meta property="og:type" content="[^"]*">', f'<meta property="og:type" content="{og_type}">')
    one(r'<meta property="article:published_time" content="[^"]*">', f'<meta property="article:published_time" content="{PUB}">')
    one(r'<meta property="article:modified_time" content="[^"]*">', f'<meta property="article:modified_time" content="{PUB}">')
    one(r'<meta name="?twitter:title"? content="[^"]*">', lambda m: re.sub(r'content="[^"]*"', f'content="{h(title)}"', m.group(0)))
    one(r'<meta name="?twitter:description"? content="[^"]*">', lambda m: re.sub(r'content="[^"]*"', f'content="{h(desc)}"', m.group(0)))
    if og_image:
        one(r'<meta property="og:image" content="[^"]*">', f'<meta property="og:image" content="{og_image}">')
        one(r'<meta name="?twitter:image"? content="[^"]*">', lambda m: re.sub(r'content="[^"]*"', f'content="{og_image}"', m.group(0)))
    if re.search(r"<link rel=canonical href=[^>\s]+>", html):
        one(r"<link rel=canonical href=[^>\s]+>", f"<link rel=canonical href={url}>")
    else:
        one(r'<link rel="canonical" href="[^"]*" */?>', f'<link rel="canonical" href="{url}">')
    return html



def replace_ld_json(html: str, blocks: list[dict]) -> str:
    scripts = [
        '<script type="application/ld+json">' + json.dumps(b, ensure_ascii=False, separators=(",", ":")) + "</script>"
        for b in blocks
    ]
    pattern = re.compile(r'<script type="?application/ld\+json"?>[\s\S]*?</script>')
    html, n = pattern.subn("", html)
    if n == 0:
        raise SystemExit("no JSON-LD scripts to replace")
    html = html.replace("</head>", "\n" + "\n".join(scripts) + "\n</head>", 1)
    return html



def faq_ld(faqs):
    return {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}}
            for q, a in faqs
        ],
    }


def crumbs(items):
    return {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": i, "name": name, "item": url}
            for i, (name, url) in enumerate(items, 1)
        ],
    }


def posting(*, headline, desc, url, body, crumbs_name):
    return {
        "@context": "https://schema.org",
        "@type": "BlogPosting",
        "headline": headline,
        "name": headline,
        "description": desc,
        "url": url,
        "datePublished": PUB,
        "dateModified": PUB,
        "inLanguage": "zh-CN",
        "author": {"@type": "Organization", "name": "出海ABC", "url": "https://fwqabc.com/"},
        "publisher": {"@type": "Organization", "name": "出海ABC", "url": "https://fwqabc.com/"},
        "articleBody": re.sub(r"<[^>]+>", " ", body),
    }


def toc_from_body(body: str) -> str:
    items = []
    for m in re.finditer(r"<h2 id=([^>\s]+)>(.*?)<a ", body):
        hid, title = m.group(1), re.sub(r"<[^>]+>", "", m.group(2)).strip()
        items.append(f'<li><a href=#{hid} aria-label={h(title)}>{title}</a></li>')
    return (
        '<details class=toc open><summary accesskey=c title="(Alt + C)"><span class=title>目录</span></summary>'
        f'<div class=inner><ul>{"".join(items)}</ul></div></details>'
    )


def replace_between(html: str, start_pat: str, end_pat: str, new: str) -> str:
    s = re.search(start_pat, html)
    e = re.search(end_pat, html)
    if not s or not e or e.start() < s.end():
        raise SystemExit(f"cannot splice {start_pat} .. {end_pat}")
    return html[: s.start()] + new + html[e.start() :]


def build_case() -> str:
    html = (TEMPL / "cases/rfkey-overseas-check-2026-11/index.html").read_text("utf-8")
    body = (ROOT / "snippets/case-body.html").read_text("utf-8")
    html = set_meta(html, title=CASE_TITLE, desc=CASE_DESC, url=CASE_URL, keywords="外贸独立站,建站记录,cavityfilter.com,康讯通", og_image="https://fwqabc.com/img/cases/cavityfilter-2026-11/cover.webp")
    html = replace_ld_json(
        html,
        [
            faq_ld(CASE_FAQS),
            crumbs([("首页", "https://fwqabc.com/"), ("实测案例", "https://fwqabc.com/cases/"), (CASE_TITLE, CASE_URL)]),
            posting(headline=CASE_TITLE, desc=CASE_DESC, url=CASE_URL, body=body, crumbs_name="cases"),
        ],
    )
    header = f'''<header class="post-header post-band"><nav class=breadcrumbs role=navigation aria-label=Breadcrumb><a href=/>首页</a>
<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-chevron-right"><polyline points="9 18 15 12 9 6"/></svg>
<a href=/cases/>实测案例</a>
<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-chevron-right"><polyline points="9 18 15 12 9 6"/></svg></nav><div class=post-chips><span class="cat-chip sec-cases">建站记录</span><a class=tag-chip href=/tags/%E5%A4%96%E8%B4%B8%E7%8B%AC%E7%AB%8B%E7%AB%99/>#外贸独立站</a></div><h1 class="post-title entry-hint-parent">{h(CASE_TITLE)}</h1><div class=post-description>{h(CASE_DESC)}</div><div class=post-meta><span title={PUB}>{PUB_DATE}</span>&nbsp;·&nbsp;<span>约 8 分钟阅读</span></div><div class=post-actions><button type=button class=btn-ghost data-copy-url={CASE_URL}>复制链接</button>
<a class=btn-ghost href="https://twitter.com/intent/tweet?text={h(CASE_TITLE)}&url=https%3A%2F%2Ffwqabc.com%2Fcases%2Fcavityfilter-site-build-2026-11%2F" target=_blank rel=noopener>分享到 X</a></div><script src=/js/post-actions.js defer></script></header>'''
    related = '''<nav class="related" aria-label=相关文章><h2>相关文章</h2><ul>
<li><a href="https://fwqabc.com/knowledge/chuhai-independent-site/">建站与独立站</a><small>2026年11月13日</small></li>
<li><a href="https://fwqabc.com/knowledge/chuhai-independent-site-server/">出海独立站怎么选服务器</a><small>2026年11月12日</small></li>
<li><a href="https://fwqabc.com/cases/rfkey-overseas-check-2026-11/">RF-KEY射频元器件商城海外访问实测：搬瓦工洛杉矶 $19.99/月</a><small>2026年11月2日</small></li>
</ul><p class="back-picks"><a href="/knowledge/chuhai-independent-site/">« 建站与独立站</a> · <a href="/cases/">实测案例</a> · <a href="/#map">出海成本地图</a></p></nav>
<footer class=post-footer><ul class=post-tags><li><a href=https://fwqabc.com/tags/%E5%A4%96%E8%B4%B8%E7%8B%AC%E7%AB%8B%E7%AB%99/>外贸独立站</a></li></ul></footer>'''
    # replace from <header class="post-header through </article>
    html = replace_between(
        html,
        r'<header class="post-header post-band">',
        r"</article>",
        header + toc_from_body(body) + f'<div class=post-content>\n{body}\n</div>\n{related}\n',
    )
    # drop leftover affiliate notice if any slipped
    html = html.replace('<p class=aff-notice>本文含推广链接，详见 <a href=/disclosure/>推广披露</a>。</p>', "")
    return html


def build_pillar() -> str:
    html = (TEMPL / "knowledge/chuhai-independent-site-server/index.html").read_text("utf-8")
    body = (ROOT / "snippets/pillar-body.html").read_text("utf-8")
    html = set_meta(html, title=PILLAR_TITLE, desc=PILLAR_DESC, url=PILLAR_URL, keywords="建站与独立站,外贸独立站,域名,企业邮箱")
    html = replace_ld_json(
        html,
        [
            faq_ld(PILLAR_FAQS),
            crumbs([("首页", "https://fwqabc.com/"), ("知识库", "https://fwqabc.com/knowledge/"), (PILLAR_TITLE, PILLAR_URL)]),
            posting(headline=PILLAR_TITLE, desc=PILLAR_DESC, url=PILLAR_URL, body=body, crumbs_name="knowledge"),
        ],
    )
    # header may be pretty-printed in this template
    header_pat = r"<header class=\"post-header[^\"]*\">"
    if not re.search(header_pat, html):
        header_pat = r"<header class=post-header[^>]*>"
    # Build a PaperMod-like header matching this template's quoting if possible
    pretty = 'class="post-header' in html
    if pretty:
        header = f'''<header class="post-header post-band"><nav aria-label="Breadcrumb" class="breadcrumbs" role="navigation"><a href="/">首页</a>
<svg class="feather feather-chevron-right" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" viewBox="0 0 24 24"><polyline points="9 18 15 12 9 6"></polyline></svg>
<a href="/knowledge/">知识库</a>
<svg class="feather feather-chevron-right" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" viewBox="0 0 24 24"><polyline points="9 18 15 12 9 6"></polyline></svg></nav><div class="post-chips"><span class="cat-chip">建站与独立站</span><a class="tag-chip" href="/tags/%E5%A4%96%E8%B4%B8%E7%8B%AC%E7%AB%8B%E7%AB%99/">#外贸独立站</a></div><h1 class="post-title entry-hint-parent">{h(PILLAR_TITLE)}</h1><div class="post-description">{h(PILLAR_DESC)}</div><div class="post-meta"><span title="{PUB}">{PUB_DATE}</span>&nbsp;·&nbsp;<span>约 6 分钟阅读</span></div><div class="post-actions"><button class="btn-ghost" data-copy-url="{PILLAR_URL}" type="button">复制链接</button>
<a class="btn-ghost" href="https://twitter.com/intent/tweet?text={h(PILLAR_TITLE)}&amp;url=https%3A%2F%2Ffwqabc.com%2Fknowledge%2Fchuhai-independent-site%2F" rel="noopener" target="_blank">分享到 X</a></div><script defer="" src="/js/post-actions.js"></script></header>'''
        related = f'''<nav aria-label="相关文章" class="related"><h2>相关文章</h2><ul>
<li><a href="{CASE_URL}">康讯通独立站建站记录：从域名、服务器到上线（cavityfilter.com）</a><small>2026年11月13日</small></li>
<li><a href="https://fwqabc.com/knowledge/chuhai-independent-site-server/">出海独立站怎么选服务器</a><small>2026年11月12日</small></li>
<li><a href="https://fwqabc.com/knowledge/overseas-visitors-server/">独立站访客主要在海外时，服务器怎么选</a><small>2026年11月12日</small></li>
<li><a href="https://fwqabc.com/cases/rfkey-overseas-check-2026-11/">RF-KEY射频元器件商城海外访问实测：搬瓦工洛杉矶 $19.99/月</a><small>2026年11月2日</small></li>
</ul><p class="back-picks"><a href="/#map">« 出海成本地图</a> · <a href="/knowledge/">知识库</a> · <a href="/knowledge/chuhai-independent-site-server/">怎么选服务器</a></p></nav>
<footer class="post-footer"><ul class="post-tags"><li><a href="/tags/%E5%A4%96%E8%B4%B8%E7%8B%AC%E7%AB%8B%E7%AB%99/">外贸独立站</a></li></ul></footer>'''
        body_wrap = f'<div class="post-content">\n{body}\n</div>\n{related}\n'
    else:
        header = f'''<header class="post-header post-band">...</header>'''
        raise SystemExit("unexpected knowledge template quoting")
    html = replace_between(html, header_pat, r"</article>", header + toc_from_body(body) + body_wrap)
    return html


def link_cost_map(html: str) -> str:
    old = "<div class=cm-card><h4>建站与独立站</h4><ul><li>展示站还是卖货站</li><li>域名和企业邮箱</li><li>多语言、多币种</li><li>上线后的维护</li></ul></div>"
    new = '<a class="cm-card cm-hot" href=/knowledge/chuhai-independent-site/><h4>建站与独立站</h4><ul><li>展示站还是卖货站</li><li>域名和企业邮箱</li><li>多语言、多币种</li><li>上线后的维护</li></ul><span class=cm-more>了解详情 →</span></a>'
    if old not in html:
        raise SystemExit("cost-map card not found")
    return html.replace(old, new, 1)


def patch_cases_index(html: str) -> str:
    html = html.replace(
        "我们用自己购买的服务器做的真实测试：机器、价格、机房、测试方法和原始数据都写清楚，结论只适用于测试当时的测试点与样本。",
        "本栏收录两类记录：一是用自购服务器做的访问实测，会写明机器、价格、机房、方法和数据；二是本站参与搭建的独立站记录，会写明域名、邮箱、部署和站点结构。结论只适用于各文写明的范围。",
    )
    card = f'''<div class=case-list><article class=case-card><a class=case-cover href={CASE_PATH}><img src=/img/cases/cavityfilter-2026-11/cover.webp alt="cavityfilter.com 英文首页截图，核对于 2026 年 11 月 13 日（北京时间）" width=800 height=500 loading=lazy decoding=async><span class=case-badge>建站记录</span></a><div class=case-body><div class=case-chips><span>康讯通</span><span>cavityfilter.com</span><span>域名到上线</span></div><h2><a href={CASE_PATH}>{h(CASE_TITLE)}</a></h2><div class="case-metrics sm"><div><b>2026-11-11</b><span>域名注册（北京时间）</span></div><div><b>中英对照</b><span>展示与询价型独立站</span></div><div><b>186</b><span>站点地图网址（11月13日复核）</span></div></div><div class=case-foot><small>2026年11月13日</small><a class=read-more href={CASE_PATH}>看完整记录 →</a></div></div></article>'''
    if "<div class=case-list>" not in html:
        raise SystemExit("case-list missing")
    html = html.replace("<div class=case-list>", card, 1)
    return html


def patch_knowledge_index(html: str) -> str:
    html = html.replace(
        "独立站选型与网络线路说明，便于判断是否适用后再比较套餐。",
        "独立站建站、选型与网络线路说明，便于判断是否适用后再比较套餐。",
    )
    html = html.replace(
        "本栏收录独立站选购专题，以及根据已发布线路说明整理的摘要。详细内容见各专题和线路页。",
        "本栏收录建站与独立站说明、独立站选购专题，以及根据已发布线路说明整理的摘要。详细内容见各专题和线路页。",
    )
    chip = '<button type=button class=chip data-knowledge-filter=site-build>建站与独立站</button>'
    anchor = '<button type=button class=chip data-knowledge-filter=independent-site>独立站选型</button>'
    if chip not in html:
        if anchor not in html:
            # pretty quoted variant
            anchor2 = '<button type="button" class="chip" data-knowledge-filter="independent-site">独立站选型</button>'
            chip2 = '<button type="button" class="chip" data-knowledge-filter="site-build">建站与独立站</button>'
            if anchor2 not in html:
                raise SystemExit("knowledge filter chip not found")
            html = html.replace(anchor2, chip2 + anchor2, 1)
        else:
            html = html.replace(anchor, chip + anchor, 1)
    section = f'''<section class="knowledge-group" data-knowledge-group="site-build">
   <h2>建站与独立站</h2>
   <div class="article-grid">
    <article class="article-card" data-knowledge="site-build" data-text="{h(PILLAR_TITLE + " " + PILLAR_DESC)}">
     <a href="{PILLAR_PATH}">
      <div class="article-body">
       <p class="article-kicker">建站与独立站</p>
       <h3>{h(PILLAR_TITLE)}</h3>
       <p>{h(PILLAR_DESC)}</p>
      </div>
     </a>
    </article>
    <article class="article-card" data-knowledge="site-build" data-text="{h(CASE_TITLE + " " + CASE_DESC)}">
     <a href="{CASE_PATH}">
      <div class="article-body">
       <p class="article-kicker">建站记录</p>
       <h3>{h(CASE_TITLE)}</h3>
       <p>{h(CASE_DESC)}</p>
      </div>
     </a>
    </article>
   </div>
</section>'''
    marker = '<section class="knowledge-group" data-knowledge-group="independent-site">'
    if marker not in html:
        marker = '<section class="knowledge-group" data-knowledge-group="independent-site">'
    if "data-knowledge-group=\"independent-site\"" not in html and "data-knowledge-group=independent-site" in html:
        html = html.replace(
            '<section class="knowledge-group" data-knowledge-group=independent-site>',
            section + '<section class="knowledge-group" data-knowledge-group=independent-site>',
            1,
        )
    elif "data-knowledge-group=\"independent-site\"" in html:
        html = html.replace(
            '<section class="knowledge-group" data-knowledge-group="independent-site">',
            section + '<section class="knowledge-group" data-knowledge-group="independent-site">',
            1,
        )
    else:
        raise SystemExit("knowledge group not found")
    return html


def set_lastmod(root, loc, lastmod, *, create=False):
    ET.register_namespace("", NS["s"])
    found = None
    for url in root.findall("s:url", NS):
        if (url.findtext("s:loc", default="", namespaces=NS) or "") == loc:
            found = url
            break
    if found is None:
        if not create:
            return False
        url = ET.SubElement(root, f"{{{NS['s']}}}url")
        loc_el = ET.SubElement(url, f"{{{NS['s']}}}loc")
        loc_el.text = loc
        lm = ET.SubElement(url, f"{{{NS['s']}}}lastmod")
        lm.text = lastmod
        return True
    lm = found.find("s:lastmod", NS)
    if lm is None:
        lm = ET.SubElement(found, f"{{{NS['s']}}}lastmod")
    lm.text = lastmod
    return True


def write_xml(root, dest: Path):
    ET.register_namespace("", NS["s"])
    dest.write_text(
        '<?xml version="1.0" encoding="utf-8" standalone="yes"?>' + ET.tostring(root, encoding="unicode") + "\n",
        encoding="utf-8",
    )


def patch_sitemaps(out_root: Path):
    cleanup_locs = {
        "https://fwqabc.com/": LASTMOD_CLEANUP,
        "https://fwqabc.com/contact/": LASTMOD_CLEANUP,
        "https://fwqabc.com/services/": LASTMOD_CLEANUP,
        "https://fwqabc.com/services/overseas-company/": LASTMOD_CLEANUP,
        "https://fwqabc.com/knowledge/": LASTMOD_NEW,  # index updated today
        "https://fwqabc.com/knowledge/as9929/": LASTMOD_CLEANUP,
        "https://fwqabc.com/knowledge/cmin2/": LASTMOD_CLEANUP,
        "https://fwqabc.com/knowledge/cn2-gia/": LASTMOD_CLEANUP,
        "https://fwqabc.com/knowledge/domestic-visitors-cn2/": LASTMOD_CLEANUP,
        "https://fwqabc.com/knowledge/premium-line-when/": LASTMOD_CLEANUP,
        "https://fwqabc.com/categories/as9929/": LASTMOD_CLEANUP,
        "https://fwqabc.com/categories/cmin2/": LASTMOD_CLEANUP,
        "https://fwqabc.com/categories/cn2-gia/": LASTMOD_CLEANUP,
        "https://fwqabc.com/categories/lines/": LASTMOD_CLEANUP,
        "https://fwqabc.com/en/": LASTMOD_CLEANUP,
        "https://fwqabc.com/en/contact/": LASTMOD_CLEANUP,
        "https://fwqabc.com/en/services/": LASTMOD_CLEANUP,
        "https://fwqabc.com/en/services/overseas-company/": LASTMOD_CLEANUP,
        "https://fwqabc.com/en/knowledge/": LASTMOD_CLEANUP,
        "https://fwqabc.com/en/knowledge/as9929/": LASTMOD_CLEANUP,
        "https://fwqabc.com/en/knowledge/cmin2/": LASTMOD_CLEANUP,
        "https://fwqabc.com/en/knowledge/cn2-gia/": LASTMOD_CLEANUP,
        "https://fwqabc.com/en/terms/": LASTMOD_CLEANUP,
        "https://fwqabc.com/about/": LASTMOD_NEW,
        "https://fwqabc.com/cases/": LASTMOD_NEW,
        PILLAR_URL: LASTMOD_NEW,
        CASE_URL: LASTMOD_NEW,
    }
    # pages sitemap (home, about, contact, services, categories…)
    pages = ET.parse(TEMPL / "sitemap-pages.xml").getroot()
    for loc, lm in cleanup_locs.items():
        if loc in (PILLAR_URL, CASE_URL):
            continue
        if loc.startswith("https://fwqabc.com/knowledge/") and loc != "https://fwqabc.com/knowledge/":
            continue
        if loc.startswith("https://fwqabc.com/cases/"):
            continue
        if "/en/" in loc[8:]:  # handled in en sitemap
            if loc != "https://fwqabc.com/en/":
                continue
        set_lastmod(pages, loc, lm)
    # home was already in pages
    set_lastmod(pages, "https://fwqabc.com/", LASTMOD_NEW)  # cost-map link added today
    write_xml(pages, out_root / "sitemap-pages.xml")

    know = ET.parse(TEMPL / "sitemap-knowledge.xml").getroot()
    for loc, lm in cleanup_locs.items():
        if loc.startswith("https://fwqabc.com/knowledge/"):
            set_lastmod(know, loc, lm)
    set_lastmod(know, PILLAR_URL, LASTMOD_NEW, create=True)
    write_xml(know, out_root / "sitemap-knowledge.xml")

    posts = ET.parse(TEMPL / "sitemap-posts.xml").getroot()
    set_lastmod(posts, CASE_URL, LASTMOD_NEW, create=True)
    write_xml(posts, out_root / "sitemap-posts.xml")

    en_pages = ET.parse(TEMPL / "en/sitemap-pages.xml").getroot()
    for loc, lm in cleanup_locs.items():
        if loc.startswith("https://fwqabc.com/en/") and not loc.startswith("https://fwqabc.com/en/knowledge/"):
            set_lastmod(en_pages, loc, lm)
    write_xml(en_pages, out_root / "en/sitemap-pages.xml")

    en_know = ET.parse(TEMPL / "en/sitemap-knowledge.xml").getroot()
    for loc, lm in cleanup_locs.items():
        if loc.startswith("https://fwqabc.com/en/knowledge/"):
            set_lastmod(en_know, loc, lm)
    write_xml(en_know, out_root / "en/sitemap-knowledge.xml")

    # index lastmods
    for src, dest, child, lm in [
        (TEMPL / "sitemap.xml", out_root / "sitemap.xml", None, LASTMOD_NEW),
        (TEMPL / "zh-cn/sitemap.xml", out_root / "zh-cn/sitemap.xml", None, LASTMOD_NEW),
        (TEMPL / "en/sitemap.xml", out_root / "en/sitemap.xml", None, LASTMOD_NEW),
    ]:
        tree = ET.parse(src)
        root = tree.getroot()
        for sm in root.findall("s:sitemap", NS):
            existing = sm.find("s:lastmod", NS)
            if existing is None:
                el = ET.SubElement(sm, f"{{{NS['s']}}}lastmod")
                el.text = lm
            else:
                existing.text = lm
        write_xml(root, dest)


def patch_llms(text: str) -> str:
    text = text.replace(
        "- [实测案例](https://fwqabc.com/cases/)：自购机器的测试记录与适用边界",
        "- [实测案例](https://fwqabc.com/cases/)：自购机器的访问实测，以及本站参与搭建的独立站记录",
        1,
    )
    needle = "- [出海独立站怎么选服务器](https://fwqabc.com/knowledge/chuhai-independent-site-server/)：先看访客在哪，再决定线路、机房、配置和付款周期"
    insert = (
        "- [建站与独立站](https://fwqabc.com/knowledge/chuhai-independent-site/)：展示站与卖货站、域名与企业邮箱、多语言和上线维护\n"
        "- [海外公司注册](https://fwqabc.com/services/overseas-company/)：公布海外公司注册及常见配套项目的用户报价，银行开户等项目可询价\n"
        + needle
    )
    if needle not in text:
        raise SystemExit("llms core line missing")
    text = text.replace(needle, insert, 1)
    recent = "## 近期文章\n"
    add = (
        "## 近期文章\n\n"
        "- [康讯通独立站建站记录：从域名、服务器到上线（cavityfilter.com）](https://fwqabc.com/cases/cavityfilter-site-build-2026-11/)\n"
        "- [建站与独立站](https://fwqabc.com/knowledge/chuhai-independent-site/)\n"
    )
    if recent not in text:
        raise SystemExit("llms recent missing")
    text = text.replace(recent, add, 1)
    return text



def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / "en").mkdir(parents=True)
    (OUT / "zh-cn").mkdir(parents=True)
    (OUT / "cases/cavityfilter-site-build-2026-11").mkdir(parents=True)
    (OUT / "knowledge/chuhai-independent-site").mkdir(parents=True)
    (OUT / "img/cases/cavityfilter-2026-11").mkdir(parents=True)
    (OUT / "about").mkdir(parents=True)
    (OUT / "contact")  # noqa
    shutil.copytree(ROOT / "img/cases/cavityfilter-2026-11", OUT / "img/cases/cavityfilter-2026-11", dirs_exist_ok=True)

    case_html = build_case()
    (OUT / "cases/cavityfilter-site-build-2026-11/index.html").write_text(case_html, encoding="utf-8")
    pillar_html = build_pillar()
    (OUT / "knowledge/chuhai-independent-site/index.html").write_text(pillar_html, encoding="utf-8")

    (OUT / "index.html").write_text(link_cost_map((TEMPL / "index.html").read_text("utf-8")), encoding="utf-8")
    (OUT / "about/index.html").write_text(link_cost_map((TEMPL / "about/index.html").read_text("utf-8")), encoding="utf-8")
    (OUT / "cases/index.html").write_text(patch_cases_index((TEMPL / "cases/index.html").read_text("utf-8")), encoding="utf-8")
    (OUT / "knowledge/index.html").write_text(patch_knowledge_index((TEMPL / "knowledge/index.html").read_text("utf-8")), encoding="utf-8")
    (OUT / "llms.txt").write_text(patch_llms((TEMPL / "llms.txt").read_text("utf-8")), encoding="utf-8")
    patch_sitemaps(OUT)

    # sanity
    checks = {
        OUT / "cases/cavityfilter-site-build-2026-11/index.html": ["cavityfilter.com", "没有自购实测", CASE_TITLE, "请扫描", "主题请写", "本站不报价"],
        OUT / "knowledge/chuhai-independent-site/index.html": ["建站与独立站", "康讯通", "请扫描", "主题请写"],
        OUT / "index.html": ['href=/knowledge/chuhai-independent-site/', "请扫描"],
        OUT / "llms.txt": ["overseas-company", "chuhai-independent-site", "cavityfilter-site-build"],
    }
    forbid_only = {"请扫描", "主题请写", "本站不报价"}
    for path, keys in checks.items():
        t = path.read_text("utf-8")
        for k in keys:
            present = k in t
            if k in forbid_only:
                if present:
                    raise SystemExit(f"forbidden {k} in {path}")
            elif not present:
                raise SystemExit(f"missing {k} in {path}")
    print("OK built", OUT)
    for p in sorted(OUT.rglob("*")):
        if p.is_file():
            print(f"  {p.relative_to(OUT)}  {p.stat().st_size}")


if __name__ == "__main__":
    main()
