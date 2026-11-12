#!/usr/bin/env python3
"""Build ZH/EN public quote articles. Public prices only; never emit channel/VIP terms."""
from __future__ import annotations

import html
import re
from pathlib import Path

ROOT = Path("/workspace/fwqabc-quotes")

# Public user quotes only. currency: CNY / USD / SGD
# source: suggested = sheet 建议报价 as-is; hk_reg = user-set 4500 CNY;
# marked_up = 普通代理价 + 100/200 CNY or +50/100 USD or +200 SGD.

def e(s: str) -> str:
    return html.escape(s, quote=True)

def t_zh(s: str) -> str:
    if not s:
        return ""
    s = s.strip()
    s = s.replace("–", "-")
    s = re.sub(r"\s+", " ", s)
    s = s.replace("工作日", "")
    m = re.fullmatch(r"(\d+)\s*[-~到至]\s*(\d+)\s*(days?|天)", s, re.I)
    if m:
        return f"{m.group(1)}–{m.group(2)} 个工作日"
    m = re.fullmatch(r"(\d+)\s*[-~到至]\s*(\d+)\s*(周)", s)
    if m:
        return f"{m.group(1)}–{m.group(2)} 周"
    m = re.fullmatch(r"约?\s*(\d+)\s*周\s*左右", s)
    if m:
        return f"约 {m.group(1)} 周"
    m = re.fullmatch(r"(\d+)\s*[-~到至]\s*(\d+)\s*weeks?", s, re.I)
    if m:
        return f"{m.group(1)}–{m.group(2)} 周"
    if re.fullmatch(r"\d+\s*-?\s*\d*\s*days?", s, re.I):
        s2 = re.sub(r"(?i)days?", "个工作日", s.replace(" ", ""))
        s2 = s2.replace("-", "–")
        if "个工作日" not in s2:
            s2 += " 个工作日"
        return re.sub(r"(\d)个", r"\1 个", s2)
    s = s.replace("-", "–")
    return s

def t_en(s: str) -> str:
    if not s:
        return ""
    zh = t_zh(s)
    zh = zh.replace("个工作日", "business days").replace("约 ", "About ").replace(" 周", " weeks")
    zh = zh.replace("天", " days")
    return zh

def money_zh(amount, ccy: str, suffix: str = "") -> str:
    unit = {"CNY": "元", "USD": "美元", "SGD": "新币"}[ccy]
    if isinstance(amount, float) and amount.is_integer():
        amount = int(amount)
    body = f"{amount} {unit}"
    return body + suffix

def money_en(amount, ccy: str, suffix: str = "") -> str:
    unit = {"CNY": "RMB", "USD": "USD", "SGD": "SGD"}[ccy]
    if isinstance(amount, float) and amount.is_integer():
        amount = int(amount)
    body = f"{unit} {amount:,}"
    return body + suffix

def rewrite_note(s: str) -> str:
    if not s:
        return ""
    s = s.replace("非我们注册的公司", "非承办供应商注册的公司")
    s = s.replace("不是我们注册的", "非承办供应商注册的")
    s = s.replace("我们注册的公司", "由承办供应商注册的公司")
    s = s.replace("变更为我们的代理地址", "变更为承办供应商的代理地址")
    s = s.replace("我司代缴", "由承办供应商代缴")
    s = s.replace("我司", "承办供应商")
    s = s.replace("转入我司代理", "转入承办供应商代理")
    return s

# --- popular 11 remain as previously drafted (建议报价, CNY) ---

POPULAR_ZH = r'''<h2 id="用户报价">美国常用州用户报价<a hidden class="anchor" aria-hidden="true" href="#用户报价">#</a></h2>
<p class="quote-included">下列用户报价默认包含：注册、首年州政府费用、首年代理服务、联邦税号 EIN、代理地址 12 个月及政府信件代收与扫描，以及可在州政府核查的全套资料（默认以 PDF 交付）。如需纸质文件及公司印章，另计 200 元。报价不含良好证明；如需办理，请另行询价。</p>
<p class="quote-asof">本表金额以人民币计，供参考，以书面确认价格为准。</p>
<div class="quote-table-wrap">
<table class="quote-table">
<thead>
<tr><th>州</th><th>用户报价</th><th>参考时效</th><th>年审（参考）</th><th>说明</th></tr>
</thead>
<tbody>
<tr><td>科罗拉多 CO</td><td class="price">2500 元</td><td>1–3 个工作日</td><td class="fee">600 元</td><td class="note"></td></tr>
<tr><td>怀俄明 WY</td><td class="price">3500 元</td><td>1–3 个工作日</td><td class="fee">1000 元</td><td class="note">报价说明写明免州所得税，以官方为准。</td></tr>
<tr><td>蒙大拿 MT</td><td class="price">2500 元</td><td>5–7 个工作日</td><td class="fee">700 元</td><td class="note">报价说明写明每年特许税 50 美元，以官方为准。</td></tr>
<tr><td>加州 CA</td><td class="price">LLC 3500 元<br>INC 3800 元</td><td>5–10 个工作日</td><td class="fee">1000 元（需授权）</td><td class="note">含州政府初次年报；LLC 两年一审。报价说明写明每年 800 美元基本州税：INC 在财年第一季度前缴纳，LLC 在成立后第四个月的第 15 日前缴纳，以官方为准。</td></tr>
<tr><td>特拉华 DE</td><td class="price">3000 元</td><td>约 2 周</td><td class="fee">INC 1500 元（不含特许税）<br>LLC 3700 元（含特许税）</td><td class="note">报价说明写明每年特许税 INC 175 美元起、LLC 400 美元，以官方为准。</td></tr>
<tr><td>华盛顿 WA</td><td class="price">3800 元</td><td>3–5 个工作日</td><td class="fee">1100 元</td><td class="note">含州政府初次年报。</td></tr>
<tr><td>马萨诸塞 MA</td><td class="price">LLC 7500 元<br>INC 5500 元</td><td>3–5 个工作日</td><td class="fee">LLC 5200 元<br>INC 2000 元</td><td class="note"></td></tr>
<tr><td>新泽西 NJ</td><td class="price">3500 元</td><td>1–3 个工作日</td><td class="fee">1400 元</td><td class="note">报价说明写明每年基本州税 500 美元起，以官方为准。</td></tr>
<tr><td>内华达 NV</td><td class="price">INC 9800 元<br>LLC 7500 元</td><td>3–5 个工作日</td><td class="fee">LLC 4000 元<br>INC 6000 元</td><td class="note">含 business license。</td></tr>
<tr><td>佛罗里达 FL</td><td class="price">LLC 3500 元<br>INC 3000 元</td><td>5–10 个工作日</td><td class="fee">2100 元</td><td class="note"></td></tr>
<tr><td>纽约 NY</td><td class="price">INC 3000 元<br>LLC 3900 元<br>州外备案 INC 3900 元 / LLC 4200 元（约 4–6 周）</td><td>1–3 个工作日</td><td class="fee">1000 元</td><td class="note">报价说明写明每年特许税 25 美元起，以官方为准。纽约州 LLC 通常须办理登报，费用约 5000 元起，一般不作为首选，可咨询 INC 或其他州。</td></tr>
</tbody>
</table>
</div>
<h2 id="后续费用">上述各州后续费用<a hidden class="anchor" aria-hidden="true" href="#后续费用">#</a></h2>
<p class="quote-asof">以下为上述各州后续费用的参考金额，以人民币计，以书面确认为准。若转入承办供应商代理，费用为转入费与代理人续费之和。</p>
<div class="quote-table-wrap">
<table class="quote-table">
<thead>
<tr><th>州</th><th>变更</th><th>代理人续费</th><th>转入代理</th><th>注销</th><th>注销参考时效</th><th>良好证明</th></tr>
</thead>
<tbody>
<tr><td>科罗拉多</td><td class="fee">800 元</td><td class="fee">400 元</td><td class="fee">500 元</td><td class="fee">600 元</td><td>1–3 个工作日</td><td>免费</td></tr>
<tr><td>怀俄明</td><td class="fee">1500 元</td><td class="fee">400 元</td><td class="fee">600 元</td><td class="fee">1600 元</td><td>30 天</td><td>免费</td></tr>
<tr><td>蒙大拿</td><td class="fee">1200 元</td><td class="fee">400 元</td><td class="fee">500 元</td><td class="fee">500 元</td><td>7–10 个工作日</td><td></td></tr>
<tr><td>加州</td><td class="note">见下方说明</td><td class="fee">400 元</td><td class="fee">能授权 600 元<br>不能授权 1000 元</td><td class="fee">1400 元（需授权；无授权不能注销）</td><td>2–4 周</td><td></td></tr>
<tr><td>特拉华</td><td class="fee">3500 元</td><td class="fee">400 元</td><td class="fee">1000 元</td><td class="fee">3000 元（须结清含当年在内的特许税）</td><td>4–6 周</td><td></td></tr>
<tr><td>华盛顿</td><td class="fee">2500 元</td><td class="fee">400 元</td><td class="fee">500 元</td><td class="fee">1000 元（需税务结清证明）</td><td>5–7 个工作日</td><td></td></tr>
<tr><td>马萨诸塞</td><td class="fee">3000 元</td><td class="fee">400 元</td><td class="fee">500 元</td><td class="fee">1600 元（需税务结清证明）</td><td>10–20 个工作日</td><td></td></tr>
<tr><td>新泽西</td><td class="fee">1700 元</td><td class="fee">400 元</td><td class="fee">1000 元</td><td class="fee">1700 元</td><td>3–5 个工作日</td><td></td></tr>
<tr><td>内华达</td><td class="fee">1800 元</td><td class="fee">400 元</td><td class="fee">900 元</td><td class="fee">1500 元</td><td>1–3 个工作日</td><td></td></tr>
<tr><td>佛罗里达</td><td class="fee">2000 元</td><td class="fee">400 元</td><td class="fee">900 元</td><td class="fee">1000 元</td><td>1–3 个工作日</td><td></td></tr>
<tr><td>纽约</td><td class="fee">章程 2500 元<br>代理地址 1500 元</td><td class="fee">400 元</td><td class="fee">1200 元</td><td class="fee">1200 元；如需税务结清证明，2500 元</td><td>5–7 个工作日</td><td></td></tr>
</tbody>
</table>
</div>
<p class="quote-fn">加州变更（参考）：由承办供应商注册的公司，变更地址、法定代表人或经营范围 1000 元；章程变更（含股份数、公司名称、LLC 管理类型）2000 元；变更类型 2500 元。非由该供应商注册的公司，变更地址、法定代表人或经营范围 1000 元（须取得授权）；章程变更 2500 元；变更类型 3500 元。取消原授权 1000 元；现场变更地址 1500 元。</p>
<p class="quote-fn">纽约州变更的参考时效约为 2–4 周。部分注销如需完成税务清算，全部办结时间可能更长，以书面确认时的说明为准。</p>
'''

