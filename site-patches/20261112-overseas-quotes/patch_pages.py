#!/usr/bin/env python3
"""Patch live-style overseas-company HTML with public user quotes. No channel prices."""
import json
import re
from pathlib import Path

ROOT = Path("/workspace/fwqabc-quotes")
OUT = ROOT / "out"

DESC_ZH = (
    "出海第一步：先立主体。本页公布海外公司注册及常见配套的用户报价，银行开户等项目可询价。"
    "办理所需的完整资质和牌照由承办供应商持有；出海ABC负责获客，并把咨询交给供应商对接。"
    "本站不代收款项，也不在网页上收集证件。"
)
DESC_EN = (
    "Step 1 of going overseas: set up a company. This page publishes user quotes for overseas company registration and common add-ons. "
    "Bank accounts and some other items are by inquiry. The licences and qualifications needed to file sit with the fulfilling supplier. "
    "出海ABC only acquires customers and hands inquiries to that supplier. This site does not take payment or collect ID documents."
)

FAQ_ZH = {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    "mainEntity": [
        {
            "@type": "Question",
            "name": "资质和牌照是谁的？",
            "acceptedAnswer": {
                "@type": "Answer",
                "text": "办理所需的完整资质和牌照，由承办供应商持有。出海ABC只负责获客，并把咨询交给供应商对接。",
            },
        },
        {
            "@type": "Question",
            "name": "钱付给谁？",
            "acceptedAnswer": {
                "@type": "Answer",
                "text": "请直接付给承办供应商。本站不代收注册款项，也不在网页上收集护照或证件。",
            },
        },
        {
            "@type": "Question",
            "name": "为什么有的项目没有报价？",
            "acceptedAnswer": {
                "@type": "Answer",
                "text": "银行开户、已暂停或需另议的项目，以及未列出的特殊主体，请发邮件或微信询价。我们不在这里另行估价格。",
            },
        },
        {
            "@type": "Question",
            "name": "要不要本人到场？",
            "acceptedAnswer": {
                "@type": "Answer",
                "text": "咨询和交资料都在邮件或微信里完成，不为了注册要求你飞到当地。有的地方另有身份核验，例如英国注册处要在线认证，对接时会单独说明。",
            },
        },
        {
            "@type": "Question",
            "name": "没有 SSN 能办吗？",
            "acceptedAnswer": {
                "@type": "Answer",
                "text": "没有 SSN 也可以先咨询。已经有 SSN 或 ITIN 的，准备材料时可以一并带上。美国各州注册的用户报价，默认包含申请 EIN。",
            },
        },
        {
            "@type": "Question",
            "name": "选哪个州？",
            "acceptedAnswer": {
                "@type": "Answer",
                "text": "本页已列出各州用户报价，选择按用途在对接时确定，这一页不代你选州。纽约州 LLC 因为要登报，一般不建议，可以改问 INC，或其他州。",
            },
        },
    ],
}

FAQ_EN = {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    "mainEntity": [
        {
            "@type": "Question",
            "name": "Who holds the licences and qualifications?",
            "acceptedAnswer": {
                "@type": "Answer",
                "text": "The licences and qualifications needed to file sit with the fulfilling supplier. 出海ABC only acquires customers and hands inquiries to that supplier.",
            },
        },
        {
            "@type": "Question",
            "name": "Who do I pay?",
            "acceptedAnswer": {
                "@type": "Answer",
                "text": "Pay the fulfilling supplier directly. This site does not take registration payments, and it does not collect a passport or other ID on the page.",
            },
        },
        {
            "@type": "Question",
            "name": "Why are some items without a quote?",
            "acceptedAnswer": {
                "@type": "Answer",
                "text": "Bank accounts, items that are paused or to be agreed, and special entities not listed here are by email or WeChat inquiry. This page does not invent a price for them.",
            },
        },
        {
            "@type": "Question",
            "name": "Do I have to travel?",
            "acceptedAnswer": {
                "@type": "Answer",
                "text": "Inquiry and document exchange are done by email or WeChat. You are not asked to fly there just to register. Some places have a separate identity check, such as the UK registrar’s online verification, which is explained at the handoff.",
            },
        },
        {
            "@type": "Question",
            "name": "Can I file without an SSN?",
            "acceptedAnswer": {
                "@type": "Answer",
                "text": "Yes, you can inquire without an SSN. If you already have an SSN or ITIN, include it when you prepare documents. User quotes for US state registrations include an EIN application by default.",
            },
        },
        {
            "@type": "Question",
            "name": "Which state should I choose?",
            "acceptedAnswer": {
                "@type": "Answer",
                "text": "This page lists user quotes by state. The choice is made at the handoff for your use case; this page does not choose a state for you. A New York LLC is generally not suggested because of the publication step; ask about an INC, or another state.",
            },
        },
    ],
}

