# 🛡️ Block-ads (CLQ_Shield 中国境内纯净去广告规则库)

专为 **Shadowrocket（小火箭）** 打造的**中国境内纯净去广告规则仓库**。已彻底剔除境外代理分流规则、二十多万条无用海外域名及虚拟定位劫持，体积精简 **96%+**（仅约 310 KB），从根源避免 iOS 小火箭因加载超大规则集触发系统 50MB 内存限制（Jetsam）导致的断连与发热。

本仓库通过 **GitHub Actions** 每天北京时间 `06:00` 与 `18:00` 自动拉取上游规则清洗构建，并支持通过编辑 [custom\_ads.txt](https://www.google.com/search?q=https%3A%2F%2Fgithub.com%2F18661619000%2FBlock-ads%2Fblob%2Fmain%2Fcustom_ads.txt) 随时追加个人抓包监听到的新广告域名。

&lt;!-- STATS_START --&gt;
## 📊 规则实时更新统计

> 🕒 **更新日期**：`2026-10-15`（精确时间：`2026-10-15 11:14:36` 北京时间）｜ **文件头版本标识**：`更新日期:20261015`

- **更新时间**：`2026-10-15`（`2026-10-15 11:14:36`）
- **直连安全保护规则总数**：`39` 条（今日新增 0 条）
- **境外代理分流规则总数**：`0` 条（已清理剔除 `27,540` 条非中国境内规则）
- **去广告拦截规则总规模**：`4,117` 条（含域名规则 `1,633` 条 + URL 重写 `2,125` 条 + 响应脚本 `359` 条）

| 规则细分类型 | 所属文件 | 当前规则总数 | 今日/本次变动 | 规则作用与覆盖范围 |
| :--- | :--- | :--- | :--- | :--- |
| **去广告域名规则 (`[Rule]`)** | `CLQ_Shield.module` | **1,633 条** | `今日精简 -36 条` | 涵盖 12 大核心 App 专项规则、摇一摇 SDK 根域名及中国境内广告网域 |
| **个人抓包自定义规则** | `custom_ads.txt` | **49 条** | `今日新增 0 条` | 个人实测抓包锁定的冷门广告/快应用/短剧广告源（自动合并入模块） |
| **URL 重写规则 (`[URL Rewrite]`)** | `CLQ_Shield.module` | **2,125 条** | `今日新增 0 条` | 拦截开屏大图/视频、MTOP 广告接口、AMDC 加密调度及流氓软件官网跳转 |
| **去广告净化脚本 (`[Script]`)** | `CLQ_Shield.module` | **359 条** | `今日精简 -1 条` | 针对信息流、取件页、播放页与搜索热词的 JSON 响应结构精准剥离 |
| **HTTPS 解密域名 (`[MITM]`)** | `CLQ_Shield.module` | **629 个** | `今日新增 +10 个` | 按需解密国内 App 广告网关，内置 **18 项**银行/支付宝/政务强制排除保护 |
| **直连与安全兜底规则** | `CLQ_Route.conf` | **39 条** | `今日新增 0 条` | 局域网保留网段、六大行与主流股份制银行、支付宝、微信支付、政务平台直连 |
&lt;!-- STATS_END --&gt;

<!-- STATS_START -->
## 📊 规则实时更新统计

> 🕒 **更新日期**：`2026-10-26`（精确时间：`2026-10-26 07:59:30` 北京时间）｜ **文件头版本标识**：`更新日期:20261026`

- **更新时间**：`2026-10-26`（`2026-10-26 07:59:30`）
- **直连安全保护规则总数**：`39` 条（今日新增 0 条）
- **境外代理分流规则总数**：`0` 条（已清理剔除 `27,540` 条非中国境内规则）
- **去广告拦截规则总规模**：`4,740` 条（含域名规则 `2,254` 条 + URL 重写 `2,127` 条 + 响应脚本 `359` 条）

| 规则细分类型 | 所属文件 | 当前规则总数 | 今日/本次变动 | 规则作用与覆盖范围 |
| :--- | :--- | :--- | :--- | :--- |
| **去广告域名规则 (`[Rule]`)** | `CLQ_Shield.module` | **2,254 条** | `今日新增 0 条` | 涵盖 12 大核心 App 专项规则、摇一摇 SDK 根域名及中国境内广告网域 |
| **个人抓包自定义规则** | `custom_ads.txt` | **66 条** | `今日新增 0 条` | 个人实测抓包锁定的冷门广告/快应用/短剧广告源（自动合并入模块） |
| **URL 重写规则 (`[URL Rewrite]`)** | `CLQ_Shield.module` | **2,127 条** | `今日新增 0 条` | 拦截开屏大图/视频、MTOP 广告接口、AMDC 加密调度及流氓软件官网跳转 |
| **去广告净化脚本 (`[Script]`)** | `CLQ_Shield.module` | **359 条** | `今日新增 0 条` | 针对信息流、取件页、播放页与搜索热词的 JSON 响应结构精准剥离 |
| **HTTPS 解密域名 (`[MITM]`)** | `CLQ_Shield.module` | **615 个** | `今日新增 0 个` | 按需解密国内 App 广告网关，内置 **18 项**银行/支付宝/政务强制排除保护 |
| **直连与安全兜底规则** | `CLQ_Route.conf` | **39 条** | `今日新增 0 条` | 局域网保留网段、六大行与主流股份制银行、支付宝、微信支付、政务平台直连 |
<!-- STATS_END -->

## 🚀 快速开始（Shadowrocket 订阅链接）

在 Shadowrocket 中复制以下链接添加配置与模块（国内无代理环境下若 GitHub Raw 较慢，可优先使用右侧 **国内 CDN 加速链接**）：

| 类型 | 文件名称 | GitHub Raw 原生链接 | 国内 CDN 加速链接（推荐国内直连使用） |
| :--- | :--- | :--- | :--- |
| **去广告模块** | `CLQ_Shield.module` | `https://raw.githubusercontent.com/18661619000/Block-ads/main/CLQ_Shield.module` | `https://fastly.jsdelivr.net/gh/18661619000/Block-ads@main/CLQ_Shield.module` |
| **主规则配置** | `CLQ_Route.conf` | `https://raw.githubusercontent.com/18661619000/Block-ads/main/CLQ_Route.conf` | `https://fastly.jsdelivr.net/gh/18661619000/Block-ads@main/CLQ_Route.conf` |

## 📁 仓库目录结构说明

请确保仓库中的文件按以下目录结构存放（注意 `update.yml` 必须位于 `.github/workflows/` 目录下）：

```text
Block-ads/
├── .github/
│   └── workflows/
│       └── update.yml        # GitHub Actions 自动定时构建与提交工作流（同步更新模块、配置与 README 统计）
├── CLQ_Route.conf            # Shadowrocket 主规则配置文件（首行标注 # CLQ_Route (更新日期:YYYYMMDD)）
├── CLQ_Shield.module         # Shadowrocket 核心去广告模块（首行标注 #!name=CLQ_Shield (更新日期:YYYYMMDD)）
├── custom_ads.txt            # 个人手动抓包新增的广告域名清单（修改保存后自动触发重编译）
├── update_clq.py             # 自动拉取上游、清洗非境内规则、防断网校验并更新统计面板的核心 Python 脚本
└── README.md                 # 仓库说明与实时更新统计文档
```

## 🎯 12 大主流国内 App 专项去广告覆盖

本仓库针对日常高频使用的 **12 款核心 App** 进行了广告联盟溯源、防 HTTPDNS 绕过与防误杀专项优化：

| 所属生态 | 专项优化 App | 核心拦截的广告联盟 / 网关 / 机制 | 防误杀与防断网安全保护 |
| :--- | :--- | :--- | :--- |
| **百度生态** | **百度、百度地图** | 百度百青藤（`mobads` / `pos` / `cpro` / `afd` / `ssp`）、百家号信息流广告、百度地图 `?qt=ads/sdkads/splash/poi_ads` 图层与开屏广告、百度 HTTPDNS（`httpdns.baidubce.com` 及硬编码 IP `180.76.76.200`） | 保护 `newclient.map.baidu.com`、`ugc.map.baidu.com` 与 `bdimg.com` 根域名不被整站拦截，确保地点搜索、导航、评价图片正常加载 |
| **阿里与蚂蚁生态** | **淘宝、天猫、菜鸟、闲鱼、支付宝** | 阿里妈妈（`tanx.com` / `alimama.com`）、友盟+（`umeng.com`）、阿里 AMDC 移动调度（`/amdc/mobileDispatch`）、淘宝开屏与弹窗（`poplayer`）、菜鸟裹裹信息流（`guoguo.nbnetflow.ads`）与飞鸟 AdX、闲鱼开屏与同城/信息流推广（`idlecommerce.splash` / `idleadv`） | • **淘宝**：保留正常商品主图与详情页 `.mp4` 视频，仅拦截 `alimama` 广告视频；保留 `accscdn` 消息推送<br>• **支付宝**：仅在域名层静默拦截 `ad/adgw/mdap/loggw.alipay.com`，**严禁对 `*.alipay.com` 进行 MITM 解密**，保障刷码支付与人脸识别绝对安全 |
| **京东生态** | **京东** | 京准通 DSP（`dsp-x` / `bdsp-x` / `x.jd.com` / `ads-union`）、京东 HTTPDNS（`dns.jd.com`）、开屏与弹窗接口（`start` / `queryMaterialAdverts` / `homeAreaPop`）及 `360buyimg` 弹窗素材路径 | 移除原版对 `img2.360buyimg.com` 的整站封禁，确保商品详情页图片不裂图 |
| **音频生态** | **喜马拉雅** | 喜马拉雅自建声效广告平台（`adse` / `ad` / `adwsa` / `adbehavior.ximalaya.com`）、开屏与贴片接口（`/ting/(loading\|feed\|home)`、`/api/v*/adRealTime`）及播放页推荐净化 | 修复原版 `/ting/(loading\|feed\|home)?` 末尾问号导致的正常音频接口误杀，移除 `/mobile-playpage/view/` 误杀 |
| **字节跳动生态** | **番茄小说、番茄畅听、红果短剧** | 穿山甲联盟 Pangle（`pangolin-sdk-toutiao*.com` / `pglstatp-toutiao.com`）、巨量引擎（`oceanengine.com`）、字节内生广告域（`ad.zijieapi.com` / `ads3/5-normal-*.zijieapi.com` / `ad.fqnovel.com` / `obriccloud.com`）、阅读页视频广告（`*reading-ad.qznovelvod.com`）、快应用小说/短剧推广（`novelquickapp*.com`）及优量汇/快手回退源 | • 保护 `zijieapi.com`、`snssdk.com`、`byteimg.com`、`pstatp.com` 根域名不被整站封禁，确保章节正文、听书音频、短剧视频及书封图片正常加载<br>• 全面采用 `REJECT-DICT` 返回空 JSON，避免翻页转圈卡顿 |
| **全网摇一摇 SDK** | **通用开屏摇一摇/扭一扭** | 倍孜（`beizi.biz` / `adscope.com.cn`）、UBiX（`ubixioe.com`）、章鱼移动（`zhangyuyidong.cn`）、旺脉（`adwangmai.com`）、瑞狮（`vlion.cn` / `advlion.com`）、TopOn（`anythinktech.com`）、Sigmob、科大讯飞广告（`voiceads.cn`）、快手广告（`adkwai.com`） | 从根域名层级阻断开屏“一碰手机就自动跳转第三方 App”的陀螺仪摇一摇广告 SDK |

## ⚙️ Shadowrocket 正确配置步骤

1. **导入主配置**：
   打开 Shadowrocket → 点击底部 **「配置」** → 点击右上角 `+` 号 → 粘贴上方 `CLQ_Route.conf` 的订阅链接并下载 → 点击该配置启用。
2. **开启 HTTPS 解密（MITM，关键步骤）**：
   在「配置」页面点击 `CLQ_Route.conf` 右侧的 **`i`** 图标 → 进入 **「HTTPS 解密」** → 开启 **HTTPS 解密** 开关 → 点击 **「生成新的 CA 证书」** → 按提示安装描述文件，并前往 iOS **「设置 → 通用 → 关于本机 → 证书信任设置」** 中勾选信任该根证书。
3. **导入去广告模块**：
   切换到底部 **「模块」** 标签页 → 点击右上角 `+` 号 → 粘贴上方 `CLQ_Shield.module` 的订阅链接并下载，确保模块处于勾选启用状态。
4. **设置全局路由**：
   回到 Shadowrocket **「首页」** → 将 **「全局路由」** 设置为 **「配置」** → 打开顶部连接开关即可（主配置已设为 `FINAL,DIRECT`，无需挂载任何境外节点即可直接作为本地去广告 VPN 常驻使用）。

## ➕ 如何添加自己抓包发现的新广告域名？

当你通过 Shadowrocket「数据 → 代理日志」筛选出新的广告域名时，无需手动编辑庞大的 `.module` 文件：

1. 直接在 GitHub 上打开本仓库根目录的 [custom\_ads.txt](https://www.google.com/search?q=https%3A%2F%2Fgithub.com%2F18661619000%2FBlock-ads%2Fblob%2Fmain%2Fcustom_ads.txt) 文件，点击编辑。
2. 在文件末尾换行填入新域名（支持直接写纯域名或完整规则）：
   ```text
   # 写法一：直接写域名（脚本会自动转为 DOMAIN-SUFFIX,域名,REJECT-DICT）
   iytcdn.com
   obriccloud.com

   # 写法二：写完整规则
   DOMAIN-SUFFIX,iytcdn.com,REJECT-200
   URL-REGEX,^https?:\/\/[^\/]*reading-ad\.qznovelvod\.com,REJECT-200
   ```
3. 点击 **Commit changes** 保存提交。
4. 仓库的 **GitHub Actions** 会自动触发运行 `update_clq.py`（约 20~30 秒完成），自动去重、完成防断网白名单校验，并将最新生成的规则与最新日期写入 `CLQ_Shield.module`、`CLQ_Route.conf` 和 `README.md`。随后在 Shadowrocket「模块」页面下拉刷新即可同步。

## ⚠️ 首次开启仓库 GitHub Actions 写入权限提示

首次将文件上传至 [18661619000/Block-ads](https://www.google.com/search?q=https%3A%2F%2Fgithub.com%2F18661619000%2FBlock-ads) 后，请检查一次仓库权限设置以确保自动提交生效：
* 进入仓库顶部的 **Settings** → 左侧菜单点击 **Actions → General**。
* 向下滚动找到 **Workflow permissions**，确认选中 **Read and write permissions**（读写权限），点击 **Save**。
* 进入仓库顶部的 **Actions** 标签页，点击左侧 **Auto Update CLQ_Shield Rules** → 点击右侧 **Run workflow** 即可立即测试一次自动构建。