POPULAR_EN = r'''<h2 id="user-quotes">User quotes for commonly used US states<a hidden class="anchor" aria-hidden="true" href="#user-quotes">#</a></h2>
<p class="quote-included">Unless a row says otherwise, each user quote below includes formation, the first year’s state government fee, the first year’s registered-agent service, a federal EIN, a registered address for 12 months with scanning of government mail, and a full document set that can be checked with the state (PDF by default). Paper documents and a company seal for a US filing add RMB 200. A certificate of good standing is not included; it may be requested separately.</p>
<p class="quote-asof">Amounts in this table are in renminbi. They are a reference only and are confirmed in writing at the time of engagement.</p>
<div class="quote-table-wrap">
<table class="quote-table">
<thead>
<tr><th>State</th><th>User quote</th><th>Typical timing</th><th>Annual review (reference)</th><th>Notes</th></tr>
</thead>
<tbody>
<tr><td>Colorado CO</td><td class="price">RMB 2,500</td><td>1–3 business days</td><td class="fee">RMB 600</td><td class="note"></td></tr>
<tr><td>Wyoming WY</td><td class="price">RMB 3,500</td><td>1–3 business days</td><td class="fee">RMB 1,000</td><td class="note">The quote notes say there is no state income tax; official rules prevail.</td></tr>
<tr><td>Montana MT</td><td class="price">RMB 2,500</td><td>5–7 business days</td><td class="fee">RMB 700</td><td class="note">The quote notes say a franchise tax of USD 50 a year; official rules prevail.</td></tr>
<tr><td>California CA</td><td class="price">LLC RMB 3,500<br>INC RMB 3,800</td><td>5–10 business days</td><td class="fee">RMB 1,000 (authorization required)</td><td class="note">Includes the first state report; an LLC is reviewed every two years. The quote notes say an USD 800 annual state tax: an INC pays before the first quarter of the fiscal year, an LLC by the 15th day of the fourth month after formation. Official rules prevail.</td></tr>
<tr><td>Delaware DE</td><td class="price">RMB 3,000</td><td>About 2 weeks</td><td class="fee">INC RMB 1,500 (franchise tax not included)<br>LLC RMB 3,700 (franchise tax included)</td><td class="note">The quote notes say an annual franchise tax from USD 175 for an INC and USD 400 for an LLC. Official rules prevail.</td></tr>
<tr><td>Washington WA</td><td class="price">RMB 3,800</td><td>3–5 business days</td><td class="fee">RMB 1,100</td><td class="note">Includes the first state report.</td></tr>
<tr><td>Massachusetts MA</td><td class="price">LLC RMB 7,500<br>INC RMB 5,500</td><td>3–5 business days</td><td class="fee">LLC RMB 5,200<br>INC RMB 2,000</td><td class="note"></td></tr>
<tr><td>New Jersey NJ</td><td class="price">RMB 3,500</td><td>1–3 business days</td><td class="fee">RMB 1,400</td><td class="note">The quote notes say a state tax from USD 500 a year; official rules prevail.</td></tr>
<tr><td>Nevada NV</td><td class="price">INC RMB 9,800<br>LLC RMB 7,500</td><td>3–5 business days</td><td class="fee">LLC RMB 4,000<br>INC RMB 6,000</td><td class="note">Includes a business license.</td></tr>
<tr><td>Florida FL</td><td class="price">LLC RMB 3,500<br>INC RMB 3,000</td><td>5–10 business days</td><td class="fee">RMB 2,100</td><td class="note"></td></tr>
<tr><td>New York NY</td><td class="price">INC RMB 3,000<br>LLC RMB 3,900<br>Foreign qualification INC RMB 3,900 / LLC RMB 4,200 (about 4–6 weeks)</td><td>1–3 business days</td><td class="fee">RMB 1,000</td><td class="note">The quote notes say a franchise tax from USD 25 a year; official rules prevail. A New York LLC usually requires publication, from about RMB 5,000, and is generally not a first choice. An INC or another state may be discussed instead.</td></tr>
</tbody>
</table>
</div>
<h2 id="follow-on-fees">Follow-on fees for these states<a hidden class="anchor" aria-hidden="true" href="#follow-on-fees">#</a></h2>
<p class="quote-asof">Reference fees in renminbi for the states above, confirmed at the time of engagement. Transferring a registered agent to the fulfilling supplier is the transfer fee plus the agent renewal fee.</p>
<div class="quote-table-wrap">
<table class="quote-table">
<thead>
<tr><th>State</th><th>Change</th><th>Agent renewal</th><th>Agent transfer</th><th>Dissolution</th><th>Dissolution timing</th><th>Good standing</th></tr>
</thead>
<tbody>
<tr><td>Colorado</td><td class="fee">RMB 800</td><td class="fee">RMB 400</td><td class="fee">RMB 500</td><td class="fee">RMB 600</td><td>1–3 business days</td><td>Included</td></tr>
<tr><td>Wyoming</td><td class="fee">RMB 1,500</td><td class="fee">RMB 400</td><td class="fee">RMB 600</td><td class="fee">RMB 1,600</td><td>30 days</td><td>Included</td></tr>
<tr><td>Montana</td><td class="fee">RMB 1,200</td><td class="fee">RMB 400</td><td class="fee">RMB 500</td><td class="fee">RMB 500</td><td>7–10 business days</td><td></td></tr>
<tr><td>California</td><td class="note">See note below</td><td class="fee">RMB 400</td><td class="fee">With authorization RMB 600<br>Without RMB 1,000</td><td class="fee">RMB 1,400 (authorization required; cannot dissolve without it)</td><td>2–4 weeks</td><td></td></tr>
<tr><td>Delaware</td><td class="fee">RMB 3,500</td><td class="fee">RMB 400</td><td class="fee">RMB 1,000</td><td class="fee">RMB 3,000 (all franchise tax through the current year must be settled)</td><td>4–6 weeks</td><td></td></tr>
<tr><td>Washington</td><td class="fee">RMB 2,500</td><td class="fee">RMB 400</td><td class="fee">RMB 500</td><td class="fee">RMB 1,000 (tax clearance required)</td><td>5–7 business days</td><td></td></tr>
<tr><td>Massachusetts</td><td class="fee">RMB 3,000</td><td class="fee">RMB 400</td><td class="fee">RMB 500</td><td class="fee">RMB 1,600 (tax clearance required)</td><td>10–20 business days</td><td></td></tr>
<tr><td>New Jersey</td><td class="fee">RMB 1,700</td><td class="fee">RMB 400</td><td class="fee">RMB 1,000</td><td class="fee">RMB 1,700</td><td>3–5 business days</td><td></td></tr>
<tr><td>Nevada</td><td class="fee">RMB 1,800</td><td class="fee">RMB 400</td><td class="fee">RMB 900</td><td class="fee">RMB 1,500</td><td>1–3 business days</td><td></td></tr>
<tr><td>Florida</td><td class="fee">RMB 2,000</td><td class="fee">RMB 400</td><td class="fee">RMB 900</td><td class="fee">RMB 1,000</td><td>1–3 business days</td><td></td></tr>
<tr><td>New York</td><td class="fee">Articles RMB 2,500<br>Registered address RMB 1,500</td><td class="fee">RMB 400</td><td class="fee">RMB 1,200</td><td class="fee">RMB 1,200; tax clearance, if needed, RMB 2,500</td><td>5–7 business days</td><td></td></tr>
</tbody>
</table>
</div>
<p class="quote-fn">California changes (reference): for a company formed by the fulfilling supplier, a change of address, officer, or business scope is RMB 1,000; an articles change (shares, name, or LLC management type) is RMB 2,000; a type change is RMB 2,500. For a company not formed by that supplier, a change of address, officer, or business scope is RMB 1,000 (authorization required); an articles change is RMB 2,500; a type change is RMB 3,500. Cancelling a prior authorization is RMB 1,000; an in-person address change is RMB 1,500.</p>
<p class="quote-fn">New York changes typically take about 2–4 weeks. Some dissolutions that need tax clearance can take longer. The written confirmation is authoritative.</p>
'''


