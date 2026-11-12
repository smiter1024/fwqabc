# 出海独立站怎么选服务器（内容专题草稿）

本目录是可手术式插入线上静态站的完整 HTML 草稿，**尚未发布**。生成过程没有部署、没有 SSH、没有改生产环境、没有 git push，也没有覆盖 `/workspace/fwqabc`。

建议上线路径：把各篇 `index.html` 拷到线上站点对应的 `knowledge/<slug>/` 目录，再按下文更新知识库首页、`sitemap-knowledge.xml` 和 `llms.txt`。需要重新生成时，可在本目录运行 `python3 _gen.py`（依赖已抓取的线上模板 `/tmp/fwqabc-live/knowledge_cn2-gia.html`）。

页眉、页脚、主导航、样式和页脚脚本均按 2026-11-12 线上知识页模板复制，包含：导航「优惠与文章」「关于本站」、`/assets/css/ux-20261112.css`。知识页模板本身不含 `servers-filter.js`，故草稿也未加入。语言为 `zh-CN`。本轮不写英文版，因此：

- `hreflang` 只有 `zh-CN` 和 `x-default`，都指向中文 URL；
- 顶栏 English 按钮指向 `https://fwqabc.com/en/`（英文首页），**没有**虚构 `/en/knowledge/...` 地址。

拟定网址与线上现有页面没有冲突：2026-11-12 抓取时，下列五个地址均返回 404。已有知识页仍是 `/knowledge/`、`/knowledge/cn2-gia/`、`/knowledge/as9929/`、`/knowledge/cmin2/`。

## 文件与篇目

| 文件 | 标题 | 拟定 URL | 约计篇幅 |
| --- | --- | --- | --- |
| `knowledge/chuhai-independent-site-server/index.html` | 出海独立站怎么选服务器 | https://fwqabc.com/knowledge/chuhai-independent-site-server/ | 约 2800 字，约 7 分钟阅读（枢纽页） |
| `knowledge/domestic-visitors-cn2/index.html` | 国内访客为主，独立站该不该上 CN2 | https://fwqabc.com/knowledge/domestic-visitors-cn2/ | 约 2100 字，约 5 分钟 |
| `knowledge/overseas-visitors-server/index.html` | 独立站访客主要在海外时，服务器怎么选 | https://fwqabc.com/knowledge/overseas-visitors-server/ | 约 2300 字，约 6 分钟 |
| `knowledge/premium-line-when/index.html` | 独立站要不要上精品线路 | https://fwqabc.com/knowledge/premium-line-when/ | 约 3100 字，约 8 分钟 |
| `knowledge/monthly-vs-yearly-vps/index.html` | 独立站服务器年付和月付差多少，续费会不会更贵 | https://fwqabc.com/knowledge/monthly-vs-yearly-vps/ | 约 3500 字，约 9 分钟 |

篇幅按正文 + 常见问题的去空白字符估算，并据此填写页内「约 N 分钟阅读」和 BlogPosting `wordCount`。结构均为：先说结论 → 对照表 → 注意事项 → 常见问题；含 FAQPage、BreadcrumbList、BlogPosting JSON-LD；文首有可见「核对日期：2026-11-12（北京时间）」。

另附插入用片段（不是完整页面）：

- `snippets/knowledge-index-cards.html`：知识库首页筛选按钮和卡片分组
- `snippets/sitemap-knowledge-urls.xml`：五条 `<url>` 片段
- `snippets/llms.txt.fragment`：`llms.txt` 可追加的专题条目
- `snippets/stats.json`：生成时的篇目统计
- `_gen.py`：从线上模板组装上述 HTML 的脚本

## 上线前需要改的导航、索引、站点地图

这些都还没改，需要发布时再动生产文件：

1. **知识库首页** `https://fwqabc.com/knowledge/`
   - 在筛选行增加按钮：`data-knowledge-filter="independent-site"`，文案「独立站选型」。
   - 在 `#knowledge-list` 增加 `data-knowledge-group="independent-site"` 分组，卡片见 `snippets/knowledge-index-cards.html`。
   - 现有 `/js/knowledge-filter.js` 已按该属性过滤，**不必改脚本**。
   - 建议改页头说明：当前文案是「用本站已经写过的线路说明，整理成先看结论……这里不另写一套」。本组是完整专题，不是线路页的缩写，说明需要改写，避免和事实不符。
2. **站点地图**
   - 把 `snippets/sitemap-knowledge-urls.xml` 追加进 `https://fwqabc.com/sitemap-knowledge.xml`。
   - 更新该文件后，再在 Google Search Console / Bing Webmaster 提交 `https://fwqabc.com/sitemap.xml`（根地图会指向 `sitemap-knowledge.xml`）。
   - 本轮不要往 `en/sitemap-knowledge.xml` 加并不存在的英文 URL。
