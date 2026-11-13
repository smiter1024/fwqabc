#!/usr/bin/env python3
"""Patch live-style overseas-company HTML with public user quotes. No channel prices."""
import json
import re
from pathlib import Path

ROOT = Path("/workspace/fwqabc-quotes")
OUT = ROOT / "out"

DESC_ZH = (
    "出海第一步是设立公司主体。本页公布海外公司注册及常见配套项目的用户报价，银行开户等项目可询价。"
)
DESC_EN = (
    "The first step in going overseas is to establish a company. This page publishes user quotes for overseas company registration and common related services. Bank accounts and certain other items are available on inquiry."
)

FAQ_ZH = {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    "mainEntity": [
        {
            "@type": "Question",
            "name": "资质和牌照由谁持有？",
            "acceptedAnswer": {
                "@type": "Answer",
                "text": "办理所需资质和牌照由承办供应商持有，并由其受理及办理。出海ABC提供对接服务，先行核对报价与需求。",
            },
        },
        {
            "@type": "Question",
            "name": "费用应支付给谁？",
            "acceptedAnswer": {
                "@type": "Answer",
                "text": "服务费用请直接支付予承办供应商。护照及身份证件须通过该供应商的正式渠道提交。本站不代收款项，亦不在网页收集或留存证件资料。",
            },
        },
        {
            "@type": "Question",
            "name": "为何部分项目未公布报价？",
            "acceptedAnswer": {
                "@type": "Answer",
                "text": "银行开户、暂停办理或需另行协商的项目，以及未列出的特殊主体，请通过电子邮件或微信询价。本页不对此类项目另行估算价格。",
            },
        },
        {
            "@type": "Question",
            "name": "是否需要本人前往当地？",
            "acceptedAnswer": {
                "@type": "Answer",
                "text": "咨询及材料提交均通过电子邮件或微信完成，注册本身不要求客户前往当地。部分地区另有身份核验要求，例如英国注册处的在线认证，将在确认方案时单独说明。",
            },
        },
        {
            "@type": "Question",
            "name": "没有 SSN 能否办理？",
            "acceptedAnswer": {
                "@type": "Answer",
                "text": "没有 SSN 亦可先行咨询。如已持有 SSN 或 ITIN，准备材料时可一并提供。美国各州注册的用户报价默认包含申请 EIN。",
            },
        },
        {
            "@type": "Question",
            "name": "应选择哪个州？",
            "acceptedAnswer": {
                "@type": "Answer",
                "text": "本页已列出各州用户报价。具体选择将根据实际用途在对接时确定，本页不代替客户作出选择。纽约州 LLC 因需办理登报，一般不作为首选，可咨询 INC 或其他州。",
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
                "text": "The fulfilling supplier holds the licences required for the filing and accepts and completes the work. 出海ABC provides coordination, beginning with a review of the quote and requirements.",
            },
        },
        {
            "@type": "Question",
            "name": "To whom should fees be paid?",
            "acceptedAnswer": {
                "@type": "Answer",
                "text": "Fees should be paid directly to the fulfilling supplier. Passports and identity documents must be submitted through the supplier’s official process. This site does not collect payment or retain identity documents on the page.",
            },
        },
        {
            "@type": "Question",
            "name": "Why do some items have no published quote?",
            "acceptedAnswer": {
                "@type": "Answer",
                "text": "Bank accounts, items that are suspended or subject to separate agreement, and special entities not listed here may be requested by email or WeChat. This page does not estimate a price for those items.",
            },
        },
        {
            "@type": "Question",
            "name": "Is travel required?",
            "acceptedAnswer": {
                "@type": "Answer",
                "text": "Inquiries and the submission of documents are completed by email or WeChat. Attendance in person is not required solely for registration. Some jurisdictions have a separate identity verification requirement, such as the UK registrar’s online verification, which will be explained when the plan is confirmed.",
            },
        },
        {
            "@type": "Question",
            "name": "Can a filing proceed without an SSN?",
            "acceptedAnswer": {
                "@type": "Answer",
                "text": "An inquiry may be made without an SSN. If an SSN or ITIN is already held, it should be included when documents are prepared. User quotes for US state registrations include an EIN application by default.",
            },
        },
        {
            "@type": "Question",
            "name": "Which state should be selected?",
            "acceptedAnswer": {
                "@type": "Answer",
                "text": "This page lists user quotes by state. The selection is confirmed according to the intended use when the plan is settled; this page does not make that choice on the client’s behalf. A New York LLC is generally not a first choice because of the publication requirement; an INC or another state may be discussed instead.",
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
        "出海第一步：先立主体。本页公布海外公司注册及常见配套的用户报价，银行开户等项目可询价。办理所需的完整资质和牌照由承办供应商持有；出海ABC负责获客，并把咨询交给供应商对接。本站不代收款项，也不在网页上收集证件。",
        "Step 1 of going overseas: set up a company. This page publishes user quotes for overseas company registration and common add-ons. Bank accounts and some other items are by inquiry. The licences and qualifications needed to file sit with the fulfilling supplier. 出海ABC only acquires customers and hands inquiries to that supplier. This site does not take payment or collect ID documents.",
        "出海第一步：先立主体。本页公布海外公司注册及常见配套的用户报价，银行开户等项目可询价。出海ABC负责咨询和对接，具体办理由具备相应资质和牌照的承办供应商完成。费用请直接付给该供应商，护照和证件通过供应商的正式渠道提交。本站不代收款项，也不在网页上留存证件资料。",
        "Step 1 of going overseas: set up a company. This page publishes user quotes for overseas company registration and common add-ons. Bank accounts and some other items are by inquiry. 出海ABC provides consultation and introduces you to the fulfilling supplier, who holds the required licences and completes the work. Please pay that supplier directly, and submit passports or identity documents through the supplier’s official process. This site does not collect payment or keep identity documents on the page.",
        "出海第一步：先立主体。本页公布海外公司注册及常见配套的用户报价，银行开户等项目可询价。出海ABC提供对接服务，先核对报价和需求，再由具备相应资质和牌照的承办供应商受理办理。费用请直接付给该供应商，护照和证件通过供应商的正式渠道提交。本站不代收款项，也不在网页上留存证件资料。",
        "Step 1 of going overseas: set up a company. This page publishes user quotes for overseas company registration and common add-ons. Bank accounts and some other items are by inquiry. 出海ABC provides the coordination: we review the quote and your needs first, then a licensed fulfilling supplier accepts and handles the filing. Please pay that supplier directly, and submit passports or identity documents through the supplier’s official process. This site does not collect payment or keep identity documents on the page.",
    
        '出海第一步是设立公司主体。本页公布海外公司注册及常见配套项目的用户报价，银行开户等项目可询价。出海ABC提供对接服务，先行核对报价与需求，再由具备相应资质和牌照的承办供应商受理办理。服务费用请直接支付予承办供应商。护照及身份证件须通过该供应商的正式渠道提交。本站不代收款项，亦不在网页收集或留存证件资料。',
        'The first step in going overseas is to establish a company. This page publishes user quotes for overseas company registration and common related services. Bank accounts and certain other items are available on inquiry. 出海ABC provides coordination: the quote and requirements are reviewed first, then a licensed fulfilling supplier accepts and completes the filing. Fees should be paid directly to that supplier, and passports or identity documents should be submitted through the supplier’s official process. This site does not collect payment or retain identity documents on the page.',]
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