def row(place_zh, place_en, price_zh, price_en, time_zh, time_en, annual_zh, annual_en, note_zh="", note_en=""):
    return {
        "place_zh": place_zh, "place_en": place_en,
        "price_zh": price_zh, "price_en": price_en,
        "time_zh": time_zh, "time_en": time_en,
        "annual_zh": annual_zh, "annual_en": annual_en,
        "note_zh": note_zh, "note_en": note_en,
    }

# Other US states (marked up from 普通代理价, all CNY)
OTHER_US = [
    row("得克萨斯 TX", "Texas TX", "4200 元", "RMB 4,200", "3–5 个工作日", "3–5 business days",
        "可收信 1000 元<br>不可收信 2500 元", "Can receive mail RMB 1,000<br>Cannot receive mail RMB 2,500",
        "公司名通常无法提前检索，只能直接提交。州外备案参考 6800 元。",
        "The company name usually cannot be searched in advance and must be filed directly. Foreign qualification is about RMB 6,800 (reference)."),
    row("南达科他 SD", "South Dakota SD", "2300 元", "RMB 2,300", "1–3 个工作日", "1–3 business days", "1100 元", "RMB 1,100",
        "报价说明写明免州所得税，以官方为准。", "The quote notes say there is no state income tax; official rules prevail."),
    row("马里兰 MD", "Maryland MD", "2700 元", "RMB 2,700", "10–15 个工作日", "10–15 business days", "3000 元", "RMB 3,000"),
    row("佐治亚 GA", "Georgia GA", "INC 2600 元<br>LLC 2200 元<br>州外备案 INC 3600 元 / LLC 3200 元",
        "INC RMB 2,600<br>LLC RMB 2,200<br>Foreign qualification INC RMB 3,600 / LLC RMB 3,200",
        "5–10 个工作日", "5–10 business days", "1200 元", "RMB 1,200",
        "INC 通常需要登报，约 450 美元，以官方为准。", "An INC usually requires publication, about USD 450; official rules prevail."),
    row("北卡罗来纳 NC", "North Carolina NC", "2400 元", "RMB 2,400", "15–20 个工作日", "15–20 business days",
        "INC 1400 元<br>LLC 2200 元", "INC RMB 1,400<br>LLC RMB 2,200"),
    row("南卡罗来纳 SC", "South Carolina SC", "INC 3300 元<br>LLC 2400 元", "INC RMB 3,300<br>LLC RMB 2,400",
        "5–7 个工作日", "5–7 business days", "700 元", "RMB 700"),
    row("宾夕法尼亚 PA", "Pennsylvania PA", "2400 元", "RMB 2,400", "5–7 个工作日", "5–7 business days", "1000 元", "RMB 1,000",
        "INC 通常需要登报，约 500 美元，以官方为准。", "An INC usually requires publication, about USD 500; official rules prevail."),
    row("康涅狄格 CT", "Connecticut CT", "INC 4400 元<br>LLC 2300 元", "INC RMB 4,400<br>LLC RMB 2,300",
        "5–7 个工作日", "5–7 business days", "LLC 1300 元<br>INC 1800 元", "LLC RMB 1,300<br>INC RMB 1,800",
        "报价说明写明 LLC 须在 3 月 31 日前年审，INC 按周年年审，以官方为准。",
        "The quote notes say an LLC is reviewed by 31 March and an INC on its anniversary; official rules prevail."),
    row("明尼苏达 MN", "Minnesota MN", "2700 元", "RMB 2,700", "1–2 个工作日", "1–2 business days", "1000 元", "RMB 1,000"),
    row("新墨西哥 NM", "New Mexico NM", "INC 2200 元<br>LLC 1600 元", "INC RMB 2,200<br>LLC RMB 1,600",
        "7–10 个工作日", "7–10 business days", "800 元", "RMB 800"),
    row("爱荷华 IA", "Iowa IA", "1700 元", "RMB 1,700", "5–6 个工作日", "5–6 business days", "1000 元", "RMB 1,000"),
    row("阿拉斯加 AK", "Alaska AK", "3100 元", "RMB 3,100", "5–10 个工作日", "5–10 business days", "1600 元", "RMB 1,600"),
    row("亚拉巴马 AL", "Alabama AL", "3000 元", "RMB 3,000", "5–6 个工作日", "5–6 business days", "询价", "By inquiry"),
    row("阿肯色 AR", "Arkansas AR", "1600 元", "RMB 1,600", "5–6 个工作日", "5–6 business days",
        "LLC 1600 元<br>INC 2600 元起", "LLC RMB 1,600<br>INC from RMB 2,600"),
    row("亚利桑那 AZ", "Arizona AZ", "1900 元", "RMB 1,900", "5–10 个工作日", "5–10 business days", "1000 元", "RMB 1,000",
        "非承办供应商注册的公司需授权；无授权另加 100 美元。",
        "A company not formed by the fulfilling supplier needs authorization; without it, add USD 100."),
    row("哥伦比亚特区 DC", "District of Columbia DC", "2000 元", "RMB 2,000", "5–10 个工作日", "5–10 business days", "询价", "By inquiry"),
    row("夏威夷 HI", "Hawaii HI", "1600 元", "RMB 1,600", "5–6 个工作日", "5–6 business days", "1300 元", "RMB 1,300"),
    row("爱达荷 ID", "Idaho ID", "2000 元", "RMB 2,000", "10–15 个工作日", "10–15 business days", "询价", "By inquiry"),
    row("波多黎各 PR", "Puerto Rico PR", "INC 2300 元<br>LLC 3100 元", "INC RMB 2,300<br>LLC RMB 3,100",
        "10–15 个工作日", "10–15 business days", "询价", "By inquiry"),
    row("伊利诺伊 IL", "Illinois IL", "2400 元", "RMB 2,400", "10–20 个工作日", "10–20 business days", "2200 元", "RMB 2,200"),
    row("印第安纳 IN", "Indiana IN", "1900 元", "RMB 1,900", "10–15 个工作日", "10–15 business days", "1500 元", "RMB 1,500"),
    row("堪萨斯 KS", "Kansas KS", "INC 1900 元<br>LLC 2400 元", "INC RMB 1,900<br>LLC RMB 2,400",
        "5–6 个工作日", "5–6 business days", "询价", "By inquiry"),
    row("肯塔基 KY", "Kentucky KY", "INC 1600 元<br>LLC 1500 元<br>州外备案 1900 元",
        "INC RMB 1,600<br>LLC RMB 1,500<br>Foreign qualification RMB 1,900",
        "5–6 个工作日", "5–6 business days", "800 元", "RMB 800",
        "报价说明写明每年特许税 175 美元起，以官方为准。",
        "The quote notes say a franchise tax from USD 175 a year; official rules prevail."),
    row("路易斯安那 LA", "Louisiana LA", "INC 1800 元<br>LLC 2000 元", "INC RMB 1,800<br>LLC RMB 2,000",
        "5–6 个工作日", "5–6 business days", "1000 元", "RMB 1,000"),
    row("缅因 ME", "Maine ME", "INC 2600 元<br>LLC 2800 元", "INC RMB 2,600<br>LLC RMB 2,800",
        "约 15 个工作日", "About 15 business days", "询价", "By inquiry"),
    row("密歇根 MI", "Michigan MI", "INC 1700 元<br>LLC 1600 元", "INC RMB 1,700<br>LLC RMB 1,600",
        "5–7 个工作日", "5–7 business days", "800 元", "RMB 800",
        "非承办供应商注册的公司，年审另加 700 元。",
        "For a company not formed by the fulfilling supplier, add RMB 700 to the annual review."),
    row("密苏里 MO", "Missouri MO", "INC 1800 元<br>LLC 1500 元", "INC RMB 1,800<br>LLC RMB 1,500",
        "6–7 个工作日", "6–7 business days", "800 元", "RMB 800"),
    row("密西西比 MS", "Mississippi MS", "1600 元", "RMB 1,600", "5–6 个工作日", "5–6 business days", "800 元", "RMB 800"),
    row("内布拉斯加 NE", "Nebraska NE", "2000 元", "RMB 2,000", "5–6 个工作日", "5–6 business days", "询价", "By inquiry"),
    row("新罕布什尔 NH", "New Hampshire NH", "2000 元", "RMB 2,000", "10–15 个工作日", "10–15 business days", "1800 元", "RMB 1,800"),
    row("俄亥俄 OH", "Ohio OH", "2000 元", "RMB 2,000", "5–10 个工作日", "5–10 business days", "询价", "By inquiry"),
    row("俄克拉何马 OK", "Oklahoma OK", "INC 1600 元<br>LLC 2000 元", "INC RMB 1,600<br>LLC RMB 2,000",
        "6–7 个工作日", "6–7 business days", "800 元", "RMB 800"),
    row("俄勒冈 OR", "Oregon OR", "2000 元", "RMB 2,000", "5–6 个工作日", "5–6 business days", "1500 元", "RMB 1,500",
        "报价说明写明每年特许税 150 美元起，以官方为准。",
        "The quote notes say a franchise tax from USD 150 a year; official rules prevail."),
    row("罗德岛 RI", "Rhode Island RI", "INC 3000 元<br>LLC 2400 元", "INC RMB 3,000<br>LLC RMB 2,400",
        "6–7 个工作日", "6–7 business days", "询价", "By inquiry"),
    row("田纳西 TN", "Tennessee TN", "INC 2000 元<br>LLC 3500 元", "INC RMB 2,000<br>LLC RMB 3,500",
        "5–6 个工作日", "5–6 business days", "询价", "By inquiry"),
    row("犹他 UT", "Utah UT", "1300 元", "RMB 1,300", "10–15 个工作日", "10–15 business days", "1000 元", "RMB 1,000"),
    row("弗吉尼亚 VA", "Virginia VA", "INC 1800 元<br>LLC 2000 元", "INC RMB 1,800<br>LLC RMB 2,000",
        "7–8 个工作日", "7–8 business days", "1700 元", "RMB 1,700"),
    row("佛蒙特 VT", "Vermont VT", "2100 元", "RMB 2,100", "5–6 个工作日", "5–6 business days", "询价", "By inquiry"),
    row("威斯康星 WI", "Wisconsin WI", "INC 2000 元<br>LLC 2200 元", "INC RMB 2,000<br>LLC RMB 2,200",
        "5–6 个工作日", "5–6 business days", "1000 元", "RMB 1,000"),
    row("西弗吉尼亚 WV", "West Virginia WV", "2000 元", "RMB 2,000", "10–15 个工作日", "10–15 business days", "800 元", "RMB 800"),
    row("北达科他 ND", "North Dakota ND", "2200 元", "RMB 2,200", "10–15 个工作日", "10–15 business days", "1200 元", "RMB 1,200"),
]

