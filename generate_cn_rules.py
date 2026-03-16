#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CN 域名规则自动生成脚本
功能：批量抓取、去重、格式化大陆直连域名规则
作者：Auto-generated
版本：1.0.0
"""

import os
import sys
import re
import argparse
import urllib.request
import ssl
import time
from datetime import datetime
from collections import OrderedDict

# ==================== 配置 ====================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_ORGANIZED = os.path.join(BASE_DIR, "organized_cn_mark.txt")
OUTPUT_CUSTOM = os.path.join(BASE_DIR, "custom_cn_mark.txt")
OUTPUT_CUSTOM_SRC = os.path.join(BASE_DIR, "custom.txt")
OUTPUT_LOG = os.path.join(BASE_DIR, "generate.log")

# 数据源配置
SOURCES = {
    "Aethersailor": {
        "priority": 1,
        "files": [
            ("Custom_Direct.list", [
                "https://raw.githubusercontent.com/Aethersailor/Custom_OpenClash_Rules/main/rule/Custom_Direct.list"
            ]),
            ("IPTVMainland_Domain.list", [
                "https://raw.githubusercontent.com/Aethersailor/Custom_OpenClash_Rules/main/rule/IPTVMainland_Domain.list"
            ]),
            ("Steam_CDN.list", [
                "https://github.com/Aethersailor/Custom_OpenClash_Rules/raw/refs/heads/main/rule/Steam_CDN.list"
            ]),
        ]
    },
    "Loyalsoldier": {
        "priority": 2,
        "files": [
            ("direct-list.txt", [
                "https://raw.githubusercontent.com/Loyalsoldier/v2ray-rules-dat/release/direct-list.txt"
            ]),
            ("china-list.txt", [
                "https://raw.githubusercontent.com/Loyalsoldier/v2ray-rules-dat/release/china-list.txt"
            ]),
            ("apple-cn.txt", [
                "https://raw.githubusercontent.com/Loyalsoldier/v2ray-rules-dat/release/apple-cn.txt"
            ]),
            ("google-cn.txt", [
                "https://raw.githubusercontent.com/Loyalsoldier/v2ray-rules-dat/release/google-cn.txt"
            ]),
        ]
    },
    "v2fly": {
        "priority": 3,
        "files": [
            ("dlc.dat_plain.yml", [
                "https://raw.githubusercontent.com/v2fly/domain-list-community/release/dlc.dat_plain.yml"
            ]),
        ]
    }
}

# 备用下载策略
FALLBACK_URLS = {
    "raw.githubusercontent.com": "https://cdn.jsdelivr.net/gh/{path}",
    "github.com": "https://ghfast.top/https://github.com/{path}"
}

# ==================== 工具函数 ====================

def log(msg, file_handle=None):
    """日志输出"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_msg = f"[{timestamp}] {msg}"
    print(log_msg)
    if file_handle:
        file_handle.write(log_msg + "\n")

def get_jsdelivr_url(url):
    """将 raw.githubusercontent.com URL 转换为 JsDelivr CDN URL"""
    # 原始: https://raw.githubusercontent.com/用户名/仓库名/分支/路径
    # 转换: https://cdn.jsdelivr.net/gh/用户名/仓库名@分支/路径
    if "raw.githubusercontent.com" not in url:
        return None
    
    # 提取路径
    path = url.replace("https://raw.githubusercontent.com/", "")
    parts = path.split("/")
    
    if len(parts) >= 3:
        username = parts[0]
        repo = parts[1]
        branch = parts[2]
        file_path = "/".join(parts[3:])
        
        return f"https://cdn.jsdelivr.net/gh/{username}/{repo}@{branch}/{file_path}"
    
    return None

def get_fallback_urls(url):
    """获取备用URL列表"""
    urls = []
    parsed = urllib.parse.urlparse(url)
    
    if parsed.netloc == "raw.githubusercontent.com":
        # JsDelivr CDN
        jsdelivr_url = get_jsdelivr_url(url)
        if jsdelivr_url:
            urls.append(jsdelivr_url)
    
    elif parsed.netloc == "github.com":
        # ghfast.top 代理
        urls.append(f"https://ghfast.top/{url}")
    
    return urls

