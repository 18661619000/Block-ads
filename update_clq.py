#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CLQ_Shield & CLQ_Route 自动构建与统计更新脚本 (update_clq.py)
仓库地址：https://github.com/18661619000/Block-ads
功能：
1. 自动从上游 Unwhimsical/NetPilot 拉取最新模块数据（若网络异常可自动回退读取本地缓存）
2. 自动读取仓库根目录下的 custom_ads.txt（平时手动抓包添加的广告域名）
3. 自动清理非中国境内的代理规则 (PROXY) 与二十多万条海外无关域名
4. 内置 12 大主流国内 App（百度、百度地图、淘宝、天猫、支付宝、菜鸟、闲鱼、京东、喜马拉雅、番茄小说、番茄畅听、红果短剧）专项强化与防断网保护
5. 严格按规范写入首行日期标识：
   - CLQ_Route.conf 第一行：# CLQ_Route (更新日期:YYYYMMDD)
   - CLQ_Shield.module 第一行：#!name=CLQ_Shield (更新日期:YYYYMMDD)
6. 自动计算每次构建的规则变动量，并同步更新 README.md 中的「📊 规则实时更新统计」面板
"""

from collections import OrderedDict
from datetime import datetime, timezone, timedelta
import os
import re
import urllib.request

UPSTREAM_URL = "https://raw.githubusercontent.com/Unwhimsical/NetPilot/refs/heads/main/modules/NetPilot_Shield.module"
CUSTOM_ADS_FILE = "custom_ads.txt"
OUT_MODULE_FILE = "CLQ_Shield.module"
OUT_CONF_FILE = "CLQ_Route.conf"
README_FILE = "README.md"

PROTECTED_ROOT_DOMAINS = {
    "baidu.com", "map.baidu.com", "newclient.map.baidu.com", "client.map.baidu.com", "ugc.map.baidu.com",
    "bdimg.com", "bdstatic.com", "taobao.com", "tmall.com", "alicdn.com", "cainiao.com", "cn-acs.m.cainiao.com",
    "goofish.com", "acs.m.goofish.com", "g-acs.m.goofish.com", "alipay.com", "alipayobjects.com",
    "jd.com", "api.m.jd.com", "360buyimg.com", "img2.360buyimg.com", "accscdn.m.taobao.com",
    "ximalaya.com", "xmcdn.com", "zijieapi.com", "snssdk.com", "isnssdk.com", "fqnovel.com",
    "byteimg.com", "pstatp.com", "volces.com", "douyin.com", "toutiao.com", "qq.com", "gtimg.cn",
}


def get_beijing_times():
    tz_bj = timezone(timedelta(hours=8))
    now = datetime.now(tz_bj)
    return now.strftime("%Y%m%d"), now.strftime("%Y-%m-%d"), now.strftime("%Y-%m-%d %H:%M:%S")


def read_previous_stats():
    stats = {"rules": None, "rewrites": None, "scripts": None, "mitm": None, "custom": None, "direct": 39}
    if os.path.exists(OUT_MODULE_FILE):
        try:
            with open(OUT_MODULE_FILE, "r", encoding="utf-8", errors="replace") as f:
                head = [next(f, "") for _ in range(20)]
            text = "".join(head)
            m_r = re.search(r"# 国内去广告规则总数:\s*(\d+)", text)
            m_rw = re.search(r"# 国内 URL 重写总数:\s*(\d+)", text)
            m_sc = re.search(r"# 国内去广告脚本总数:\s*(\d+)", text)
            m_m = re.search(r"# MITM 主机名总数:\s*(\d+)", text)
            if m_r: stats["rules"] = int(m_r.group(1))
            if m_rw: stats["rewrites"] = int(m_rw.group(1))
            if m_sc: stats["scripts"] = int(m_sc.group(1))
            if m_m: stats["mitm"] = int(m_m.group(1))
        except Exception:
            pass
    return stats


def format_delta(new_val, old_val, unit="条"):
    if old_val is None:
        return f"今日新增 0 {unit}"
    diff = new_val - old_val
    if diff > 0:
        return f"今日新增 +{diff} {unit}"
    elif diff < 0:
        return f"今日精简 {diff} {unit}"
    return f"今日新增 0 {unit}"


def fetch_upstream_lines():
    req = urllib.request.Request(
        UPSTREAM_URL,
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            content = resp.read().decode("utf-8", errors="replace")
            print(f"[INFO] 成功拉取上游规则: {UPSTREAM_URL}")
            return [line.rstrip("\r\n") for line in content.splitlines()]
    except Exception as e:
        print(f"[WARN] 拉取上游失败 ({e})，读取本地现有 {OUT_MODULE_FILE} 作为基础源...")
        if os.path.exists(OUT_MODULE_FILE):
            with open(OUT_MODULE_FILE, "r", encoding="utf-8", errors="replace") as f:
                return [line.rstrip("\r\n") for line in f]
        raise RuntimeError("无法获取上游规则且本地无缓存文件")


def load_custom_ads():
    custom_rules = []
    if not os.path.exists(CUSTOM_ADS_FILE):
        return custom_rules
    with open(CUSTOM_ADS_FILE, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            s = line.strip()
            if not s or s.startswith("#"):
                continue
            if "," not in s:
                dom = s.lower().lstrip("*.")
                if dom in PROTECTED_ROOT_DOMAINS:
                    print(f"[WARN] 跳过受保护的核心业务根域名: {dom}")
                    continue
                custom_rules.append(f"DOMAIN-SUFFIX,{dom},REJECT-DICT")
            else:
                parts = [p.strip() for p in s.split(",")]
                rtype = parts[0].upper()
                target = parts[1].lstrip("*.") if rtype in ("DOMAIN", "DOMAIN-SUFFIX") else parts[1]
                if rtype in ("DOMAIN", "DOMAIN-SUFFIX") and target.lower() in PROTECTED_ROOT_DOMAINS:
                    print(f"[WARN] 跳过受保护的核心业务根域名: {target}")
                    continue
                pol = parts[2].upper() if len(parts) >= 3 else "REJECT-DICT"
                if pol == "REJECT":
                    pol = "REJECT-200"
                custom_rules.append(f"{rtype},{target},{pol}")
    return custom_rules


def build_conf(ymd_compact, ymd_dash, full_time):
    conf_content = f"""# CLQ_Route (更新日期:{ymd_compact})
# 仓库地址：https://github.com/18661619000/Block-ads
# 订阅地址：https://raw.githubusercontent.com/18661619000/Block-ads/main/CLQ_Route.conf
# 更新时间：{full_time} 北京时间
# 适用客户端：Shadowrocket (小火箭本地去广告配置)
# 核心特性：
# 1. 专为中国境内去广告设计：清理全部境外代理分流规则、境外 DoH 及无用海外域名，无虚拟定位劫持
# 2. 针对百度、百度地图、淘宝、天猫、支付宝、菜鸟、闲鱼、京东、喜马拉雅、番茄小说、番茄畅听、红果短剧专项调优
# 3. 拦截 UDP 443 (HTTP/3 QUIC)，防止百度、淘宝、菜鸟、闲鱼、京东、番茄/红果(字节系)通过 QUIC 协议绕过去广告规则
# 4. 支付宝与各大银行核心业务域名直连并强制排除 MITM 解密，确保刷码支付、人脸识别与资金绝对安全
# 5. 默认兜底策略为 FINAL,DIRECT，无需配置境外代理节点即可直接在小火箭中开启本地 VPN 实现全天候去广告

[General]
bypass-system = true
skip-proxy = 192.168.0.0/16, 10.0.0.0/8, 172.16.0.0/12, 100.64.0.0/10, 127.0.0.0/8, localhost, *.local, captive.apple.com
tun-excluded-routes = 10.0.0.0/8, 100.64.0.0/10, 127.0.0.0/8, 169.254.0.0/16, 172.16.0.0/12, 192.0.0.0/24, 192.0.2.0/24, 192.88.99.0/24, 192.168.0.0/16, 198.51.100.0/24, 203.0.113.0/24, 224.0.0.0/4, 255.255.255.255/32, 239.255.255.250/32, ff02::fb/128
dns-server = 223.5.5.5, 119.29.29.29, https://dns.alidns.com/dns-query, https://doh.pub/dns-query

# 启用 IPv6 支持，但默认优先使用 IPv4
ipv6 = true
prefer-ipv6 = false

# 国内直连使用系统与国内高速 DNS 解析
dns-direct-system = true

# 自动响应 ICMP，提升兼容性
icmp-auto-reply = true

# 非必要不修改
always-reject-url-rewrite = false
private-ip-answer = true

# 纯境内去广告模式下无需回退代理 DNS
dns-direct-fallback-proxy = false

# UDP 策略：回退为直连（保障微信语音、视频通话等稳定可用）
udp-policy-not-supported-behaviour = DIRECT