PLACES = [
    row("香港公司注册", "Hong Kong company registration", "4500 元", "RMB 4,500", "3–5 个工作日", "3–5 business days", "—", "—",
        "用户报价为人民币，其中包含代缴的港币官费，官费以确认时为准。",
        "The user quote is in renminbi and includes official fees payable in Hong Kong dollars, confirmed at the time of engagement."),
    row("香港公司年审", "Hong Kong annual review", "3000 元", "RMB 3,000", "5–7 个工作日", "5–7 business days", "—", "—"),
    row("香港公司地址变更", "Hong Kong address change", "900 元", "RMB 900", "7–14 个工作日", "7–14 business days", "—", "—"),
    row("香港宽带", "Hong Kong broadband service", "4200 元", "RMB 4,200", "询价", "By inquiry", "地址续费参考 600 元/年", "Address renewal about RMB 600 a year (reference)"),
    row("香港分行", "Hong Kong branch", "1200 元", "RMB 1,200", "约 2 周", "About 2 weeks", "与总行一并年审", "Reviewed together with the head office"),
    row("香港独立地址租赁", "Hong Kong independent address", "4200 元", "RMB 4,200", "询价", "By inquiry", "—", "—",
        "该地址不支持实际办公。", "The address is not for actual office use."),
    row("英国", "United Kingdom", "1800 元", "RMB 1,800", "2–5 个工作日", "2–5 business days",
        "有授权码 1200 元；无授权码另加获取 1000 元", "With an authorization code RMB 1,200; without one, add RMB 1,000 to obtain it",
        "无授权码获取约需 1–2 个月，获取后注册地址会改为承办供应商的代理地址。地址续费参考 600 元；零申报参考 1500 元。",
        "Obtaining a code takes about 1–2 months, after which the registered address is changed to the fulfilling supplier’s agent address. Address renewal is about RMB 600; a nil return is about RMB 1,500."),
    row("法国", "France", "15000 元", "RMB 15,000", "6–8 周", "6–8 weeks",
        "地址维护 5000 元；零申报年审 6000 元；增值税申报一年 2800–4200 元",
        "Address maintenance RMB 5,000; nil-return annual review RMB 6,000; VAT filing RMB 2,800–4,200 a year"),
    row("罗马尼亚", "Romania", "15200 元", "RMB 15,200", "2–4 周", "2–4 weeks",
        "年审 3500 元；地址维护 7500 元；零申报报税 6000 元",
        "Annual review RMB 3,500; address maintenance RMB 7,500; nil-return tax filing RMB 6,000"),
    row("加拿大公司注册", "Canada company registration", "普通公司 11200 元<br>联邦公司 11200 元",
        "Provincial company RMB 11,200<br>Federal company RMB 11,200",
        "询价", "By inquiry",
        "联邦挂董 9200 元/年；地址挂靠 3200 元/年；BN 税号 6200 元；GST 税号 8200 元",
        "Federal nominee director RMB 9,200 a year; address service RMB 3,200 a year; BN number RMB 6,200; GST number RMB 8,200",
        "普通公司仅限安大略省、不列颠哥伦比亚省。", "The provincial company quote covers Ontario and British Columbia only."),
    row("韩国", "Korea", "12200 元", "RMB 12,200", "4–8 周", "4–8 weeks",
        "年审 3000 元起；地址续费 6000 元/年", "Annual review from RMB 3,000; address renewal RMB 6,000 a year",
        "后续记账报税、手机月租在报价说明中按韩币计，对接时确认，本页不折算。",
        "Bookkeeping and mobile-plan fees are quoted in Korean won in the source notes and are confirmed when the plan is settled; this page does not convert them."),
    row("新加坡公司注册", "Singapore company registration", "6700 元", "RMB 6,700", "1–2 周", "1–2 weeks",
        "年审 5000 元（含挂名董事、秘书、注册地址和零报税）",
        "Annual review RMB 5,000 (includes a nominee director, secretary, registered address, and a nil tax return)"),
    row("新加坡就业准证（EP）", "Singapore Employment Pass (EP)", "3200 新币", "SGD 3,200", "约 4 周", "About 4 weeks", "—", "—",
        "本项按新币报价，不折算人民币。", "This item is quoted in Singapore dollars and is not converted into renminbi."),
    row("马来西亚", "Malaysia", "8200 元", "RMB 8,200", "询价", "By inquiry",
        "周年报 4500 元；无运营申报 3800 元；有运营申报 6000 元起",
        "Annual return RMB 4,500; no-operation filing RMB 3,800; operating filing from RMB 6,000"),
    row("澳门", "Macau", "8200 元", "RMB 8,200", "询价", "By inquiry", "6000 元（含年审、地址、报税）", "RMB 6,000 (includes annual review, address, and tax filing)"),
]