3. **`llms.txt`**
   - 在「核心页面」或「近期文章」下追加 `snippets/llms.txt.fragment`。枢纽页发布后应优先列入核心页面。
4. **互链（发布后再做，草稿里只写了正向链接）**
   - 首页出海成本地图 `#map` 中，「服务器与网络」卡片目前指向 `/servers/`。「建站与独立站」目前没有链接。发布后可把「服务器与网络」或「建站与独立站」指到枢纽页，或同时保留比价入口。
   - `/services/` 目前只介绍海外公司注册，没有服务器选型入口；若要相互引流，可在服务页加一句指向枢纽页，但不是上线硬条件。
   - 既有线路短页 `/knowledge/cn2-gia/` 等，可在文末加指向本组专题的链接。
   - 顶栏「优惠与文章」下拉里没有单独的「独立站选型」项；知识库链接已能进入本组，不是必须改导航。
5. **英文站**：本轮不提供译文。若以后补英文，再加 `/en/knowledge/...` 并改 `hreflang` 与顶栏 English 按钮。

## 封面图（全部复用已发布图片，没有新造图）

线上知识页和长文的 `og:image` 一律是 `https://fwqabc.com/brand/og-default-1200x630.jpg`，本组草稿同样如此，没有虚构新的 OG 图。

正文配图：