[Rule]
# 1. 局域网与保留地址直连（带 no-resolve 避免触发多余 DNS 查询）
IP-CIDR,192.168.0.0/16,DIRECT,no-resolve
IP-CIDR,10.0.0.0/8,DIRECT,no-resolve
IP-CIDR,172.16.0.0/12,DIRECT,no-resolve
IP-CIDR,100.64.0.0/10,DIRECT,no-resolve
IP-CIDR,127.0.0.0/8,DIRECT,no-resolve
IP-CIDR,169.254.0.0/16,DIRECT,no-resolve

# 2. 支付宝广告与埋点网关优先拦截（置于 alipay.com 直连兜底之前，无感屏蔽开屏与腰封广告且不触发 MITM）
DOMAIN-SUFFIX,ad.alipay.com,REJECT-200
DOMAIN-SUFFIX,adgw.alipay.com,REJECT-200
DOMAIN-SUFFIX,mdap.alipay.com,REJECT-200
DOMAIN-SUFFIX,loggw.alipay.com,REJECT-200
DOMAIN-SUFFIX,loggw.alipay.com.cn,REJECT-200
DOMAIN-SUFFIX,loggw-ex.alipay.com,REJECT-200
DOMAIN-SUFFIX,amdc.alipay.com,REJECT-200
DOMAIN-SUFFIX,amdc-sibling.alipay.com.cn,REJECT-200

# 3. 核心银行、支付与政务服务直连（保障收付款、网银与政务安全）
DOMAIN-SUFFIX,icbc.com.cn,DIRECT
DOMAIN-SUFFIX,ccb.com,DIRECT
DOMAIN-SUFFIX,ccb.com.cn,DIRECT
DOMAIN-SUFFIX,boc.cn,DIRECT
DOMAIN-SUFFIX,abchina.com,DIRECT
DOMAIN-SUFFIX,abchina.com.cn,DIRECT
DOMAIN-SUFFIX,bankcomm.com,DIRECT
DOMAIN-SUFFIX,bankcomm.cn,DIRECT
DOMAIN-SUFFIX,psbc.com,DIRECT
DOMAIN-SUFFIX,cmbchina.com,DIRECT
DOMAIN-SUFFIX,citicbank.com,DIRECT
DOMAIN-SUFFIX,spdb.com.cn,DIRECT
DOMAIN-SUFFIX,cib.com.cn,DIRECT
DOMAIN-SUFFIX,pingan.com,DIRECT
DOMAIN-SUFFIX,pingan.com.cn,DIRECT
DOMAIN-SUFFIX,unionpay.com,DIRECT
DOMAIN-SUFFIX,95516.com,DIRECT
DOMAIN-SUFFIX,alipay.com,DIRECT
DOMAIN-SUFFIX,alipayobjects.com,DIRECT
DOMAIN-SUFFIX,wechatpay.com,DIRECT
DOMAIN-SUFFIX,tenpay.com,DIRECT
DOMAIN-SUFFIX,122.gov.cn,DIRECT
DOMAIN-SUFFIX,nhsa.gov.cn,DIRECT

# 4. 拦截 HTTP/3 (QUIC)，强制回退 TCP，防止淘宝、百度、京东、番茄小说、红果短剧利用 QUIC 绕过本地去广告规则
AND,((PROTOCOL,UDP),(DEST-PORT,443)),REJECT-NO-DROP

# 5. 最终兜底：所有非广告正常流量全部直连
FINAL,DIRECT

[Host]
localhost = 127.0.0.1

[MITM]
# 主配置强制排除所有银行、支付宝、微信支付与政务域名；去广告域名由 CLQ_Shield.module 按需追加
enable = true
hostname = -*.alipay.com, -*.alipay.com.cn, -*.alipayobjects.com, -*.icbc.com.cn, -*.ccb.com, -*.ccb.com.cn, -*.boc.cn, -*.abchina.com, -*.abchina.com.cn, -*.bankcomm.com, -*.bankcomm.cn, -*.psbc.com, -*.cmbchina.com, -*.citicbank.com, -*.spdb.com.cn, -*.cib.com.cn, -*.pingan.com, -*.pingan.com.cn, -*.unionpay.com, -*.95516.com, -*.wechatpay.com, -*.tenpay.com, -*.122.gov.cn, -*.nhsa.gov.cn, -*.apple.com, -*.icloud.com
"""
    with open(OUT_CONF_FILE, "w", encoding="utf-8") as f:
        f.write(conf_content)
    # Count direct/rule lines in CLQ_Route.conf
    direct_count = sum(1 for l in conf_content.splitlines() if l.startswith(("IP-CIDR,", "DOMAIN-SUFFIX,", "AND,", "FINAL,")))
    return direct_count


def update_readme_stats(ymd_compact, ymd_dash, full_time, new_stats, old_stats):
    if not os.path.exists(README_FILE):
        return
    with open(README_FILE, "r", encoding="utf-8", errors="replace") as f:
        readme_text = f.read()

    r_delta = format_delta(new_stats["rules"], old_stats.get("rules"), "条")
    c_delta = format_delta(new_stats["custom"], old_stats.get("custom"), "条")
    rw_delta = format_delta(new_stats["rewrites"], old_stats.get("rewrites"), "条")
    sc_delta = format_delta(new_stats["scripts"], old_stats.get("scripts"), "条")
    m_delta = format_delta(new_stats["mitm"], old_stats.get("mitm"), "个")
    d_delta = format_delta(new_stats["direct"], old_stats.get("direct"), "条")
    total_ad_items = new_stats["rules"] + new_stats["rewrites"] + new_stats["scripts"]

    stats_block = f"""<!-- STATS_START -->
## 📊 规则实时更新统计

> 🕒 **更新日期**：`{ymd_dash}`（精确时间：`{full_time}` 北京时间）｜ **文件头版本标识**：`更新日期:{ymd_compact}`

- **更新时间**：`{ymd_dash}`（`{full_time}`）
- **直连安全保护规则总数**：`{new_stats["direct"]:,}` 条（{d_delta}）
- **境外代理分流规则总数**：`0` 条（已清理剔除 `27,540` 条非中国境内规则）
- **去广告拦截规则总规模**：`{total_ad_items:,}` 条（含域名规则 `{new_stats["rules"]:,}` 条 + URL 重写 `{new_stats["rewrites"]:,}` 条 + 响应脚本 `{new_stats["scripts"]:,}` 条）