ADDONS = [
    row("美国注册代理人（一年）", "US registered agent (one year)", "600 元", "RMB 600", "1–3 个工作日", "1–3 business days", "—", "—",
        "支持美国 50 个州。", "Available in all 50 US states."),
    row("普通独立地址租赁", "Standard independent address", "10 封信 700 元/年<br>25 封信 1400 元/年",
        "10 letters RMB 700 a year<br>25 letters RMB 1,400 a year",
        "1–3 个工作日", "1–3 business days", "—", "—",
        "可选州以确认时为准。", "Available states are confirmed at the time of engagement."),
    row("高级独立地址租赁", "Premium independent address", "租金 4300 美元/年<br>服务费 650 美元/年",
        "Rent USD 4,300 a year<br>Service USD 650 a year",
        "约 7 天", "About 7 days", "—", "—",
        "本项按美元报价。可选加州、特拉华、佛罗里达。", "Quoted in US dollars. Available in California, Delaware, and Florida."),
    row("ITIN", "ITIN", "600 元", "RMB 600", "8–15 周", "8–15 weeks", "—", "—", "免寄护照。", "Passport mailing is not required."),
    row("EIN（美国公司申请）", "EIN (US company)", "500 元", "RMB 500", "INC 1–3 个工作日；LLC 2–4 周", "INC 1–3 business days; LLC 2–4 weeks", "—", "—"),
    row("EIN（非美国公司申请）", "EIN (non-US company)", "700 元", "RMB 700", "2–4 周", "2–4 weeks", "—", "—"),
    row("年 BOND（5 万美元额度）", "Annual bond (USD 50,000 limit)", "900 美元", "USD 900", "7–10 个工作日", "7–10 business days", "—", "—",
        "本项按美元报价。不含 IOR 注册；如需办理，费用另加，以确认为准。",
        "Quoted in US dollars. An IOR registration is not included and may be requested separately."),
    row("GLN 码", "GLN code", "1000 元", "RMB 1,000", "3–5 个工作日", "3–5 business days", "—", "—", "长期有效 1 个。", "One code, long-term validity."),
    row("美国 MSB 金融牌照", "US MSB licence", "2200 元", "RMB 2,200", "10–15 个工作日", "10–15 business days", "—", "—"),
    row("加拿大 MSB 牌照", "Canada MSB licence", "5100 美元", "USD 5,100", "顺利约 4–5 个月，较慢约 10–12 个月",
        "About 4–5 months if straightforward; about 10–12 months if slower", "—", "—",
        "本项按美元报价。需用加拿大公司申请。审批结果以官方为准。",
        "Quoted in US dollars. A Canadian company is required. The official decision is what counts."),
    row("销售许可证申请", "Sales tax permit application", "2000 元", "RMB 2,000", "加州、科罗拉多、新泽西约 2–3 周，其他另询",
        "California, Colorado, and New Jersey about 2–3 weeks; others by inquiry", "—", "—",
        "华盛顿、康涅狄格、南卡罗来纳需另询。", "Washington, Connecticut, and South Carolina are by inquiry."),
    row("销售许可证地址变更", "Sales tax permit address change", "1700 元", "RMB 1,700", "询价", "By inquiry", "—", "—"),
    row("销售许可证注销", "Sales tax permit cancellation", "2000 元", "RMB 2,000", "询价", "By inquiry", "—", "—"),
    row("销售税申报（俄亥俄除外，按年）", "Sales tax filing (except Ohio, per year)",
        "月度 12 次 950 美元<br>季度 4 次 550 美元<br>半年 2 次 500 美元<br>年报 1 次 400 美元",
        "Monthly (12 filings) USD 950<br>Quarterly (4) USD 550<br>Semiannual (2) USD 500<br>Annual (1) USD 400",
        "—", "—", "—", "—", "本项按美元报价。", "Quoted in US dollars."),
    row("美国报税：零申报", "US tax filing: nil return", "1500 元", "RMB 1,500", "1–2 周", "1–2 weeks", "—", "—",
        "含联邦和州税申报服务费；部分州的固定州税另计。", "Covers the service fee for federal and state filing; a fixed state tax, where due, is extra."),
    row("美国报税：收入 25 万美元以内", "US tax filing: income up to USD 250,000", "2000 元", "RMB 2,000", "1–2 周", "1–2 weeks", "—", "—"),
    row("美国报税：收入 25 万至 100 万美元", "US tax filing: income USD 250,000–1,000,000", "2700 元", "RMB 2,700", "1–2 周", "1–2 weeks", "—", "—"),
    row("ODI 备案（新设代理）", "ODI filing (new setup, agent service)",
        "100 万美元以内 13200 元<br>100 万至 800 万美元 19200 元<br>800 万至 5000 万美元 39200 元<br>5000 万美元以上询价",
        "Up to USD 1 million: RMB 13,200<br>USD 1–8 million: RMB 19,200<br>USD 8–50 million: RMB 39,200<br>Above USD 50 million: by inquiry",
        "询价", "By inquiry", "—", "—",
        "档位按备案金额（美元）划分，服务费为人民币。", "Tiers are by filing amount in US dollars; the service fee is in renminbi."),
]