| 篇目 | 复用的线上路径 | 说明 |
| --- | --- | --- |
| 枢纽页 | `/img/cases/rfkey-2026-11/cover.webp`（800×500） | 已发布案例封面：RF-KEY射频元器件商城中文首页，美国加州 VPS 冷加载。首页和案例页已经在用。图注写明来源和测试时间 2026-11-02，不是为本专题新截。 |
| 海外访客篇 | `/img/cases/rfkey-2026-11/home-zh-desktop.webp`（1440×1000） | 同一案例的桌面冷加载截图，已在案例正文使用。 |
| 精品线路篇、年付月付篇 | `/img/promos/bandwagonhost-cn2-gia-e.webp`（640×400） | 搬瓦工官网购物车截图，已在方案对比文使用，图注保留**截于 2026-11-01**。本文没有重截，价格以官网当前结算页为准。 |
| 国内访客 / CN2 篇 | 无正文配图 | 站点没有可用的官方 CN2 / AS4809 说明页截图。不编造。若以后要配图，应新截 [IPinfo AS4809](https://ipinfo.io/AS4809) 或 [PeeringDB net/7941](https://www.peeringdb.com/net/7941)，或商家结算页上写明 CN2 GIA 的官方页面，并注明截图日期。 |

## 推广链接

只有年付月付篇含 `/go/bandwagonhost/`（指向搬瓦工 CN2 GIA-E 相关官方订购，按钮文案为「去官网核对并下单」，并标明「含推广」，`rel="sponsored nofollow noopener"`，文末有推广披露）。其余四篇只链到本站指南、工具、线路页和 RF-KEY 案例，文末没有「本文含推广链接」。引用本站优惠文章时，保留那篇文章自己的核对日期，不把活动写成今天仍有效。

## 已核对的官方事实（2026-11-12）

访问时间均为 **Asia/Taipei（UTC+8，即北京时间）**。

### 自治系统公开登记（约 15:02）

均 HTTP 200。

| AS | IPinfo | PeeringDB API | 当日读到的名称 |
| --- | --- | --- | --- |
| AS4809 | https://ipinfo.io/AS4809 | https://www.peeringdb.com/api/net?asn=4809 （公开页 https://www.peeringdb.com/net/7941） | IPinfo：China Telecom Next Generation Carrier Network / CHINATELECOM-CORE-WAN-CN2；PeeringDB：China Telecom / CN2 |
| AS9929 | https://ipinfo.io/AS9929 | https://www.peeringdb.com/api/net?asn=9929 （公开页 https://www.peeringdb.com/net/19957） | CHINA UNICOM Industrial Internet Backbone / China Unicom Industrial Internet Backbone |
| AS58807 | https://ipinfo.io/AS58807 | https://www.peeringdb.com/api/net?asn=58807 （公开页 https://www.peeringdb.com/net/22581） | IPinfo：China Mobile International Limited；PeeringDB：China Mobile International - NII，又称 CMIN2 |
| AS10099 | https://ipinfo.io/AS10099 | https://www.peeringdb.com/api/net?asn=10099 （公开页 https://www.peeringdb.com/net/7268） | China Unicom Global |

以上与本站线路页已有表述相符。AS9929 与 AS10099 在登记里是两个网络；草稿写明：本站线路页把搬瓦工标注的 Unicom Premium AS10099 写成常说的 9929/10099 精品网，但没有路径实测前，不把两个 AS 号直接写成同一条线。PeeringDB 公开 HTML 页本身未再单独抓取，名称来自同日 API。

### 搬瓦工公开目录与条款（约 15:02–15:04）

- 目录：https://bandwagonhost.com/order/catalog.json （官网首页 “Plans, prices & availability (JSON)”，`www` 与非 www 内容一致，HTTP 200）。目录自述：价格是整个付款周期的美元美分，不是折算月费；下单前库存和价格可能变化。
- 条款：https://bandwagonhost.com/terms-of-service.php （HTTP 200）。可在账单门户取消续费；30 天退款只适用于新购（not a renewal）、下单 30 天内。
- E-Commerce+SLA 产品说明将 USA-China routing 写为：China Telecom CN2 GIA/CTGNet AS4809/AS23764、China Unicom Premium AS10099、China Mobile CMIN2 AS58807。这是官方文字，不是本站实测。
- 文中举例的目录标价（2026-11-12 核对，与本站 2026-11-01 方案整理中对应档位一致，不保证之后不变）：
  - Basic 4 核 / 4 GB（pid 46）：$19.99/月，$199.99/年（年付比月付×12 约低 16.6%）
  - CN2 GIA-E 3 核 / 2 GB（pid 88）：无月付，$89.99/季，$299.99/年（年付比季付×4 约低 16.7%）
  - CN2 GIA-E 4 核 / 4 GB（pid 89）：$56.99/月，$549.99/年（约低 19.6%）
  - 大阪 CN2 GIA 2 核 / 2 GB（pid 134，JPOS_6）与新加坡同档（pid 173，SG_8）：$49.99/月，$499.99/年（约低 16.7%）
  - 香港同档（pid 95，HK_8）：$89.99/月，$899.99/年（约低 16.7%）
- 目录没有单独的续费价字段。条款也没有写续费会自动高于首期。因此文中的结论是：差额来自付款周期标价；续费是不是同一档，要再看结算页；首期优惠或秒杀到期后的价格，本文不填未核对的数字。

### 本站已有页面（约 14:59–15:00 抓取，作为引用，不是今天重核商家活动）

- 线路页：`/routes/cn2-gia/`、`/routes/9929/`、`/routes/cmin2/` 及对应知识短页
- 工具：`/tools/server-sizing/`（CMS 起步假设 1 vCPU / 2048 MB 等）、`/tools/network-lines/`（目录目前有 CN2 GIA 标注，没有把套餐标成 AS9929 或 CMIN2）
- 案例：`/cases/rfkey-overseas-check-2026-11/`（测试时间 2026-11-02；只引用已发布结论，未写出源站 IP、后台地址、账号或商品价格库存）
- 优惠/赠金文仅作交叉引用，并保留原文核对日期（多为 2026-11-01），不宣称今天活动仍在进行
- 首页成本地图、关于、披露、服务页：用于互链说明和措辞边界

`https://bandwagonhost.com/vps-hosting` 无扩展名时返回 404；正确列表页是 `https://bandwagonhost.com/vps-hosting.php`。价格以 JSON 目录和结算页为准。

## 未能核实、因而没有下结论的事项

- **没有为本组做新的自购性能测试**，因此各篇都不写新的延迟、丢包或“会更快多少”。
- **未在今天重核** RakSmart、双 11 汇总或其他商家的活动是否仍有效，也没有把那些价格抄进本组。
- 搬瓦工条款和公开目录都**没有**提供“续费自动涨价”的依据，所以没有写成续费一定更贵。
- https://cmi.chinamobile.com/ （PeeringDB 为 AS58807 填写的网站）在 15:02 左右 TLS 握手失败，**未核到该站内容**，正文没有引用它。
- 未逐页打开 PeeringDB 的 HTML 网络页，名称以 API 为准。
- 未核对其它商家（Vultr、RackNerd、CloudCone 等）的年付/月付差额，故 16%–20% 只限于当日搬瓦工目录里列出的方案。
- 未新截任何官方页面；CN2 篇因此没有正文配图。
- 搜索控制台验证状态不在本组范围内；发布站点地图仍需账号侧提交。

## 编辑边界（草稿已遵守）

- 不用「最佳 / 第一 / 最低成本 / 最高质量 / 翻墙」，也不在每篇堆叠站点口号或信任原则标签墙。
- 没有核实不下结论；没有自购实测不下性能结论。
- 客户案例一律写全称「RF-KEY射频元器件商城」。
- 排序按适合场景，不按佣金。