def download_file_with_fallback(url, timeout=60, verbose=False, use_fallback_direct=False, max_retries=3):
    """下载文件，支持备用URL
    
    Args:
        url: 原始URL
        timeout: 超时时间
        verbose: 是否显示详细输出
        use_fallback_direct: 是否直接使用备用链接
        max_retries: 最大重试次数
    """
    # 确定要尝试的URL列表
    if use_fallback_direct:
        # 直接使用备用链接
        all_urls = get_fallback_urls(url)
        if not all_urls:
            all_urls = [url]
    else:
        all_urls = [url] + get_fallback_urls(url)
    
    for attempt, try_url in enumerate(all_urls):
        if verbose:
            retry_msg = f" (重试 {attempt + 1}/{max_retries})" if attempt > 0 else ""
            log(f"    尝试: {try_url[:60]}...{retry_msg}")
        
        content = download_file(try_url, timeout)
        
        # 检查下载是否正常
        if content and len(content) > 10:
            # 检查是否包含有效内容（不是错误页面）
            if "404" not in content[:200] and "Not Found" not in content[:200]:
                return content
            else:
                if verbose:
                    log(f"    下载返回404，跳过")
        elif content:
            if verbose:
                log(f"    下载内容过短，可能失败")
    
    return None

def download_file(url, timeout=60):
    """下载文件"""
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as response:
            return response.read().decode('utf-8')
    except Exception as e:
        log(f"下载失败 {url}: {e}")
        return None

def parse_domain_rule(line, source):
    """解析域名规则"""
    line = line.strip()
    if not line or line.startswith('#'):
        return None
    
    # 移除行号标记 (如 1. )
    line = re.sub(r'^\d+\.\s*', '', line)
    
    domain = None
    rule_type = "domain"  # 默认
    
    # 处理不同格式
    if line.startswith('DOMAIN-SUFFIX,'):
        domain = line.replace('DOMAIN-SUFFIX,', '').strip()
        rule_type = "domain"
    elif line.startswith('DOMAIN,'):
        domain = line.replace('DOMAIN,', '').strip()
        rule_type = "full"
    elif line.startswith('DOMAIN-KEYWORD,'):
        domain = line.replace('DOMAIN-KEYWORD,', '').strip()
        rule_type = "keyword"
    elif line.startswith('full:'):
        domain = line.replace('full:', '').strip()
        rule_type = "full"
    elif line.startswith('domain:'):
        domain = line.replace('domain:', '').strip()
        rule_type = "domain"
    elif line.startswith('keyword:'):
        domain = line.replace('keyword:', '').strip()
        rule_type = "keyword"
    elif line.startswith('regexp:'):
        domain = line.replace('regexp:', '').strip()
        rule_type = "regexp"
    elif '.' in line and not line.startswith('#'):
        # 裸域名
        domain = line
        rule_type = "domain"
    else:
        return None
    
    if not domain:
        return None
    
    # 清理域名
    domain = domain.lower().strip()
    
    # 跳过无效域名
    if not re.match(r'^[a-z0-9\-\*\.\*]+$', domain):
        return None
    
    return {
        "domain": domain,
        "type": rule_type,
        "source": source,
        "original": line
    }

def parse_dlc_yml(content, source_name="v2fly"):
    """解析 dlc.dat_plain.yml 文件，提取 *-cn 分类"""
    rules = []
    current_category = None
    in_rules_section = False
    
    for line in content.split('\n'):
        stripped = line.strip()
        
        # 提取分类名 (在 - name: 这一行)
        if '- name:' in line and not stripped.startswith('#'):
            match = re.search(r'- name:\s*(\S+)', line)
            if match:
                current_category = match.group(1)
                in_rules_section = False
        
        # 检测 rules 部分开始
        if stripped == 'rules:':
            in_rules_section = True
        
        # 提取域名规则 (在 rules 部分内)
        if in_rules_section and current_category and '-cn' in current_category:
            if stripped.startswith('- "'):
                # 提取域名
                match = re.search(r'- "(domain|full|keyword):(.+)"', stripped)
                if match:
                    rule_type = match.group(1)
                    domain = match.group(2)
                    
                    rules.append({
                        "domain": domain,
                        "type": rule_type,
                        "source": source_name,
                        "category": current_category,
                        "original": f"{rule_type}:{domain}"
                    })
    
    return rules