def table(rows, lang, cols):
    """cols: place, price, time, [annual], [note]"""
    if lang == "zh":
        headers = {"place": "项目" if "addon" in cols else ("州" if "us" in cols else "地区"),
                   "price": "用户报价", "time": "参考时效", "annual": "年审（参考）", "note": "说明"}
        if "addon" in cols:
            headers["place"] = "项目"
        pk, tk, ak, nk = "place_zh", "time_zh", "annual_zh", "note_zh"
        prk = "price_zh"
    else:
        headers = {"place": "Item" if "addon" in cols else ("State" if "us" in cols else "Place"),
                   "price": "User quote", "time": "Typical timing", "annual": "Annual review (reference)", "note": "Notes"}
        pk, tk, ak, nk = "place_en", "time_en", "annual_en", "note_en"
        prk = "price_en"
    show = ["place", "price", "time"]
    if "annual" in cols:
        show.append("annual")
    if "note" in cols:
        show.append("note")
    out = ['<div class="quote-table-wrap">', '<table class="quote-table">', "<thead>", "<tr>"]
    for c in show:
        out.append(f"<th>{headers[c]}</th>")
    out += ["</tr>", "</thead>", "<tbody>"]
    for r in rows:
        out.append("<tr>")
        out.append(f"<td>{r[pk]}</td>")
        out.append(f'<td class="price">{r[prk]}</td>')
        out.append(f"<td>{r[tk] or '—'}</td>")
        if "annual" in cols:
            val = r[ak]
            cls = "fee" if val and val not in ("—", "询价", "By inquiry") else ""
            out.append(f'<td class="{cls}">{val or "—"}</td>')
        if "note" in cols:
            out.append(f'<td class="note">{r[nk]}</td>')
        out.append("</tr>")
    out += ["</tbody>", "</table>", "</div>"]
    return "\n".join(out)


CTA_ZH = '''<div class="service-cta">
<p>邮箱：<a href="mailto:chuhaiABC@outlook.com?subject=%E5%92%A8%E8%AF%A2%E6%B5%B7%E5%A4%96%E5%85%AC%E5%8F%B8%E6%B3%A8%E5%86%8C">chuhaiABC@outlook.com</a></p>
<p><a class="service-cta-btn" href="mailto:chuhaiABC@outlook.com?subject=%E5%92%A8%E8%AF%A2%E6%B5%B7%E5%A4%96%E5%85%AC%E5%8F%B8%E6%B3%A8%E5%86%8C">发送邮件</a></p>
<p>微信：出海ABC（四川成都）。</p>
<p><img src=/images/contact/wechat.jpg alt="出海ABC 微信二维码" width=280 height=381></p>
</div>'''

CTA_EN = '''<div class="service-cta">
<p>Email: <a href="mailto:chuhaiABC@outlook.com?subject=Overseas%20company%20registration">chuhaiABC@outlook.com</a></p>
<p><a class="service-cta-btn" href="mailto:chuhaiABC@outlook.com?subject=Overseas%20company%20registration">Email</a></p>
<p>WeChat: 出海ABC (Chengdu, Sichuan).</p>
<p><img src=/images/contact/wechat.jpg alt="出海ABC WeChat QR code" width=280 height=381></p>
</div>'''

DESC_ZH = (
    "出海第一步是设立公司主体。本页公布海外公司注册及常见配套项目的用户报价，银行开户等项目可询价。"
)
DESC_EN = (
    "The first step in going overseas is to establish a company. This page publishes user quotes for overseas company registration and common related services. Bank accounts and certain other items are available on inquiry."
)