CSS_LINK = '<link href=/assets/css/quote-20261112.css rel=stylesheet>'
UX_LINK = '<link href=/assets/css/ux-20261112.css rel=stylesheet>'


def patch(src: str, article_inner: str, desc: str, faq: dict) -> str:
    html = src
    # CSS
    if "quote-20261112.css" not in html:
        if UX_LINK in html:
            html = html.replace(UX_LINK, UX_LINK + CSS_LINK, 1)
        else:
            html = html.replace("</head>", CSS_LINK + "</head>", 1)

    # Replace every occurrence of the previous page description (meta, og, twitter, JSON-LD).
    old_descs = [
        "出海第一步：先立主体。面向中小企业、个体户和源头工厂，介绍美国及英国、欧洲、加拿大、香港、新加坡、韩国、马来西亚、澳门的公司注册与常见配套。本站不报价、不代收、不上传证件。",
        "Step 1 of going overseas: set up a company so contracts, payments, customs, and a storefront have an entity that can sign. This page introduces the service. It does not quote figures or take payment.",
    ]
    for old in old_descs:
        html = html.replace(old, desc)

    faq_json = json.dumps(faq, ensure_ascii=False, separators=(",", ":"))
    html = re.sub(
        r'<script type=application/ld\+json>\{"@context":"https://schema.org","@type":"FAQPage".*?</script>',
        f'<script type=application/ld+json>{faq_json}</script>',
        html,
        count=1,
        flags=re.S,
    )

    new_article = "<article class=post-single>" + article_inner + "</article>"
    html2, n = re.subn(
        r"<article class=post-single>.*?</article>",
        new_article,
        html,
        count=1,
        flags=re.S,
    )
    if n != 1:
        raise SystemExit(f"article replace count={n}")
    # sanity: no leftover old copy
    for bad in ["本站不报价", "数字不写在这里", "does not quote figures", "Figures stay out of the page"]:
        if bad in html2:
            raise SystemExit(f"old copy remains: {bad}")
    # never leak supplier name or channel terms
    for bad in ["美司通", "普通代理价", "VIP价格", "预存10w", "预存10万", "建设银行", "汇丰", "OCBC", "大通", "花旗", "退全款"]:
        if bad in html2:
            raise SystemExit(f"forbidden term leaked: {bad}")
    return html2


def main():
    zh_src = Path("/tmp/overseas-company.html").read_text(encoding="utf-8")
    en_src = Path("/tmp/overseas-en.html").read_text(encoding="utf-8")
    zh_art = (ROOT / "article-zh.html").read_text(encoding="utf-8")
    en_art = (ROOT / "article-en.html").read_text(encoding="utf-8")

    zh = patch(zh_src, zh_art, DESC_ZH, FAQ_ZH)
    en = patch(en_src, en_art, DESC_EN, FAQ_EN)

    (OUT / "zh").mkdir(parents=True, exist_ok=True)
    (OUT / "en").mkdir(parents=True, exist_ok=True)
    (OUT / "zh" / "index.html").write_text(zh, encoding="utf-8")
    (OUT / "en" / "index.html").write_text(en, encoding="utf-8")
    print("wrote", OUT / "zh/index.html", len(zh))
    print("wrote", OUT / "en/index.html", len(en))
    print("zh has 2500 and 4500", "2500 元" in zh, "4500 元" in zh)
    print("zh has SGD/USD", "3200 新币" in zh, "5100 美元" in zh, "900 美元" in zh)
    print("en has RMB 2,500", "RMB 2,500" in en)
    print("css linked zh/en", "quote-20261112.css" in zh, "quote-20261112.css" in en)


if __name__ == "__main__":
    main()