def convert_to_paopaodns_format(rule_type, domain):
    """转换为 PaoPaoDNS 格式"""
    prefix = f"{rule_type}:"
    
    # 如果已经是 PaoPaoDNS 格式，直接返回
    if domain.startswith(('domain:', 'full:', 'keyword:', 'regexp:')):
        return domain
    
    # 处理通配符
    if domain.startswith('*') and domain.endswith('*'):
        domain = domain.strip('*')
        return f"keyword:{domain}"
    elif domain.startswith('+.'):
        domain = domain[2:]
        return f"domain:{domain}"
    elif domain.startswith('*'):
        domain = domain[1:]
        return f"keyword:{domain}"
    else:
        return f"{prefix}{domain}"

def deduplicate_rules(rules):
    """去重，保留最高优先级"""
    # 按优先级排序
    priority_map = {"Aethersailor": 1, "Loyalsoldier": 2, "v2fly": 3, "custom": 4}
    
    # 使用 OrderedDict 按域名分组
    seen = {}
    
    for rule in rules:
        domain = rule["domain"]
        source = rule["source"]
        priority = priority_map.get(source, 99)
        
        key = domain
        
        if key not in seen:
            seen[key] = rule
        else:
            # 比较优先级
            existing_priority = priority_map.get(seen[key]["source"], 99)
            if priority < existing_priority:
                seen[key] = rule
    
    return list(seen.values())

def load_custom_rules(filepath):
    """加载自定义规则"""
    if not os.path.exists(filepath):
        return []
    
    rules = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            rule = parse_domain_rule(line, "custom")
            if rule:
                rules.append(rule)
    
    return rules

# ==================== 主流程 ====================