def build_zh() -> str:
    toc = '''<header class="post-header post-band"><nav class="breadcrumbs" role="navigation" aria-label="Breadcrumb"><a href=/>首页</a>
<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-chevron-right"><polyline points="9 18 15 12 9 6"/></svg>
<a href=/services/>出海服务</a>
<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-chevron-right"><polyline points="9 18 15 12 9 6"/></svg></nav><h1 class="post-title entry-hint-parent">海外公司注册</h1><div class="post-description">''' + DESC_ZH + '''</div><div class="post-meta"><span>语言:</span><ul class="i18n_list"><li><a href=https://fwqabc.com/en/services/overseas-company/>En</a></li></ul></div></header><details class="toc" open><summary accesskey=c title="(Alt + C)"><span class="title">目录</span></summary><div class="inner"><ul>
<li><a href="#用户报价" aria-label="美国常用州用户报价">美国常用州用户报价</a></li>
<li><a href="#后续费用" aria-label="上述各州后续费用">上述各州后续费用</a></li>
<li><a href="#美国其他州" aria-label="美国其他州用户报价">美国其他州用户报价</a></li>
<li><a href="#其他地区" aria-label="香港及其他地区">香港及其他地区</a></li>
<li><a href="#配套服务" aria-label="配套服务">配套服务</a></li>
<li><a href="#所需材料" aria-label="所需材料">所需材料</a></li>
<li><a href="#联系咨询" aria-label="联系咨询">联系咨询</a></li>
<li><a href="#报价说明" aria-label="报价说明">报价说明</a></li>
<li><a href="#常见问题" aria-label="常见问题">常见问题</a></li>
</ul></div></details><div class="post-content md-content">'''
    body = f'''<div class="role-notice">
<p>出海ABC提供海外公司注册对接服务：先行核对报价与需求，再由具备相应资质和牌照的承办供应商受理办理。本页公布用户报价，便于比较与核对。</p>
<p class="role-sub">服务费用请直接支付予承办供应商。护照及身份证件须通过该供应商的正式渠道提交。本站不代收款项，亦不在网页收集或留存证件资料。</p>
</div>
<p>中小企业、个体户、源头工厂及原厂在签署合同、收取货款、办理报关或设立经营网点前，一般需先完成公司主体设立。以下为用户报价，整理日期为 2026年11月12日。除另行标明美元或新加坡元外，金额以人民币计。如官费以美元、港币或韩元收取，本页保留原币种，不予折算。</p>
<p class="quote-disclaimer">本页报价可能因信息更新滞后或成本变动而与办理时不一致，解释以最新书面报价为准。</p>
<p>银行开户、暂停办理或需另行协商的项目，以及名称中含基金会、协会、联盟等字样的特殊主体，均需询价，本页不另行估算价格。具体开户安排以咨询时说明为准，本页不列示银行名称。</p>
{CTA_ZH}
{POPULAR_ZH}
<h2 id="美国其他州">美国其他州用户报价<a hidden class="anchor" aria-hidden="true" href="#美国其他州">#</a></h2>
<p class="quote-included">下列各州用户报价的默认包含范围，与上表美国常用州相同。金额以人民币计。年审费用为参考金额，以书面确认为准。如列有两个价格，依次为 INC、LLC。</p>
{table(OTHER_US, "zh", {"us", "annual", "note"})}
<h2 id="其他地区">香港及其他地区<a hidden class="anchor" aria-hidden="true" href="#其他地区">#</a></h2>
<p class="quote-included">香港公司注册的用户报价为 4500 元。新加坡就业准证以新加坡元计价。其余下列项目以人民币计价。年审等后续费用为参考金额，以书面确认为准。</p>
{table(PLACES, "zh", {"annual", "note"})}
<h2 id="配套服务">配套服务<a hidden class="anchor" aria-hidden="true" href="#配套服务">#</a></h2>
<p class="quote-included">表中已标明美元或新加坡元的项目，均按原币种计价，不折算为人民币。对公或个人银行开户均需询价；部分渠道可能暂停，以咨询时说明为准。本页不列示银行名称。</p>
{table(ADDONS, "zh", {"addon", "annual", "note"})}
<p>美国税务申报中，收入超过 100 万美元的项目请询价。</p>
<h2 id="所需材料">所需材料<a hidden class="anchor" aria-hidden="true" href="#所需材料">#</a></h2>
<p>本站不通过网页收取文件。下列为美国公司注册通常所需材料，供提前准备；其他地区所需材料以书面确认为准。</p>
<ul>
<li>拟定英文公司名称（亦可由承办供应商协助提供备选名称）</li>
<li>有效证件照片，例如护照、身份证或驾照</li>
<li>证件上的地址</li>
<li>电话和邮箱</li>
<li>如已持有 SSN 或 ITIN，请一并准备</li>
</ul>
<h2 id="联系咨询">联系咨询<a hidden class="anchor" aria-hidden="true" href="#联系咨询">#</a></h2>
{CTA_ZH}
<h2 id="报价说明">报价说明<a hidden class="anchor" aria-hidden="true" href="#报价说明">#</a></h2>
<ul>
<li>本页报价可能因信息更新滞后或成本变动而与办理时不一致，解释以最新书面报价为准。</li>
<li>因国际汇率及各国政策调整，公证、认证等费用同样以书面确认为准。</li>
<li>各项目的办理流程及所需资料，以实际需求及书面确认为准。</li>
<li>所列办理时效按加急及工作日估算，仅供参考，实际取决于官方审查进度，本页不对时效作出承诺。</li>
<li>所列价格不含税点；如需开具发票，税费另行计算。美国及英国文件默认以 PDF 交付；如需纸质文件及公司印章，另计 200 元。</li>
<li>最终解释以书面确认为准。</li>
</ul>
<h2 id="常见问题">常见问题<a hidden class="anchor" aria-hidden="true" href="#常见问题">#</a></h2>
<div class="faq">
<details open><summary>Q：资质和牌照由谁持有？</summary><p>A：办理所需资质和牌照由承办供应商持有，并由其受理及办理。出海ABC提供对接服务，先行核对报价与需求。</p></details>
<details open><summary>Q：费用应支付给谁？</summary><p>A：服务费用请直接支付予承办供应商。护照及身份证件须通过该供应商的正式渠道提交。本站不代收款项，亦不在网页收集或留存证件资料。</p></details>
<details open><summary>Q：为何部分项目未公布报价？</summary><p>A：银行开户、暂停办理或需另行协商的项目，以及未列出的特殊主体，请通过电子邮件或微信询价。本页不对此类项目另行估算价格。</p></details>
<details open><summary>Q：是否需要本人前往当地？</summary><p>A：咨询及材料提交均通过电子邮件或微信完成，注册本身不要求客户前往当地。部分地区另有身份核验要求，例如英国注册处的在线认证，将在确认方案时单独说明。</p></details>
<details open><summary>Q：没有 SSN 能否办理？</summary><p>A：没有 SSN 亦可先行咨询。如已持有 SSN 或 ITIN，准备材料时可一并提供。美国各州注册的用户报价默认包含申请 EIN。</p></details>
<details open><summary>Q：应选择哪个州？</summary><p>A：本页已列出各州用户报价。具体选择将根据实际用途在对接时确定，本页不代替客户作出选择。纽约州 LLC 因需办理登报，一般不作为首选，可咨询 INC 或其他州。</p></details>
<details open><summary>Q：报价采用何种货币？</summary><p>A：除标明美元或新加坡元的项目外，均为人民币。官费如以美元、港币或韩元收取，本页保留原币种，以书面确认为准。</p></details>
</div>
<p>本页含推广说明，详见 <a href=/disclosure/>推广披露</a>。</p>
</div>'''
    return toc + body