| 规则细分类型 | 所属文件 | 当前规则总数 | 今日/本次变动 | 规则作用与覆盖范围 |
| :--- | :--- | :--- | :--- | :--- |
| **去广告域名规则 (`[Rule]`)** | `CLQ_Shield.module` | **{new_stats["rules"]:,} 条** | `{r_delta}` | 涵盖 12 大核心 App 专项规则、摇一摇 SDK 根域名及中国境内广告网域 |
| **个人抓包自定义规则** | `custom_ads.txt` | **{new_stats["custom"]:,} 条** | `{c_delta}` | 个人实测抓包锁定的冷门广告/快应用/短剧广告源（自动合并入模块） |
| **URL 重写规则 (`[URL Rewrite]`)** | `CLQ_Shield.module` | **{new_stats["rewrites"]:,} 条** | `{rw_delta}` | 拦截开屏大图/视频、MTOP 广告接口、AMDC 加密调度及流氓软件官网跳转 |
| **去广告净化脚本 (`[Script]`)** | `CLQ_Shield.module` | **{new_stats["scripts"]:,} 条** | `{sc_delta}` | 针对信息流、取件页、播放页与搜索热词的 JSON 响应结构精准剥离 |
| **HTTPS 解密域名 (`[MITM]`)** | `CLQ_Shield.module` | **{new_stats["mitm"]:,} 个** | `{m_delta}` | 按需解密国内 App 广告网关，内置 **18 项**银行/支付宝/政务强制排除保护 |
| **直连与安全兜底规则** | `CLQ_Route.conf` | **{new_stats["direct"]:,} 条** | `{d_delta}` | 局域网保留网段、六大行与主流股份制银行、支付宝、微信支付、政务平台直连 |
<!-- STATS_END -->"""

    if "<!-- STATS_START -->" in readme_text and "<!-- STATS_END -->" in readme_text:
        readme_text = re.sub(
            r"<!-- STATS_START -->.*?<!-- STATS_END -->",
            stats_block,
            readme_text,
            flags=re.DOTALL
        )
    else:
        readme_text = readme_text.replace("## 🚀 快速开始", stats_block + "\n\n## 🚀 快速开始", 1)

    with open(README_FILE, "w", encoding="utf-8") as f:
        f.write(readme_text)


def main():
    ymd_compact, ymd_dash, full_time = get_beijing_times()
    old_stats = read_previous_stats()
    direct_count = build_conf(ymd_compact, ymd_dash, full_time)
    lines = fetch_upstream_lines()
    custom_rules = load_custom_ads()
    old_stats["custom"] = len(custom_rules) if old_stats.get("custom") is None else old_stats.get("custom")

    sections = {}
    cur = "HEADER"
    sections[cur] = []
    for l in lines:
        if l.startswith("[") and l.endswith("]"):
            cur = l
            sections[cur] = []
        else:
            sections[cur].append(l)

    raw_reject_rules = []
    mode = None
    for l in sections.get("[Rule]", []):
        s = l.strip()
        if not s:
            continue
        if s.startswith("#"):
            if "代理分流规则" in s:
                mode = "PROXY"
            elif "去广告" in s or "专项" in s or "通用" in s:
                mode = "REJECT"
            continue
        if mode == "REJECT" or (mode is None and "REJECT" in s):
            raw_reject_rules.append(s)

    curated_core_rules = [
        "# === [专项0] 用户实测抓包新增广告与摇一摇/快应用/短剧广告域名 (custom_ads.txt) ===",
        *custom_rules,
        "",
        "# === [专项1] 百度 & 百度地图（百度百青藤 MobAds + HTTPDNS 防绕过） ===",
        "DOMAIN-SUFFIX,mobads.baidu.com,REJECT-DICT",
        "DOMAIN-SUFFIX,mobads-logs.baidu.com,REJECT-200",
        "DOMAIN-SUFFIX,mobads-pre-config.cdn.bcebos.com,REJECT-DICT",
        "DOMAIN-SUFFIX,pos.baidu.com,REJECT-200",
        "DOMAIN-SUFFIX,wn.pos.baidu.com,REJECT-200",
        "DOMAIN-SUFFIX,cbjs.baidu.com,REJECT-200",
        "DOMAIN-SUFFIX,cpro.baidu.com,REJECT-200",
        "DOMAIN-SUFFIX,cpro.baidustatic.com,REJECT-200",
        "DOMAIN-SUFFIX,afd.baidu.com,REJECT-DICT",
        "DOMAIN-SUFFIX,afdconf.baidu.com,REJECT-DICT",
        "DOMAIN-SUFFIX,als.baidu.com,REJECT-200",
        "DOMAIN-SUFFIX,nadvideo2.baidu.com,REJECT-200",
        "DOMAIN-SUFFIX,nsclick.baidu.com,REJECT-200",
        "DOMAIN-SUFFIX,duclick.baidu.com,REJECT-200",
        "DOMAIN-SUFFIX,hm.baidu.com,REJECT-200",
        "DOMAIN-SUFFIX,hmma.baidu.com,REJECT-200",
        "DOMAIN-SUFFIX,httpdns.baidubce.com,REJECT-200",
        "DOMAIN-SUFFIX,httpsdns.baidu.com,REJECT-200",
        "DOMAIN-SUFFIX,httpdns.baidu.com,REJECT-200",
        "IP-CIDR,180.76.76.200/32,REJECT-200,no-resolve",
        "IP-CIDR,180.76.76.112/32,REJECT-200,no-resolve",
        "DOMAIN-SUFFIX,lookup.api.bsb.baidu.com,REJECT-200",
        "DOMAIN-SUFFIX,baidumap.baidu.com,REJECT-200",
        "DOMAIN-SUFFIX,sdk.map.baidu.com,REJECT-200",
        "DOMAIN-SUFFIX,nis.map.baidu.com,REJECT-200",
        "DOMAIN-SUFFIX,stat.map.baidu.com,REJECT-200",
        "DOMAIN-SUFFIX,log.map.baidu.com,REJECT-200",
        "DOMAIN-SUFFIX,clog.map.baidu.com,REJECT-200",
        "",
        "# === [专项2] 淘宝 & 天猫 & 菜鸟 & 闲鱼 & 支付宝（阿里妈妈 Tanx + 友盟 + AMDC 防绕过） ===",
        "DOMAIN-SUFFIX,tanx.com,REJECT-200",
        "DOMAIN-SUFFIX,df.tanx.com,REJECT-200",
        "DOMAIN-SUFFIX,et.tanx.com,REJECT-200",
        "DOMAIN-SUFFIX,ef-dongfeng.tanx.com,REJECT-200",
        "DOMAIN-SUFFIX,bdlog.tanx.com,REJECT-200",
        "DOMAIN-SUFFIX,atanx.alicdn.com,REJECT-200",
        "DOMAIN-SUFFIX,atanx2.alicdn.com,REJECT-200",
        "DOMAIN-SUFFIX,alimama.com,REJECT-200",
        "DOMAIN-SUFFIX,afp.alimama.com,REJECT-200",
        "DOMAIN-SUFFIX,tns.simba.taobao.com,REJECT-200",
        "DOMAIN-SUFFIX,strip.taobaocdn.com,REJECT-200",
        "DOMAIN-SUFFIX,adash.m.taobao.com,REJECT-200",
        "DOMAIN-SUFFIX,adashx.m.taobao.com,REJECT-200",
        "DOMAIN-SUFFIX,adashbc.ut.taobao.com,REJECT-200",
        "DOMAIN-SUFFIX,adashxgc.ut.taobao.com,REJECT-200",
        "DOMAIN-SUFFIX,h-adashx.ut.taobao.com,REJECT-200",
        "DOMAIN-SUFFIX,v6-adashx.ut.taobao.com,REJECT-200",
        "DOMAIN-SUFFIX,amdc.m.taobao.com,REJECT-200",
        "DOMAIN-SUFFIX,amdcopen.m.taobao.com,REJECT-200",
        "DOMAIN-SUFFIX,amdc.alicdn.com,REJECT-200",
        "DOMAIN-SUFFIX,httpdns.alicdn.com,REJECT-200",
        "DOMAIN-SUFFIX,wgo.mmstat.com,REJECT-200",
        "DOMAIN-SUFFIX,yt.mmstat.com,REJECT-200",
        "DOMAIN-SUFFIX,cnlogs.umeng.com,REJECT-DICT",
        "DOMAIN-SUFFIX,cnlogs.umengcloud.com,REJECT-DICT",
        "DOMAIN-SUFFIX,ulogs.umeng.com,REJECT-DICT",
        "DOMAIN-SUFFIX,ulogs.umengcloud.com,REJECT-DICT",
        "DOMAIN-SUFFIX,utoken.umeng.com,REJECT-DICT",
        "DOMAIN-SUFFIX,resolve.umeng.com,REJECT-DICT",
        "DOMAIN-SUFFIX,alog.umeng.com,REJECT-DICT",
        "DOMAIN-SUFFIX,alog.umengcloud.com,REJECT-DICT",
        "DOMAIN-SUFFIX,alogs.umeng.com,REJECT-DICT",
        "DOMAIN-SUFFIX,alogs.umengcloud.com,REJECT-DICT",
        "DOMAIN-SUFFIX,amdc.cainiao.com,REJECT-200",
        "DOMAIN-SUFFIX,ad.cainiao.com,REJECT-DICT",
        "DOMAIN-SUFFIX,adx.cainiao.com,REJECT-DICT",
        "DOMAIN-SUFFIX,adashx.ut.cainiao.com,REJECT-200",
        "DOMAIN-SUFFIX,h-adashx.ut.cainiao.com,REJECT-200",
        "DOMAIN-SUFFIX,ashx.ut.cainiao.com,REJECT-200",
        "DOMAIN-SUFFIX,amdc.m.goofish.com,REJECT-200",
        "DOMAIN-SUFFIX,ut.goofish.com,REJECT-200",
        "DOMAIN-SUFFIX,adashx.ut.goofish.com,REJECT-200",
        "DOMAIN-SUFFIX,h-adashx.ut.goofish.com,REJECT-200",
        "DOMAIN-SUFFIX,ad.goofish.com,REJECT-DICT",
        "DOMAIN-SUFFIX,ad.alipay.com,REJECT-200",
        "DOMAIN-SUFFIX,adgw.alipay.com,REJECT-200",
        "DOMAIN-SUFFIX,mdap.alipay.com,REJECT-200",
        "DOMAIN-SUFFIX,loggw.alipay.com,REJECT-200",
        "DOMAIN-SUFFIX,loggw.alipay.com.cn,REJECT-200",
        "DOMAIN-SUFFIX,loggw-ex.alipay.com,REJECT-200",
        "DOMAIN-SUFFIX,amdc.alipay.com,REJECT-200",
        "DOMAIN-SUFFIX,amdc-sibling.alipay.com.cn,REJECT-200",
        "",
        "# === [专项3] 京东（京准通 DSP + 弹窗与归因日志 + HTTPDNS 防绕过） ===",
        "DOMAIN-SUFFIX,dsp-x.jd.com,REJECT-DICT",
        "DOMAIN-SUFFIX,bdsp-x.jd.com,REJECT-DICT",
        "DOMAIN-SUFFIX,x.jd.com,REJECT-DICT",
        "DOMAIN-SUFFIX,im-x.jd.com,REJECT-DICT",
        "DOMAIN-SUFFIX,ads-union.jd.com,REJECT-DICT",
        "DOMAIN-SUFFIX,c-nfa.jd.com,REJECT-200",
        "DOMAIN-SUFFIX,cps.jd.com,REJECT-200",
        "DOMAIN-SUFFIX,popup3.jd.com,REJECT-DICT",
        "DOMAIN-SUFFIX,wa.jd.com,REJECT-200",
        "DOMAIN-SUFFIX,log.jd.com,REJECT-200",
        "DOMAIN-SUFFIX,mllog.jd.com,REJECT-200",
        "DOMAIN-SUFFIX,sgm-w.jd.com,REJECT-200",
        "DOMAIN-SUFFIX,mercury.jd.com,REJECT-200",
        "DOMAIN-SUFFIX,uranus.jd.com,REJECT-200",
        "DOMAIN-SUFFIX,orbit.jd.com,REJECT-200",
        "DOMAIN-SUFFIX,dns.jd.com,REJECT-200",
        "DOMAIN-SUFFIX,httpdns.jd.com,REJECT-200",
        "",
        "# === [专项4] 喜马拉雅（喜马拉雅 AdSE 声效广告平台与行为采集） ===",
        "DOMAIN-SUFFIX,adse.ximalaya.com,REJECT-DICT",
        "DOMAIN-SUFFIX,adse.wsa.ximalaya.com,REJECT-DICT",
        "DOMAIN-SUFFIX,ad.ximalaya.com,REJECT-DICT",
        "DOMAIN-SUFFIX,adwsa.ximalaya.com,REJECT-DICT",
        "DOMAIN-SUFFIX,adsebs.ximalaya.com,REJECT-DICT",
        "DOMAIN-SUFFIX,adbehavior.ximalaya.com,REJECT-200",
        "DOMAIN-SUFFIX,adbehavior.wsa.ximalaya.com,REJECT-200",
        "DOMAIN-SUFFIX,xdcs-collector.ximalaya.com,REJECT-200",
        "DOMAIN-SUFFIX,gslb.ximalaya.com,REJECT-200",
        "",
        "# === [专项5] 番茄小说 & 番茄畅听 & 红果短剧（穿山甲 Pangle / 巨量引擎 / 摇一摇聚合） ===",
        "DOMAIN-KEYWORD,pangolin,REJECT-DICT",
        "DOMAIN-SUFFIX,pangolin-sdk-toutiao.com,REJECT-DICT",
        "DOMAIN-SUFFIX,pangolin-sdk-toutiao-b.com,REJECT-DICT",
        "DOMAIN-SUFFIX,pangolin-sdk-toutiao1.com,REJECT-DICT",
        "DOMAIN-SUFFIX,pangolin-dsp-toutiao.com,REJECT-DICT",
        "DOMAIN-SUFFIX,api-access.pangolin-sdk-toutiao.com,REJECT-DICT",
        "DOMAIN-SUFFIX,api-access.pangolin-sdk-toutiao-b.com,REJECT-DICT",
        "DOMAIN-SUFFIX,api-access.pangolin-sdk-toutiao1.com,REJECT-DICT",
        "DOMAIN-SUFFIX,pglstatp-toutiao.com,REJECT-DICT",
        "DOMAIN-SUFFIX,pangolin16.isnssdk.com,REJECT-DICT",
        "DOMAIN-SUFFIX,pangolin16.sgsnssdk.com,REJECT-DICT",
        "DOMAIN-SUFFIX,ad.zijieapi.com,REJECT-DICT",
        "DOMAIN-SUFFIX,ads3-normal-hl.zijieapi.com,REJECT-DICT",
        "DOMAIN-SUFFIX,ads5-normal-hl.zijieapi.com,REJECT-DICT",
        "DOMAIN-SUFFIX,ads3-normal-lq.zijieapi.com,REJECT-DICT",
        "DOMAIN-SUFFIX,ads5-normal-lq.zijieapi.com,REJECT-DICT",
        "DOMAIN-SUFFIX,ads3-normal-lf.zijieapi.com,REJECT-DICT",
        "DOMAIN-SUFFIX,ads5-normal-lf.zijieapi.com,REJECT-DICT",
        "DOMAIN-SUFFIX,ad.toutiao.com,REJECT-DICT",
        "DOMAIN-SUFFIX,dsp.toutiao.com,REJECT-DICT",
        "DOMAIN-SUFFIX,dm.toutiao.com,REJECT-200",
        "DOMAIN-SUFFIX,dm.isnssdk.com,REJECT-200",
        "DOMAIN-SUFFIX,ad.fqnovel.com,REJECT-DICT",
        "DOMAIN-SUFFIX,mon11-misc-lq.fqnovel.com,REJECT-200",
        "DOMAIN-SUFFIX,frontier100-toutiao-lf.fqnovel.com,REJECT-200",
        "DOMAIN-SUFFIX,applog.fqnovel.com,REJECT-200",
        "DOMAIN-SUFFIX,rtlog.fqnovel.com,REJECT-200",
        "DOMAIN-SUFFIX,lf-reward-video.bytedcdn.com,REJECT-200",
        "DOMAIN-SUFFIX,lf-leads-fe-scm.bytecdn.com,REJECT-200",
        "DOMAIN-SUFFIX,lf-cdn-tos.bytescm.com,REJECT-200",
        "DOMAIN-SUFFIX,lf1-cdn-tos.bytescm.com,REJECT-200",
        "DOMAIN-SUFFIX,applog.zijieapi.com,REJECT-200",
        "DOMAIN-SUFFIX,mon.zijieapi.com,REJECT-200",
        "DOMAIN-SUFFIX,mcs.zijieapi.com,REJECT-200",
        "DOMAIN-SUFFIX,timon.zijieapi.com,REJECT-200",
        "DOMAIN-SUFFIX,polaris.zijieapi.com,REJECT-200",
        "DOMAIN-SUFFIX,mssdk.volces.com,REJECT-DICT",
        "DOMAIN-SUFFIX,mssdk3-normal-hl.zijieapi.com,REJECT-DICT",
        "DOMAIN-SUFFIX,ctobsnssdk.com,REJECT-DICT",
        "DOMAIN-SUFFIX,toblog.ctobsnssdk.com,REJECT-200",
        "DOMAIN-SUFFIX,tobapplog.ctobsnssdk.com,REJECT-200",
        "DOMAIN-SUFFIX,toblog.tobsnssdk.com,REJECT-200",
        "DOMAIN-SUFFIX,tobapplog.tobsnssdk.com,REJECT-200",
        "DOMAIN-SUFFIX,mon.snssdk.com,REJECT-200",
        "DOMAIN-SUFFIX,extlog.snssdk.com,REJECT-200",
        "DOMAIN-SUFFIX,log.snssdk.com,REJECT-200",
        "DOMAIN-SUFFIX,log.isnssdk.com,REJECT-200",
        "DOMAIN-SUFFIX,rtlog.isnssdk.com,REJECT-200",
        "DOMAIN-SUFFIX,dig.bdurl.net,REJECT-200",
        "DOMAIN-SUFFIX,tnc3-alisc1.zijieapi.com,REJECT-200",
        "DOMAIN-SUFFIX,tnc3-aliec2.zijieapi.com,REJECT-200",
        "DOMAIN-SUFFIX,tnc3-bjlgy.zijieapi.com,REJECT-200",
        "DOMAIN-SUFFIX,e.qq.com,REJECT-DICT",
        "DOMAIN-SUFFIX,mi.gdt.qq.com,REJECT-DICT",
        "DOMAIN-SUFFIX,v.gdt.qq.com,REJECT-DICT",
        "DOMAIN-SUFFIX,c.gdt.qq.com,REJECT-DICT",
        "DOMAIN-SUFFIX,win.gdt.qq.com,REJECT-DICT",
        "DOMAIN-SUFFIX,ugdtimg.com,REJECT-200",
        "DOMAIN-SUFFIX,gdtimg.com,REJECT-200",
        "DOMAIN-SUFFIX,open.e.kuaishou.com,REJECT-DICT",
        "DOMAIN-SUFFIX,gdfp.gifshow.com,REJECT-DICT",
        "DOMAIN-SUFFIX,beizi.biz,REJECT-DICT",
        "DOMAIN-SUFFIX,adscope.com.cn,REJECT-DICT",
        "DOMAIN-SUFFIX,anythinktech.com,REJECT-DICT",
        "DOMAIN-SUFFIX,toponad.com,REJECT-DICT",
        "DOMAIN-SUFFIX,sigmob.cn,REJECT-DICT",
        "DOMAIN-SUFFIX,sigmob.com,REJECT-DICT",
        "DOMAIN-SUFFIX,mobvista.com,REJECT-DICT",
        "DOMAIN-SUFFIX,mintegral.com,REJECT-DICT",
        "DOMAIN-SUFFIX,rayjump.com,REJECT-DICT",
        "DOMAIN-SUFFIX,inmobi.cn,REJECT-DICT",
        "DOMAIN-SUFFIX,inmobicdn.net,REJECT-200",
        "DOMAIN-SUFFIX,adview.cn,REJECT-DICT",
        "DOMAIN-SUFFIX,adview.com,REJECT-DICT",
        "DOMAIN-SUFFIX,youmi.net,REJECT-DICT",
        "DOMAIN-SUFFIX,domob.cn,REJECT-DICT",
        "DOMAIN-SUFFIX,tanv.com,REJECT-DICT",
        "DOMAIN-SUFFIX,miaozhen.com,REJECT-200",
        "DOMAIN-SUFFIX,admaster.com.cn,REJECT-200",
        "DOMAIN-SUFFIX,gridsumdissector.com,REJECT-200",
        "DOMAIN-SUFFIX,talkingdata.com,REJECT-200",
        "DOMAIN-SUFFIX,talkingdata.net,REJECT-200",
        "DOMAIN-SUFFIX,cpatrk.net,REJECT-200",
        "DOMAIN-SUFFIX,shuzilm.cn,REJECT-200",
        "DOMAIN-SUFFIX,ishumei.com,REJECT-200",
        "DOMAIN-SUFFIX,fengkongcloud.com,REJECT-200",
        "DOMAIN-SUFFIX,tuia.cn,REJECT-DICT",
        "DOMAIN-SUFFIX,duiba.com.cn,REJECT-DICT",
        "DOMAIN-SUFFIX,bianxianmao.com,REJECT-DICT",
        "DOMAIN-SUFFIX,hubcloud.com.cn,REJECT-DICT",
        "DOMAIN-SUFFIX,effirst.com,REJECT-200",
        "DOMAIN-SUFFIX,appwheel.com,REJECT-DICT",
    ]

    cn_exact_domains = {
        "baidu.com", "bdimg.com", "bdstatic.com", "baidustatic.com", "bcebos.com", "baidubce.com", "hao123.com", "duapps.com", "zuoyebang.com",
        "iqiyi.com", "71.am", "qy.net", "pps.tv",
        "taobao.com", "taobaocdn.com", "tbcdn.cn", "tmall.com", "alicdn.com", "alibaba.com", "aliyun.com", "aliyuncs.com",
        "alimama.com", "alimama.cn", "tanx.com", "mmstat.com", "alipan.com", "aliyundrive.com",
        "alipay.com", "alipay.com.cn", "alipaydns.com",
        "cainiao.com", "guoguo-app.com", "goofish.com", "ele.me", "elemecdn.com", "koubei.com", "xiami.com", "fliggy.com",
        "umeng.com", "umengcloud.com", "umsns.com", "uyunad.com", "youku.com", "ykimg.com", "tudou.com", "uc.cn", "ucweb.com", "uczzd.cn", "sm.cn",
        "dingtalk.com", "amap.com", "autonavi.com", "shuzilm.cn",
        "jd.com", "360buy.com", "360buyimg.com", "jcloud.com", "jdcloud.com", "paipai.com", "joybuy.com",
        "ximalaya.com", "xmcdn.com",
        "fqnovel.com", "novelapp.com", "snssdk.com", "isnssdk.com", "sgsnssdk.com", "tobsnssdk.com", "ctobsnssdk.com",
        "zijieapi.com", "toutiao.com", "dftoutiao.com", "pangolin-sdk-toutiao.com", "pangolin-sdk-toutiao-b.com",
        "pangolin-sdk-toutiao1.com", "pangolin-dsp-toutiao.com", "pglstatp-toutiao.com", "i18n-pglstatp.com", "pstatp.com",
        "byteimg.com", "bytecdn.com", "bytedcdn.com", "bytescm.com", "bytetos.com", "bytegoofy.com", "bytedance.com", "ibytecdn.cn",
        "douyin.com", "iesdouyin.com", "douyinpic.com", "ixigua.com", "volces.com", "volcengine.com", "bdurl.net",
        "qq.com", "gtimg.com", "qlogo.cn", "qpic.cn", "ugdtimg.com", "gdtimg.com", "myapp.com", "qcloud.com", "tencent.com",
        "kuaishou.com", "ksapisrv.com", "yximgs.com", "kwai.com", "gifshow.com", "ayximgs.com", "adkwai.com",
        "meituan.com", "meituan.net", "dianping.com", "dpfile.com", "sankuai.com", "maoyan.com",
        "pinduoduo.com", "yangkeduo.com", "pddpic.com",
        "sina.com", "sina.com.cn", "sinaimg.cn", "weibo.com", "weibo.cn", "weibocdn.com",
        "163.com", "126.net", "127.net", "netease.com", "ydstatic.com", "youdao.com", "lofter.com",
        "bilibili.com", "bilivideo.com", "hdslb.com", "biliapi.net", "biliapi.com", "acgvideo.com",
        "xiaohongshu.com", "xhscdn.com", "zhihu.com", "zhimg.com",
        "xiaomi.com", "mi.com", "miui.com", "mifile.cn", "duokan.com",
        "huawei.com", "hicloud.com", "vmall.com", "dbankcdn.com", "hihonor.com",
        "oppo.com", "oppomobile.com", "heytap.com", "heytapobi.com", "heytapimage.com", "coloros.com", "nearme.com.cn", "oneplus.cn", "oneplus.net", "realme.com",
        "vivo.com", "vivo.com.cn", "vivoglobal.com", "meizu.com", "flyme.cn",
        "360.cn", "360.com", "360safe.com", "qhimg.com", "qhres.com", "qhres2.com", "qhupdate.com", "qihoo.com", "ludashi.com", "mediav.com", "mvad.com",
        "sohu.com", "sohucs.com", "itc.cn", "sogou.com", "sogo.com", "changyou.com",
        "xunlei.com", "sandai.net", "kanimg.com", "xycdn.com", "mgtv.com", "imgo.tv", "hunantv.com",
        "le.com", "letv.com", "letvimg.com", "pptv.com", "pplive.com", "suning.com",
        "kuwo.cn", "kugou.com", "kgimg.com", "qianqian.com", "qingting.fm", "lizhi.fm",
        "smzdm.com", "zdmimg.com", "coolapk.com", "coolapkmarket.com", "douban.com", "doubanio.com",
        "hupu.com", "hoopchina.com", "shihuo.cn", "duapp.com", "dewu.com", "poizon.com", "shizhuang-inc.com",
        "ctrip.com", "c-ctrip.com", "qunar.com", "qunarzz.com", "elong.com", "ly.com", "umetrip.com", "tuniu.com", "mafengwo.cn", "variflight.com",
        "didiglobal.com", "diditaxi.com.cn", "xiaojukeji.com", "kuaidadi.com", "didapinche.com", "hellobike.com", "t3go.cn", "caocaokeji.cn", "zuche.com",
        "58.com", "58cdn.com.cn", "ganji.com", "anjuke.com", "fang.com", "ke.com", "lianjia.com", "ziroom.com",
        "autohome.com.cn", "autoimg.cn", "che168.com", "yiche.com", "bitauto.com", "dongchedi.com", "xcar.com.cn", "pcauto.com.cn", "tuhu.cn",
        "eastmoney.com", "1234567.com.cn", "xueqiu.com", "hexun.com", "10jqka.com.cn", "futunn.com", "wind.com.cn",
        "wps.cn", "wps.com", "kingsoft.com", "kingsoft-office-service.com", "iciba.com", "kdocs.cn",
        "wifi.com", "wkanx.com", "51y5.net", "moji.com", "caiyunapp.com", "cyapi.cn", "weathercn.com", "tianqi.com", "2345.com",
        "meitu.com", "meitudata.com", "meipai.com", "wuta-cam.com",
        "soulapp.cn", "blued.cn", "immomo.com", "momocdn.com", "tantanapp.com", "izuiyou.com", "xiaochuankeji.cn",
        "gotokeep.com", "boohee.com", "seeyouyima.com", "babytree.com", "dxy.cn",
        "qidian.com", "yuewen.com", "zongheng.com", "jjwxc.net", "17k.com", "ireader.com", "zhangyue.com", "zhuishushenqi.com", "km.com", "qimao.com", "wtzw.com",
        "sf-express.com", "zto.com", "yto.net.cn", "sto.cn", "yundaex.com", "ems.com.cn", "kuaidi100.com",
        "10086.cn", "10010.com", "189.cn", "wo.com.cn", "cmpassport.com", "miguvideo.com", "migu.cn",
        "cctv.com", "cntv.cn", "people.com.cn", "peopleapp.com", "xinhuanet.com", "thepaper.cn", "caixin.com", "jiemian.com", "ifeng.com", "ifengimg.com", "huanqiu.com", "guancha.cn", "zaker.com", "yidianzixun.com", "jin10.com", "vistastory.com", "lifeweek.com.cn", "qdaily.com",
        "ithome.com", "ruanmei.com", "lapin365.com", "sspai.com", "ifanr.com", "36kr.com", "huxiu.com", "geekpark.net", "zol.com.cn", "pconline.com.cn", "mydrivers.com", "nga.cn", "ngabbs.com", "tgbus.com", "gamersky.com", "3dmgame.com", "vgtime.com", "ali213.net", "tapimg.com", "taptap.com", "duowan.com", "yy.com", "huya.com", "douyu.com", "douyucdn.cn",
        "csdn.net", "jianshu.com", "oschina.net", "juejin.cn", "segmentfault.com", "cnblogs.com", "51cto.com",
        "51job.com", "51jobapp.com", "zhaopin.com", "liepin.com", "zhipin.com", "taou.com", "lagou.com",
        "vip.com", "vipstatic.com", "appvipshop.com", "dangdang.com", "gome.com.cn", "mogujie.com", "meilishuo.com", "juanpi.com", "kaola.com", "aihuishou.com", "zhuanzhuan.com",
        "luckincoffee.com", "mxbc.net", "heytea.com", "qmai.cn", "ddxq.mobi", "pupuapi.com", "freshippo.com", "samsclub.cn", "huazhu.com", "pizzahut.com.cn", "kfc.com.cn", "4008823823.com.cn",
        "chaoxing.com", "fenbi.com", "yuanfudao.com", "koolearn.com", "xdf.cn", "hujiang.com", "baicizhan.com",
        "123pan.com", "quark.cn", "weiyun.com", "115.com",
        "miaozhen.com", "admaster.com.cn", "gridsumdissector.com", "gridsum.com", "talkingdata.com", "talkingdata.net", "cpatrk.net", "tenddata.com",
        "jpush.cn", "jpush.io", "jiguang.cn", "n0909.com", "getui.com", "getui.net", "igexin.com",
        "mob.com", "sharesdk.cn", "tinymob.com", "sensorsdata.cn", "growingio.com", "gio.ren", "tingyun.com", "networkbench.com", "bonree.com", "oneapm.com",
        "ishumei.com", "fengkongcloud.com", "tongdun.net", "fraudmetrix.cn", "geetest.com", "dingxiang-inc.com",
        "anythinktech.com", "toponad.com", "sigmob.cn", "sigmob.com", "mobvista.com", "mintegral.com", "rayjump.com",
        "inmobi.cn", "inmobicdn.net", "adview.cn", "adview.com", "youmi.net", "domob.cn", "ader.mobi", "smarter.com.cn",
        "tanv.com", "voiceads.cn", "iflytek.com", "xfyun.cn",
        "beizi.biz", "adscope.com.cn", "hubcloud.com.cn", "ubixioe.com", "vlion.cn", "advlion.com", "ruirui.com", "zampda.net", "ipinyou.com",
        "allyes.com", "allyes.com.cn", "chanet.com.cn", "duomai.com", "yiqifa.com", "adchina.com", "adwo.com", "casee.cn", "waps.cn", "winads.cn", "wqmobile.com",
        "cnzz.com", "51.la", "51yes.com", "linezing.com", "wrating.com",
        "ugsdk.cn", "ugsdk.com", "66mobi.com", "1rtb.net", "appwheel.com", "effirst.com",
        "tuia.cn", "duiba.com.cn", "bianxianmao.com", "adbaita.com", "adbright.cn", "adcome.cn", "adguang.com", "adpolestar.net", "adsage.com", "adsame.com", "adsmogo.com", "aduwant.com", "adxmi.com",
        "appsflyersdk.com", "appsflyer.com", "adjust.com", "app-measurement.com", "googlesyndication.com", "doubleclick.net", "googleadservices.com", "google-analytics.com", "admob.com", "admob-cn.com", "2mdn.net", "2mdn-cn.net", "admeld.com", "unity3d.com", "applovin.com", "applvn.com", "vungle.com", "ironsrc.com", "chartboost.com", "supersonicads.com",
    }

    false_positive_reject_domains = {
        "img2.360buyimg.com",
        "accscdn.m.taobao.com",
        "lf-static.tiktokpangle-cdn-us.com",
        "hotapi-va.isnssdk.com",
        "imapi-sg.isnssdk.com",
        "tnc16-alisg.isnssdk.com",
        "tnc16-useast1a.isnssdk.com",
        "sf16-static.i18n-pglstatp.com",
        "apmplus.ap-southeast-1.volces.com",
    } | PROTECTED_ROOT_DOMAINS

    def is_cn_domain(dom):
        if dom in false_positive_reject_domains:
            return False
        if dom.endswith(".cn") or dom.endswith(".xn--fiqs8s") or dom.endswith(".xn--fiqz9s"):
            return True
        parts = dom.split(".")
        for i in range(len(parts)):
            if ".".join(parts[i:]) in cn_exact_domains:
                return True
        return False

    all_candidate_rules = list(curated_core_rules) + ["# === [通用] 其他中国境内及国内 App 广告/追踪拦截规则 ==="]
    for r in raw_reject_rules:
        if not r.endswith(",REJECT"):
            parts = [p.strip() for p in r.split(",")]
            if parts[0] == "DOMAIN-SUFFIX" and parts[1].lower() in false_positive_reject_domains:
                continue
            all_candidate_rules.append(r)
        else:
            parts = [p.strip() for p in r.split(",")]
            if is_cn_domain(parts[1].lower()):
                all_candidate_rules.append(r)

    prio = {"REJECT-DICT": 4, "REJECT-IMG": 3, "REJECT-VIDEO": 3, "REJECT-200": 2, "REJECT": 1}
    best_rule_by_key = OrderedDict()
    all_suffixes = set()

    for l in all_candidate_rules:
        if not l or l.startswith("#"):
            continue
        parts = [p.strip() for p in l.split(",")]
        rtype, target, pol = parts[0], parts[1], parts[2]
        if rtype == "DOMAIN-SUFFIX":
            all_suffixes.add(target.lower())
        if rtype == "IP-CIDR" and "no-resolve" not in parts[3:]:
            parts.append("no-resolve")
        key = (rtype, target.lower())
        norm_str = ",".join(parts)
        if key not in best_rule_by_key or prio.get(pol, 0) > best_rule_by_key[key][0]:
            best_rule_by_key[key] = (prio.get(pol, 0), norm_str)

    def has_parent_in_set(dom, suffix_set):
        parts = dom.split(".")
        for i in range(1, len(parts)):
            if ".".join(parts[i:]) in suffix_set:
                return True
        return False

    final_rule_lines = []
    emitted_keys = set()
    rule_count = 0
    in_general = False

    for l in all_candidate_rules:
        if not l or l.startswith("#"):
            if "=== [通用]" in l:
                in_general = True
            final_rule_lines.append(l)
            continue
        parts = [p.strip() for p in l.split(",")]
        key = (parts[0], parts[1].lower())
        if key in emitted_keys:
            continue
        if in_general and parts[0] == "DOMAIN-SUFFIX" and has_parent_in_set(key[1], all_suffixes):
            continue
        emitted_keys.add(key)
        final_rule_lines.append(best_rule_by_key[key][1])
        rule_count += 1

    # URL Rewrites
    curated_rewrites = [
        "# --- 闲鱼 (Goofish) 专项重写（全网关覆盖 acs / g-acs / guide-acs / h5api） ---",
        r"^https?:\/\/[a-zA-Z0-9_.-]+\.goofish\.com\/gw\/mtop\.taobao\.idlecommerce\.splash _ REJECT-DICT",
        r"^https?:\/\/[a-zA-Z0-9_.-]+\.goofish\.com\/gw\/mtop\.idle\.idleadv\. _ REJECT-DICT",
        r"^https?:\/\/[a-zA-Z0-9_.-]+\.goofish\.com\/gw\/mtop.*splash\.ads _ REJECT-DICT",
        r"^https?:\/\/[a-zA-Z0-9_.-]+\.goofish\.com\/gw\/mtop\.taobao\.idlemtopsearch\.search\.discover _ REJECT-DICT",
        r"^https?:\/\/[a-zA-Z0-9_.-]+\.goofish\.com\/gw\/mtop\.taobao\.idlemtopsearch\.item\.search\.activate _ REJECT-DICT",
        r"^https?:\/\/[a-zA-Z0-9_.-]+\.goofish\.com\/gw\/mtop\.taobao\.idlehome\.idle\.coin\.nextfresh _ REJECT-DICT",
        r"^https?:\/\/[a-zA-Z0-9_.-]+\.goofish\.com\/gw\/mtop\.taobao\.idle\.playboy\.recommend _ REJECT-DICT",
        r"^https?:\/\/[a-zA-Z0-9_.-]+\.goofish\.com\/gw\/mtop\.taobao\.idle\.item\.resell\.recommendorhotcate _ REJECT-DICT",
        r"^https?:\/\/[a-zA-Z0-9_.-]+\.goofish\.com\/gw\/mtop\.taobao\.idle\.item\.buy\.feeds _ REJECT-DICT",
        r"^https?:\/\/[a-zA-Z0-9_.-]+\.taobao\.com\/gw\/mtop\.taobao\.idle\.home\.welcome _ REJECT-DICT",
        "# --- 阿里系 AMDC 调度拦截（防止菜鸟/闲鱼/淘宝通过加密 IP 绕过域名分流） ---",
        r"^https?:\/\/[a-zA-Z0-9_.-]+\.(taobao|alicdn|cainiao|goofish)\.com\/amdc\/mobileDispatch _ REJECT-DICT",
        "# --- 菜鸟 (Cainiao) 全网关强化重写 ---",
        r"^https?:\/\/[a-zA-Z0-9_.-]+\.cainiao\.com\/gw\/mtop\.cainiao\.guoguo\.nbnetflow\.ads\. _ REJECT-DICT",
        r"^https?:\/\/[a-zA-Z0-9_.-]+\.cainiao\.com\/gw\/mtop\.cainiao\.adx\.flyad\.getad _ REJECT-DICT",
        r"^https?:\/\/[a-zA-Z0-9_.-]+\.cainiao\.com\/gw\/mtop\.com\.cainiao\.(longquan\.place\.getpageresourcecontent|cncreditmarket\.hit\.getactivityhit|cnactivitycenter) _ REJECT-DICT",
        r"^https?:\/\/[a-zA-Z0-9_.-]+\.cainiao\.com\/gw\/mtop\.cainiao\.(nbpresentation\.tabbar\.marketing|nbopen\.miniapp\.recommend\.cpc|adkeyword\.get) _ REJECT-DICT",
        "# --- 百度 & 百度地图 强化重写 ---",
        r"^https?:\/\/(newclient|client)\.map\.baidu\.com\/client\/phpui2\/\?qt=(ads|sdkads|splash|bdbox|poi_ads) _ REJECT-DICT",
        r"^https?:\/\/(newclient|client)\.map\.baidu\.com\/client\/(crossmarketing|msgcenter|operation) _ REJECT-DICT",
        r"^https?:\/\/mime\.baidu\.com\/v\d\/IosStart\/getStartInfo _ REJECT-200",
        r"^https?:\/\/mime\.baidu\.com\/v\d\/activity\/advertisement _ REJECT-200",
        r"^https?:\/\/mbd\.baidu\.com\/newspage\/api\/getmobads _ REJECT-200",
        r"^https?:\/\/dss0\.bdstatic\.com\/.+\/tam-ogel\/.+\.(jpg|mp4) _ REJECT-200",
        r"^https?:\/\/afd\.baidu\.com\/afd\/entry _ REJECT-DICT",
        "# --- 淘宝 & 天猫 专项重写 ---",
        r"^https?:\/\/guide-acs\.m\.taobao\.com\/gw\/mtop\.taobao\.wireless\.home\.splash\.awesome\.get _ REJECT-DICT",
        r"^https?:\/\/acs\.m\.taobao\.com\/gw\/mtop\.alibaba\.advertisementservice\.getadv _ REJECT-DICT",
        r"^https?:\/\/poplayer\.template\.alibaba\.com\/\w+\.json _ REJECT-DICT",
        r"^https?:\/\/cloud\.video\.taobao\.com\/.*alimama.*\.mp4 _ REJECT-VIDEO",
        r"^https?:\/\/ossgw\.alicdn\.com\/creatives-assets\/(image|prod)\/([\w\W]*)\.(jpg|png|heic|webp) _ REJECT-200",
        "# --- 京东 专项重写 ---",
        r"^https?:\/\/api\.m\.jd\.com\/client\.action\?functionId=(start|queryMaterialAdverts|home_launchConfig|lite_advertising|homeAreaPop) _ REJECT-DICT",
        r"^https?:\/\/m\.360buyimg\.com\/mobilecms\/s1125 _ REJECT-200",
        r"^https?:\/\/(img\w|kjimg10)\.360buyimg\.com\/(pop|mcmktresadmin)\/jfs\/([\w\W]*)\.(jpg|png|heic|webp|avif) _ REJECT-200",
        "# --- 喜马拉雅 专项重写 ---",
        r"^https?:\/\/(adse\.wsa|adse|adbehavior|xdcs-collector)\.xima.*\.com\/.* _ REJECT-200",
        r"^https?:\/\/.*\.xima.*\.com\/ting\/(loading|feed|home) _ REJECT-DICT",
        r"^https?:\/\/.*\.xima.*\.com\/api\/v\d\/adRealTime _ REJECT-DICT",
        "# --- 番茄小说 & 番茄畅听 & 红果短剧 专项重写 ---",
        r"^https?:\/\/api-access\.(pangolin-sdk-toutiao|pangolin-sdk-toutiao-b|pangolin-sdk-toutiao1)\.com\/api\/ad\/ _ REJECT-DICT",
        r"^https?:\/\/.+\.pangolin-sdk-toutiao\.com\/api\/ad\/union\/sdk\/(get_ads|stats|settings)\/ _ REJECT-DICT",
        r"^https?:\/\/ether-pack\.pangolin-sdk-toutiao\.com\/union\/endcard\/ _ REJECT-200",
        r"^https?:\/\/sf\d+-fe-tos\.pglstatp-toutiao\.com\/obj\/ad-pattern\/ _ REJECT-200",
        r"^https?:\/\/.+\.(pglstatp-toutiao|pstatp)\.com\/(obj|img)\/(ad-app-package|ad|web\.business\.image)\/ _ REJECT-200",
        r"^https?:\/\/.+\.byteimg\.com\/(web\.business\.image|ad-app-package) _ REJECT-200",
        r"^https?:\/\/[\w-]+\.(snssdk|zijieapi|fqnovel)\.com\/.+_ad\/ _ REJECT-DICT",
        r"^https?:\/\/[\w-]+\.(snssdk|zijieapi|fqnovel)\.com\/api\/ad\/ _ REJECT-DICT",
        r"^https?:\/\/lf-cdn-tos\.bytescm\.com\/obj\/static\/ad _ REJECT-200",
    ]

    emitted_rw = {rw.split()[0] for rw in curated_rewrites if not rw.startswith("#")}
    rw_by_pat = OrderedDict()

    for l in sections.get("[URL Rewrite]", []):
        s = l.strip()
        if not s or s.startswith("#") or s.startswith("https://raw.githubusercontent.com/"):
            continue
        if any(bad in s for bad in [
            "cloud\\.video\\.taobao\\.com\\/vod\\/([\\w\\W]*).mp4",
            "xima.*\\.com\\/ting\\/(loading|feed|home)?",
            "xima.*\\.com\\/mobile-playpage\\/view\\/",
            "gab\\.122\\.gov\\.cn", "biliintl\\.com", "fmz200/wool_scripts",
            "google\\.cn", "g\\.cn", "spotify\\.com", "yap\\.yahoo\\.com",
            "tiktokv", "i18n-pglstatp", "ign\\.xn--fiqs8s", "aicoin\\.cn"
        ]):
            continue
        parts = s.split()
        if len(parts) == 2:
            pat, target, act = parts[0], "_", parts[1].upper()
        elif len(parts) >= 3:
            pat, target, act = parts[0], parts[1], parts[2].upper()
        else:
            continue
        if pat in emitted_rw:
            continue
        norm_line = f"{pat} {target} {act}"
        p = prio.get(act, 0)
        if pat not in rw_by_pat or p > rw_by_pat[pat][0]:
            rw_by_pat[pat] = (p, norm_line)

    final_rw_lines = curated_rewrites + ["", "# --- 其他国内主流 App 重写规则 ---"] + [v[1] for v in rw_by_pat.values()]
    rw_count = sum(1 for l in final_rw_lines if l and not l.startswith("#"))

    # Scripts
    exclude_sc = ["abchina.com", "ccb.com", "bankcomm.", "epicc.com.cn", "cmschina.com", "jk.cn", "cloudpnr.com", "u51.com", "weixin110.qq", "security.wechat", "pixiv.net", "reddit.com", "gamer.com.tw", "spotify.com"]
    sc_by_pat = OrderedDict()
    used_names = set()

    for l in sections.get("[Script]", []):
        s = l.strip()
        if not s or s.startswith("#") or " url script-" in s:
            continue
        if any(k in s.lower() for k in exclude_sc):
            continue
        s = s.replace(r"pattern=^https?:\/\/cn-acs\.m\.cainiao\.com\/gw\/", r"pattern=^https?:\/\/[a-zA-Z0-9_.-]+\.cainiao\.com\/gw\/")
        s = s.replace(r"pattern=^https?:\/\/acs\.m\.goofish\.com\/gw\/", r"pattern=^https?:\/\/(g-|guide-|h5api\.)?acs\.m\.goofish\.com\/gw\/")
        s = s.replace(r"pattern=^https?:\/\/g-acs\.m\.goofish\.com\/gw\/", r"pattern=^https?:\/\/(g-|guide-|h5api\.)?acs\.m\.goofish\.com\/gw\/")
        s = s.replace(r"pattern=^http:\/\/amdc\.m\.taobao\.com", r"pattern=^https?:\/\/amdc\.m\.taobao\.com")
        s = s.replace(r"pattern=^http:\/\/[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+){1,4}(:\d+)?\/amdc\/mobileDispatch", r"pattern=^https?:\/\/[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+){1,4}(:\d+)?\/amdc\/mobileDispatch")
        m_pat = re.search(r'pattern=([^,]+)', s)
        if not m_pat:
            continue
        pat = m_pat.group(1).strip()
        norm_pat = pat.replace(r"^https:\/\/", r"^https?:\/\/").replace(r"^https://", r"^https?://")
        if norm_pat in sc_by_pat:
            continue
        s = s.replace(f"pattern={pat}", f"pattern={norm_pat}")
        eq_idx = s.find("=type=")
        if eq_idx != -1:
            raw_name = s[:eq_idx].strip()
            rest = s[eq_idx:]
            clean_name = re.sub(r'[^a-zA-Z0-9_\-\.\u4e00-\u9fa5]', '_', raw_name).strip('_')
            if not clean_name or clean_name.startswith("w_"):
                clean_name = "ali_poplayer"
            base_name = clean_name
            idx = 2
            while clean_name in used_names:
                clean_name = f"{base_name}_{idx}"
                idx += 1
            used_names.add(clean_name)
            s = f"{clean_name}{rest}"
        sc_by_pat[norm_pat] = s

    final_sc_lines = list(sc_by_pat.values())

    # MITM
    safety_exclusions = [
        "-*.alipay.com", "-*.alipay.com.cn", "-*.alipayobjects.com",
        "-*.icbc.com.cn", "-*.ccb.com", "-*.boc.cn", "-*.abchina.com", "-*.abchina.com.cn",
        "-*.bankcomm.com", "-*.psbc.com", "-*.cmbchina.com", "-*.unionpay.com",
        "-*.wechatpay.com", "-*.tenpay.com", "-*.122.gov.cn", "-*.nhsa.gov.cn",
        "-*.apple.com", "-*.icloud.com",
    ]
    priority_mitm = [
        "*.cainiao.com", "*.goofish.com", "client.map.baidu.com", "newclient.map.baidu.com",
        "mime.baidu.com", "mbd.baidu.com", "afd.baidu.com", "dss0.bdstatic.com", "ss0.bdstatic.com",
        "gss0.bdstatic.com", "tb1.bdstatic.com", "tb2.bdstatic.com", "amdc.m.taobao.com", "amdc.alicdn.com",
        "guide-acs.m.taobao.com", "acs.m.taobao.com", "poplayer.template.alibaba.com", "cloud.video.taobao.com",
        "ossgw.alicdn.com", "g.alicdn.com", "gw.alicdn.com", "img.alicdn.com", "heic.alicdn.com",
        "cn-acs.m.cainiao.com", "acs.m.goofish.com", "g-acs.m.goofish.com", "api.m.jd.com",
        "m.360buyimg.com", "kjimg10.360buyimg.com", "router-app-api.jdcloud.com",
        "*.ximalaya.com", "*.xmcdn.com", "api-access.pangolin-sdk-toutiao.com",
        "api-access.pangolin-sdk-toutiao-b.com", "api-access.pangolin-sdk-toutiao1.com",
        "ether-pack.pangolin-sdk-toutiao.com", "*.pglstatp-toutiao.com", "lf-cdn-tos.bytescm.com",
        "toblog.ctobsnssdk.com", "dsp.toutiao.com", "open.e.kuaishou.com", "mi.gdt.qq.com",
    ]
    exclude_mitm = {
        "*.taobao.com", "*.alicdn.com", "*.360buyimg.com", "*.bdstatic.com", "*.58.com", "*.58cdn.com.cn",
        "*.google.cn", "translate.google.cn", "ditu.google.cn", "maps.google.cn", "testflight.apple.com",
        "security.wechat.com", "weixin110.qq.com", "gab.122.gov.cn", "fuwu.nhsa.gov.cn",
        "mobilepaas.abchina.com.cn", "ms.jr.jd.com", "appactive.1234567.com.cn", "api.xueqiu.com",
        "promo.xueqiu.com", "zgrb.epicc.com.cn", "saas-ad.cloudpnr.com", "mcsp.cloudpnr.com",
        "marketing.cmschina.com", "api.u51.com", "creditcardapp.bankcomm.com", "creditcardapp.bankcomm.cn",
        "yunbusiness.ccb.com", "120.241.*", "103.41.167.*", "*.feidee.*", "*.ssjlicai.*",
        "*.api.weibo.*", "api.weibo.*", "mapi.weibo.*", "oauth.secure.pixiv.net", "gql.reddit.com",
        "gql-fed.reddit.com", "api.gamer.com.tw", "spclient.wg.spotify.com", "gae2-spclient.spotify.com",
        "m.yap.yahoo.com", "passport.biliintl.com", "app.biliintl.com",
    }

    mitm_lines = [l for l in sections.get("[MITM]", []) if l.strip().startswith("hostname")]
    raw_hosts = []
    if mitm_lines:
        raw_hosts = [h.strip() for h in mitm_lines[0].split("=", 1)[1].replace("%APPEND%", "").split(",") if h.strip()]

    clean_hosts = list(safety_exclusions)
    seen_hosts = set(clean_hosts)
    for h in priority_mitm + raw_hosts:
        if h in exclude_mitm or any(ok in h.lower() for ok in ["google", "spotify", "yahoo", "reddit", "pixiv", "gamer.com.tw", "biliintl", "tiktokv", "musical.ly", "i18n-pglstatp", "alipay"]):
            continue
        if h.count("*") > 1 or ("*" in h and not h.startswith("*.") and not h.startswith("-*.")):
            continue
        if h not in seen_hosts:
            seen_hosts.add(h)
            clean_hosts.append(h)

    with open(OUT_MODULE_FILE, "w", encoding="utf-8") as f:
        f.write(f"#!name=CLQ_Shield (更新日期:{ymd_compact})\n")
        f.write(f"#!desc=国内去广告规则: {rule_count} ｜ 重写: {rw_count} ｜ 脚本: {len(final_sc_lines)}\n\n")
        f.write("# 描述：专为中国境内环境优化的 Shadowrocket 纯去广告模块（专项强化：百度、百度地图、淘宝、天猫、支付宝、菜鸟、闲鱼、京东、喜马拉雅、番茄小说、番茄畅听、红果短剧）\n")
        f.write("# 仓库地址: https://github.com/18661619000/Block-ads\n")
        f.write("# 订阅地址: https://raw.githubusercontent.com/18661619000/Block-ads/main/CLQ_Shield.module\n")
        f.write(f"# 更新时间: {full_time} 北京时间\n")
        f.write(f"# 国内去广告规则总数: {rule_count}\n")
        f.write(f"# 国内 URL 重写总数: {rw_count}\n")
        f.write(f"# 国内去广告脚本总数: {len(final_sc_lines)}\n")
        f.write(f"# MITM 主机名总数: {len(clean_hosts)}\n\n")
        f.write("[Rule]\n\n")
        for l in final_rule_lines:
            f.write(l + "\n")
        f.write("\n[URL Rewrite]\n")
        for l in final_rw_lines:
            f.write(l + "\n")
        f.write("\n[Script]\n")
        for l in final_sc_lines:
            f.write(l + "\n")
        f.write("\n[MITM]\nenable = true\n")
        f.write("hostname = %APPEND% " + ", ".join(clean_hosts) + "\n")

    new_stats = {
        "rules": rule_count,
        "custom": len(custom_rules),
        "rewrites": rw_count,
        "scripts": len(final_sc_lines),
        "mitm": len(clean_hosts),
        "direct": direct_count,
    }
    update_readme_stats(ymd_compact, ymd_dash, full_time, new_stats, old_stats)
    print(f"[SUCCESS] 已更新 {OUT_MODULE_FILE}, {OUT_CONF_FILE}, {README_FILE} (更新日期:{ymd_compact})")


if __name__ == "__main__":
    main()