def generate_rules(args):
    """生成规则文件"""
    all_rules = []
    
    # 创建日志文件
    log_file = open(OUTPUT_LOG, 'w', encoding='utf-8') if args.log else None
    if log_file:
        log("开始生成 CN 域名规则", log_file)
    
    # 步骤 1-3: 抓取各源规则
    for source_name, source_config in SOURCES.items():
        if args.verbose:
            log(f"正在处理 {source_name} 源...", log_file)
        
        priority = source_config["priority"]
        
        for filename, urls in source_config["files"]:
            if args.verbose:
                log(f"  下载: {filename}", log_file)
            
            # 尝试下载（支持多个URL备用）
            content = None
            
            if isinstance(urls, str):
                urls = [urls]  # 兼容旧格式
            
            for url in urls:
                if args.verbose:
                    log(f"    尝试: {url[:60]}...", log_file)
                content = download_file_with_fallback(
                    url, 
                    timeout=180 if source_name == "v2fly" else 60, 
                    verbose=args.verbose,
                    use_fallback_direct=args.use_fallback
                )
                if content:
                    break
            
            if not content:
                error_msg = f"错误: {filename} 下载失败，脚本退出"
                log(error_msg, log_file)
                if log_file:
                    log_file.close()
                print(error_msg)
                sys.exit(1)
            
            # 解析内容
            if source_name == "v2fly":
                # 特殊处理 v2fly yml
                rules = parse_dlc_yml(content, source_name)
            else:
                rules = []
                for line in content.split('\n'):
                    rule = parse_domain_rule(line, source_name)
                    if rule:
                        rules.append(rule)
            
            # 检查规则数量
            if len(rules) == 0:
                error_msg = f"错误: {filename} 解析规则为0，可能网络错误或链接无效，脚本退出"
                log(error_msg, log_file)
                if log_file:
                    log_file.close()
                print(error_msg)
                sys.exit(1)
            
            all_rules.extend(rules)
            log(f"  获取 {len(rules)} 条规则: {filename}", log_file)
    
    # 步骤 4: 本地自定义规则
    if os.path.exists(OUTPUT_CUSTOM_SRC):
        log(f"加载本地自定义规则: {OUTPUT_CUSTOM_SRC}", log_file)
        custom_rules = load_custom_rules(OUTPUT_CUSTOM_SRC)
        all_rules.extend(custom_rules)
        log(f"  添加 {len(custom_rules)} 条自定义规则", log_file)
    
    # 步骤 5: 全局去重
    log(f"去重前共 {len(all_rules)} 条规则", log_file)
    all_rules = deduplicate_rules(all_rules)
    log(f"去重后共 {len(all_rules)} 条规则", log_file)
    
    # 步骤 6: 清理失效规则 (已在上一步处理)
    
    # 步骤 7: 合并自定义域名
    # 已经在步骤4处理
    
    # 步骤 8: 生成输出文件
    
    # 生成 organized_cn_mark.txt (原始规则)
    with open(OUTPUT_ORGANIZED, 'w', encoding='utf-8') as f:
        f.write("# ============================================\n")
        f.write("# CN 域名规则列表 (原始格式)\n")
        f.write(f"# 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("# ============================================\n")
        f.write("\n")
        
        # 按来源分组
        current_source = None
        for rule in all_rules:
            if rule["source"] != current_source:
                current_source = rule["source"]
                f.write(f"\n# --- {current_source} ---\n")
            
            f.write(f"{rule['original']}\n")
    
    log(f"生成原始规则文件: {OUTPUT_ORGANIZED}", log_file)
    
    # 生成 custom_cn_mark.txt (格式化)
    with open(OUTPUT_CUSTOM, 'w', encoding='utf-8') as f:
        f.write("# ============================================\n")
        f.write("# PaoPaoDNS CN 标记域名列表\n")
        f.write(f"# 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("# ============================================\n")
        f.write("# \n")
        f.write("# 格式说明:\n")
        f.write("#   domain:xxx - 域名后缀匹配 (包含子域名)\n")
        f.write("#   full:xxx  - 完整精确匹配\n")
        f.write("#   keyword:xxx - 关键字匹配\n")
        f.write("#   regexp:xxx - 正则匹配\n")
        f.write("# ============================================\n")
        f.write("\n")
        
        for rule in all_rules:
            formatted = convert_to_paopaodns_format(rule["type"], rule["domain"])
            f.write(f"{formatted}\n")
    
    log(f"生成格式化规则文件: {OUTPUT_CUSTOM}", log_file)
    
    if log_file:
        log_file.close()
    
    print(f"\n完成！")
    print(f"  原始规则: {OUTPUT_ORGANIZED}")
    print(f"  格式化规则: {OUTPUT_CUSTOM}")
    print(f"  总规则数: {len(all_rules)}")

def show_help():
    """显示帮助信息"""
    help_text = """
╔════════════════════════════════════════════════════════════════╗
║           CN 域名规则自动生成脚本 v1.0.0                     ║
╚════════════════════════════════════════════════════════════════╝

【脚本功能】
  批量抓取、去重、格式化中国大陆直连域名规则

【支持平台】
  Windows / macOS / Linux

【执行方式】
  python3 generate_cn_rules.py [选项]

【数据源优先级】
  1. Aethersailor (最高优先级)
  2. Loyalsoldier
  3. v2fly
  4. 本地自定义 (custom.txt)

【命令行参数】
  --help, -h       显示帮助信息
  --verbose, -v    显示详细输出
  --log            生成日志文件
  --no-download    跳过下载，仅处理现有文件
  -f, --use-fallback  直接使用备用链接下载（大陆环境）

【输出文件】
  organized_cn_mark.txt  - 合并去重后的原始规则文件
  custom_cn_mark.txt     - 格式化后的最终规则文件 (PaoPaoDNS 使用)
  custom.txt            - 个人自定义规则文件 (可选)
  generate.log          - 日志文件 (可选)

【自定义规则格式】
  支持以下格式:
  - DOMAIN-SUFFIX,example.com
  - DOMAIN,example.com
  - full:example.com
  - domain:example.com
  - example.com (裸域名)

【注意事项】
  1. 需要网络连接以下载规则文件
  2. 如果规则解析为0，脚本会报错退出（可能是网络问题）
  3. 使用 -f 参数可直接使用备用链接（适用于大陆网络环境）
  2. 运行时会覆盖已有的输出文件
  3. v2fly 源文件较大，下载可能需要较长时间

【示例】
  python3 generate_cn_rules.py           # 执行生成
  python3 generate_cn_rules.py -v        # 详细输出
  python3 generate_cn_rules.py --log      # 生成日志

"""
    print(help_text)

# ==================== 入口 ====================

if __name__ == "__main__":
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("-h", "--help", action="store_true")
    parser.add_argument("-v", "--verbose", action="store_true")
    parser.add_argument("--log", action="store_true")
    parser.add_argument("--no-download", action="store_true")
    parser.add_argument("-f", "--use-fallback", action="store_true", help="直接使用备用链接下载（大陆环境）")
    
    args = parser.parse_args()
    
    if args.help:
        show_help()
    else:
        generate_rules(args)