def build_en() -> str:
    toc = '''<header class="post-header post-band"><nav class="breadcrumbs" role="navigation" aria-label="Breadcrumb"><a href=/en/>Home</a>
<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-chevron-right"><polyline points="9 18 15 12 9 6"/></svg>
<a href=/en/services/>Services</a>
<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-chevron-right"><polyline points="9 18 15 12 9 6"/></svg></nav><h1 class="post-title entry-hint-parent">Overseas company registration</h1><div class="post-description">''' + DESC_EN + '''</div><div class="post-meta"><span>Translations:</span><ul class="i18n_list"><li><a href=https://fwqabc.com/services/overseas-company/>Zh-Cn</a></li></ul></div></header><details class="toc" open><summary accesskey=c title="(Alt + C)"><span class="title">Table of Contents</span></summary><div class="inner"><ul>
<li><a href="#user-quotes" aria-label="User quotes for commonly used US states">User quotes for commonly used US states</a></li>
<li><a href="#follow-on-fees" aria-label="Follow-on fees for these states">Follow-on fees for these states</a></li>
<li><a href="#other-us-states" aria-label="User quotes for other US states">User quotes for other US states</a></li>
<li><a href="#other-places" aria-label="Hong Kong and other places">Hong Kong and other places</a></li>
<li><a href="#add-ons" aria-label="Add-on services">Add-on services</a></li>
<li><a href="#documents" aria-label="Required documents">Required documents</a></li>
<li><a href="#contact" aria-label="Contact">Contact</a></li>
<li><a href="#quote-notes" aria-label="Quote notes">Quote notes</a></li>
<li><a href="#questions" aria-label="Questions">Questions</a></li>
</ul></div></details><div class="post-content md-content">'''
    body = f'''<div class="role-notice">
<p>出海ABC provides a coordination service for overseas company registration. The quote and requirements are reviewed first; a licensed fulfilling supplier then accepts and completes the filing. User quotes are published on this page for comparison and verification.</p>
<p class="role-sub">Fees should be paid directly to that supplier. Passports and identity documents must be submitted through the supplier’s official process. This site does not collect payment, and does not retain identity documents on the page.</p>
</div>
<p>Small and medium-sized enterprises, sole proprietors, and source manufacturers generally need to establish a company before entering into contracts, receiving payment, completing customs formalities, or opening a place of business. The figures below are user quotes, compiled on 12 November 2026. Amounts are in renminbi unless a row is marked in US dollars or Singapore dollars. Official fees charged in US dollars, Hong Kong dollars, or Korean won remain in that currency and are not converted on this page.</p>
<p class="quote-disclaimer">Quotes on this page may differ from the price at the time of filing because of delayed updates or changes in cost. The latest written quote is authoritative.</p>
<p>Bank accounts, items that are suspended or subject to separate agreement, and special entities whose names include words such as foundation, association, or alliance, are available on inquiry. This page does not estimate a price for those items. Bank names are not listed; available arrangements are confirmed at the time of inquiry.</p>
{CTA_EN}
{POPULAR_EN}
<h2 id="other-us-states">User quotes for other US states<a hidden class="anchor" aria-hidden="true" href="#other-us-states">#</a></h2>
<p class="quote-included">The default scope of the user quotes for the states below is the same as for the commonly used US states above. Amounts are in renminbi. Annual-review figures are provided for reference and are confirmed in writing. Where two prices are listed, they appear in the order INC, LLC.</p>
{table(OTHER_US, "en", {"us", "annual", "note"})}
<h2 id="other-places">Hong Kong and other places<a hidden class="anchor" aria-hidden="true" href="#other-places">#</a></h2>
<p class="quote-included">The user quote for Hong Kong company registration is RMB 4,500. The Singapore Employment Pass is priced in Singapore dollars. Other items below are in renminbi. Annual and follow-on figures are provided for reference and are confirmed in writing.</p>
{table(PLACES, "en", {"annual", "note"})}
<h2 id="add-ons">Add-on services<a hidden class="anchor" aria-hidden="true" href="#add-ons">#</a></h2>
<p class="quote-included">Items denominated in US dollars or Singapore dollars are labelled as such and are not converted into renminbi. Business or personal bank accounts are available on inquiry; some channels may be suspended, and the position is confirmed at the time of inquiry. Bank names are not listed on this page.</p>
{table(ADDONS, "en", {"addon", "annual", "note"})}
<p>US tax filings for income above USD 1 million are available on inquiry.</p>
<h2 id="documents">Required documents<a hidden class="anchor" aria-hidden="true" href="#documents">#</a></h2>
<p>This site does not collect documents through the web page. The list below sets out materials typically required for a US company registration, for advance preparation. Materials for other jurisdictions are confirmed in writing.</p>
<ul>
<li>A proposed English company name (the fulfilling supplier may also provide alternatives)</li>
<li>A photo of a valid ID, such as a passport, national ID card, or driver licence</li>
<li>The address on that ID</li>
<li>A phone number and email address</li>
<li>An SSN or ITIN, if already held</li>
</ul>
<h2 id="contact">Contact<a hidden class="anchor" aria-hidden="true" href="#contact">#</a></h2>
{CTA_EN}
<h2 id="quote-notes">Quote notes<a hidden class="anchor" aria-hidden="true" href="#quote-notes">#</a></h2>
<ul>
<li>Quotes on this page may differ from the price at the time of filing because of delayed updates or changes in cost. The latest written quote is authoritative.</li>
<li>Legalization and similar fees may also change with exchange rates and official rules, and are confirmed in writing.</li>
<li>Procedures and required documents follow the actual case and the written confirmation.</li>
<li>The indicated timelines assume an expedited, business-day path and are for reference only. Actual timing depends on official review, and no timeline is promised.</li>
<li>The listed prices exclude any tax point; if an invoice is required, tax is calculated separately. Documents for the United States and the United Kingdom are delivered as PDF by default; paper documents and a company seal are an additional RMB 200.</li>
<li>The written confirmation is authoritative.</li>
</ul>
<h2 id="questions">Questions<a hidden class="anchor" aria-hidden="true" href="#questions">#</a></h2>
<div class="faq">
<details open><summary>Q: Who holds the licences and qualifications?</summary><p>A: The fulfilling supplier holds the licences required for the filing and accepts and completes the work. 出海ABC provides coordination, beginning with a review of the quote and requirements.</p></details>
<details open><summary>Q: To whom should fees be paid?</summary><p>A: Fees should be paid directly to the fulfilling supplier. Passports and identity documents must be submitted through the supplier’s official process. This site does not collect payment or retain identity documents on the page.</p></details>
<details open><summary>Q: Why do some items have no published quote?</summary><p>A: Bank accounts, items that are suspended or subject to separate agreement, and special entities not listed here may be requested by email or WeChat. This page does not estimate a price for those items.</p></details>
<details open><summary>Q: Is travel required?</summary><p>A: Inquiries and the submission of documents are completed by email or WeChat. Attendance in person is not required solely for registration. Some jurisdictions have a separate identity verification requirement, such as the UK registrar’s online verification, which will be explained when the plan is confirmed.</p></details>
<details open><summary>Q: Can a filing proceed without an SSN?</summary><p>A: An inquiry may be made without an SSN. If an SSN or ITIN is already held, it should be included when documents are prepared. User quotes for US state registrations include an EIN application by default.</p></details>
<details open><summary>Q: Which state should be selected?</summary><p>A: This page lists user quotes by state. The selection is confirmed according to the intended use when the plan is settled; this page does not make that choice on the client’s behalf. A New York LLC is generally not a first choice because of the publication requirement; an INC or another state may be discussed instead.</p></details>
<details open><summary>Q: In which currency are the quotes stated?</summary><p>A: Amounts are in renminbi unless a row is marked in US dollars or Singapore dollars. Official fees charged in US dollars, Hong Kong dollars, or Korean won remain in that currency and are confirmed in writing.</p></details>
</div>
<p>This page includes an affiliate disclosure. See the <a href=/en/disclosure/>disclosure statement</a>.</p>
</div>'''
    return toc + body


def main():
    zh = build_zh()
    en = build_en()
    (ROOT / "article-zh.html").write_text(zh, encoding="utf-8")
    (ROOT / "article-en.html").write_text(en, encoding="utf-8")
    print("wrote articles", len(zh), len(en))


if __name__ == "__main__":
    main()
