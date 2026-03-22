#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CN 域名规则自动生成脚本
功能：批量抓取、去重、格式化大陆直连域名规则
作者：Auto-generated
版本：2.0.0
"""

import argparse
import concurrent.futures
import fnmatch
import hashlib
import os
import re
import socket
import ssl
import sys
import threading
import time
import urllib.parse
import urllib.request
from datetime import datetime


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_ORGANIZED = os.path.join(BASE_DIR, "organized_cn_mark.txt")
OUTPUT_CUSTOM = os.path.join(BASE_DIR, "custom_cn_mark.txt")
OUTPUT_CUSTOM_SRC = os.path.join(BASE_DIR, "custom.txt")
OUTPUT_CUSTOM_RULE_SRC = os.path.join(BASE_DIR, "custom_rule.txt")
OUTPUT_LOG = os.path.join(BASE_DIR, "generate.log")
CACHE_DIR = os.path.join(BASE_DIR, ".cache")

DOWNLOAD_PRIORITY_HINTS = {
    "Steam_CDN.list": 1,
    "apple-cn.txt": 1,
    "google-cn.txt": 1,
    "Custom_Direct.list": 2,
    "IPTVMainland_Domain.list": 2,
    "direct-list.txt": 10,
    "china-list.txt": 10,
    "dlc.dat_plain.yml": 20,
}

SOURCES = {
    "Aethersailor": {
        "display_name": "Custom_OpenClash_Rules",
        "priority": 1,
        "files": [
            (
                "Custom_Direct.list",
                [
                    "https://raw.githubusercontent.com/Aethersailor/Custom_OpenClash_Rules/main/rule/Custom_Direct.list",
                ],
            ),
            (
                "IPTVMainland_Domain.list",
                [
                    "https://raw.githubusercontent.com/Aethersailor/Custom_OpenClash_Rules/main/rule/IPTVMainland_Domain.list",
                ],
            ),
            (
                "Steam_CDN.list",
                [
                    "https://github.com/Aethersailor/Custom_OpenClash_Rules/raw/refs/heads/main/rule/Steam_CDN.list",
                ],
            ),
        ],
    },
    "Loyalsoldier": {
        "display_name": "v2ray-rules-dat",
        "priority": 2,
        "files": [
            (
                "direct-list.txt",
                [
                    "https://raw.githubusercontent.com/Loyalsoldier/v2ray-rules-dat/release/direct-list.txt",
                ],
            ),
            (
                "china-list.txt",
                [
                    "https://raw.githubusercontent.com/Loyalsoldier/v2ray-rules-dat/release/china-list.txt",
                ],
            ),
            (
                "apple-cn.txt",
                [
                    "https://raw.githubusercontent.com/Loyalsoldier/v2ray-rules-dat/release/apple-cn.txt",
                ],
            ),
            (
                "google-cn.txt",
                [
                    "https://raw.githubusercontent.com/Loyalsoldier/v2ray-rules-dat/release/google-cn.txt",
                ],
            ),
        ],
    },
    "v2fly": {
        "display_name": "domain-list-community",
        "priority": 3,
        "files": [
            (
                "dlc.dat_plain.yml",
                [
                    "https://github.com/v2fly/domain-list-community/releases/latest/download/dlc.dat_plain.yml",
                    "https://raw.githubusercontent.com/v2fly/domain-list-community/release/dlc.dat_plain.yml",
                ],
            ),
        ],
    },
}

RULE_SOURCE_PRIORITIES = {
    **{name: config["priority"] for name, config in SOURCES.items()},
    "custom_rule": 4,
    "custom": 5,
}

RULE_MATCH_PRIORITIES = {
    "full": 1,
    "domain": 2,
    "regexp": 3,
    "keyword": 4,
}

CUSTOM_OUTPUT_SECTION_PRIORITIES = {
    "custom": 1,
    "custom_rule": 2,
    "generated": 3,
}

CUSTOM_OUTPUT_SECTION_TITLES = {
    "custom": "用户自定义规则（编辑 custom.txt）",
    "custom_rule": "第三方规则链接导入（编辑 custom_rule.txt）",
    "generated": "自动聚合规则（请勿直接修改）",
}

SOURCE_ALIASES = {
    "aethersailor": "Aethersailor",
    "custom_openclash_rules": "Aethersailor",
    "custom-openclash-rules": "Aethersailor",
    "loyalsoldier": "Loyalsoldier",
    "v2ray_rules_dat": "Loyalsoldier",
    "v2ray-rules-dat": "Loyalsoldier",
    "v2fly": "v2fly",
    "domain_list_community": "v2fly",
    "domain-list-community": "v2fly",
}

LOG_LOCK = threading.Lock()
ACTIVE_PROGRESS = None


def log(message, file_handle=None):
    """线程安全日志输出。"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"[{timestamp}] {message}"
    with LOG_LOCK:
        global ACTIVE_PROGRESS
        if ACTIVE_PROGRESS:
            ACTIVE_PROGRESS.clear_line()
        print(log_message)
        if file_handle:
            file_handle.write(log_message + "\n")
            file_handle.flush()


def format_size(num_bytes):
    """格式化字节大小。"""
    value = float(num_bytes)
    for unit in ["B", "KB", "MB", "GB"]:
        if value < 1024 or unit == "GB":
            return f"{value:.1f}{unit}"
        value /= 1024
    return f"{value:.1f}GB"


def format_rate(num_bytes_per_second):
    """格式化速率。"""
    return f"{format_size(num_bytes_per_second)}/s"


class DownloadProgress:
    """下载进度展示。"""

    def __init__(self, total_tasks, enabled=True):
        self.total_tasks = max(total_tasks, 1)
        self.enabled = enabled
        self.completed = 0
        self.lock = threading.Lock()
        self.stats = {}
        self.stop_event = threading.Event()
        self.is_tty = enabled and sys.stdout.isatty()
        self.spinner_frames = ["|", "/", "-", "\\"]
        self.spinner_index = 0
        self.last_line_length = 0
        self.render_thread = None

        global ACTIVE_PROGRESS
        if self.enabled:
            ACTIVE_PROGRESS = self

        if self.is_tty:
            self.render_thread = threading.Thread(target=self._render_loop, daemon=True)
            self.render_thread.start()

    def start_task(self, label):
        if not self.enabled:
            return
        with self.lock:
            self.stats[label] = {
                "status": "running",
                "start_time": time.monotonic(),
                "last_time": time.monotonic(),
                "downloaded": 0,
                "total_bytes": None,
                "from_cache": False,
            }
            if not self.is_tty:
                print(f"[{self.completed}/{self.total_tasks}] 开始 {label}")

    def update(self, label, downloaded, total_bytes):
        if not self.enabled:
            return
        with self.lock:
            stats = self.stats.setdefault(
                label,
                {
                    "status": "running",
                    "start_time": time.monotonic(),
                    "downloaded": 0,
                    "total_bytes": total_bytes,
                    "from_cache": False,
                },
            )
            stats["downloaded"] = downloaded
            stats["total_bytes"] = total_bytes
            stats["last_time"] = time.monotonic()

    def finish_task(self, label, size_bytes, from_cache=False):
        if not self.enabled:
            return
        with self.lock:
            now = time.monotonic()
            stats = self.stats.setdefault(
                label,
                {
                    "status": "finished",
                    "start_time": now,
                    "downloaded": size_bytes,
                    "total_bytes": size_bytes,
                    "from_cache": from_cache,
                },
            )
            stats["status"] = "finished"
            stats["downloaded"] = size_bytes
            stats["total_bytes"] = size_bytes
            stats["from_cache"] = from_cache
            stats["end_time"] = now
            stats["last_time"] = now
            self.completed += 1
            source = "缓存" if from_cache else "下载"
            elapsed = max(0.001, now - stats["start_time"])
            speed = size_bytes / elapsed
            if self.is_tty:
                self._clear_line_locked()
            print(
                f"[{self.completed}/{self.total_tasks}] 完成 {label} "
                f"({source}, {format_size(size_bytes)}, {elapsed:.1f}s, {format_rate(speed)})"
            )

    def fail_task(self, label, message):
        if not self.enabled:
            return
        with self.lock:
            self.stats[label] = {
                "status": "failed",
                "message": message,
                "start_time": time.monotonic(),
                "last_time": time.monotonic(),
                "downloaded": 0,
                "total_bytes": None,
                "from_cache": False,
            }
            if self.is_tty:
                self._clear_line_locked()
            print(f"[{self.completed}/{self.total_tasks}] 失败 {label}: {message}")

    def stop(self):
        if not self.enabled:
            return
        self.stop_event.set()
        if self.render_thread:
            self.render_thread.join(timeout=1)
        if self.is_tty:
            with self.lock:
                self._clear_line_locked()
        global ACTIVE_PROGRESS
        if ACTIVE_PROGRESS is self:
            ACTIVE_PROGRESS = None

    def clear_line(self):
        if not self.enabled or not self.is_tty:
            return
        with self.lock:
            self._clear_line_locked()

    def _render_loop(self):
        while not self.stop_event.is_set():
            with self.lock:
                self._render_locked()
            time.sleep(0.2)
        with self.lock:
            self._clear_line_locked()

    def _render_locked(self):
        now = time.monotonic()
        active_stats = [
            (label, stats)
            for label, stats in self.stats.items()
            if stats.get("status") == "running"
        ]

        spinner = self.spinner_frames[self.spinner_index % len(self.spinner_frames)]
        self.spinner_index += 1

        line = f"{spinner} {self.completed}/{self.total_tasks}"
        if active_stats:
            label, stats = max(
                active_stats,
                key=lambda item: (item[1].get("last_time", 0), item[1].get("downloaded", 0)),
            )
            downloaded = stats.get("downloaded", 0)
            total_bytes = stats.get("total_bytes")
            elapsed = max(0.001, now - stats.get("start_time", now))
            speed = downloaded / elapsed
            short_label = label if len(label) <= 24 else f"{label[:21]}..."
            bar = self._build_bar(downloaded, total_bytes)
            if total_bytes:
                line += (
                    f" {bar} {short_label} {format_size(downloaded)}/{format_size(total_bytes)} "
                    f"{format_rate(speed)}"
                )
            else:
                line += f" {bar} {short_label} {format_size(downloaded)} {format_rate(speed)}"
        self._write_line_locked(line)

    def _build_bar(self, downloaded, total_bytes, width=24):
        if not total_bytes:
            return "[" + "." * width + "]"

        ratio = max(0.0, min(1.0, downloaded / total_bytes))
        filled = min(width, int(ratio * width))
        if filled == width:
            return "[" + "#" * width + "]"
        if filled <= 0:
            return "[" + ">" + "." * (width - 1) + "]"
        return "[" + "#" * filled + ">" + "." * (width - filled - 1) + "]"

    def _write_line_locked(self, line):
        if not self.is_tty:
            return
        padded_line = line
        if len(padded_line) < self.last_line_length:
            padded_line += " " * (self.last_line_length - len(padded_line))
        sys.stdout.write("\r" + padded_line)
        sys.stdout.flush()
        self.last_line_length = len(line)

    def _clear_line_locked(self):
        if not self.is_tty:
            return
        if self.last_line_length:
            sys.stdout.write("\r" + " " * self.last_line_length + "\r")
            sys.stdout.flush()
            self.last_line_length = 0


def flatten_cli_values(values):
    """展开可重复参数和逗号/分号分隔参数。"""
    if not values:
        return []

    flattened = []
    for value in values:
        for item in re.split(r"[;,]", value):
            stripped = item.strip()
            if stripped:
                flattened.append(stripped)
    return flattened


def normalize_source_name(source_name):
    """标准化数据源名称。"""
    if source_name in SOURCES:
        return source_name

    normalized = source_name.strip().lower().replace(" ", "_")
    if normalized in SOURCE_ALIASES:
        return SOURCE_ALIASES[normalized]

    raise RuntimeError(f"错误: 未知数据源 {source_name}")


def resolve_enabled_sources(args):
    """根据参数确定启用的数据源。"""
    enabled_sources = [] if args.no_default_sources else list(SOURCES.keys())

    selected_sources = flatten_cli_values(args.sources)
    if selected_sources:
        enabled_sources = [normalize_source_name(source) for source in selected_sources]

    excluded_sources = {normalize_source_name(source) for source in flatten_cli_values(args.exclude_sources)}
    enabled_sources = [source for source in enabled_sources if source not in excluded_sources]

    deduplicated_sources = []
    for source in enabled_sources:
        if source not in deduplicated_sources:
            deduplicated_sources.append(source)

    return deduplicated_sources


def resolve_geosite_groups(args):
    """解析 v2fly 提取的分类组。"""
    groups = flatten_cli_values(args.geosite_groups)
    if not groups:
        return ["*-cn"]

    deduplicated_groups = []
    for group in groups:
        if group not in deduplicated_groups:
            deduplicated_groups.append(group)
    return deduplicated_groups


def compile_geosite_group_matchers(group_patterns):
    """编译 geosite 分类组匹配器。"""
    matchers = []
    for pattern in group_patterns:
        if pattern.startswith("re:") or pattern.startswith("regex:"):
            _, expression = pattern.split(":", 1)
            expression = expression.strip()
            if not expression:
                raise RuntimeError("错误: geosite 正则表达式不能为空")
            try:
                compiled = re.compile(expression)
            except re.error as exc:
                raise RuntimeError(f"错误: geosite 正则表达式无效 {pattern}: {exc}") from exc
            matchers.append(("regex", compiled))
        else:
            matchers.append(("glob", pattern))
    return matchers


def matches_geosite_group(category, matchers):
    """判断分类组是否匹配 geosite 选择器。"""
    for matcher_type, matcher_value in matchers:
        if matcher_type == "regex":
            if matcher_value.search(category):
                return True
        elif fnmatch.fnmatch(category, matcher_value):
            return True
    return False


def get_jsdelivr_url(url):
    """将 raw.githubusercontent.com URL 转换为 JsDelivr CDN URL。"""
    if "raw.githubusercontent.com" not in url:
        return None

    path = url.replace("https://raw.githubusercontent.com/", "")
    parts = path.split("/")
    if len(parts) < 3:
        return None

    username = parts[0]
    repo = parts[1]
    branch = parts[2]
    file_path = "/".join(parts[3:])
    return f"https://cdn.jsdelivr.net/gh/{username}/{repo}@{branch}/{file_path}"


def get_fastly_jsdelivr_url(url):
    """将 jsDelivr 地址替换为 fastly.jsdelivr.net。"""
    parsed = urllib.parse.urlparse(url)
    if parsed.netloc != "cdn.jsdelivr.net":
        return None
    return urllib.parse.urlunparse(parsed._replace(netloc="fastly.jsdelivr.net"))


def get_fallback_urls(url):
    """获取备用 URL 列表。"""
    parsed = urllib.parse.urlparse(url)
    urls = []

    if parsed.netloc == "raw.githubusercontent.com":
        jsdelivr_url = get_jsdelivr_url(url)
        if jsdelivr_url:
            urls.append(jsdelivr_url)
            fastly_url = get_fastly_jsdelivr_url(jsdelivr_url)
            if fastly_url:
                urls.append(fastly_url)
        urls.append(f"https://ghfast.top/{url}")
    elif parsed.netloc == "cdn.jsdelivr.net":
        fastly_url = get_fastly_jsdelivr_url(url)
        if fastly_url:
            urls.append(fastly_url)
    elif parsed.netloc == "github.com":
        urls.append(f"https://ghfast.top/{url}")

    deduplicated_urls = []
    for item in urls:
        if item not in deduplicated_urls:
            deduplicated_urls.append(item)
    return deduplicated_urls


def build_url_opener(proxy_url=None):
    """构造支持代理的 urllib opener。"""
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE

    handlers = [
        urllib.request.HTTPHandler(),
        urllib.request.HTTPSHandler(context=context),
    ]

    if proxy_url:
        handlers.insert(0, urllib.request.ProxyHandler({"http": proxy_url, "https": proxy_url}))

    return urllib.request.build_opener(*handlers)


def apply_socket_timeout(response, timeout):
    """尽量给底层 socket 设置读取超时。"""
    stack = [response]
    seen = set()
    attrs_to_visit = ("fp", "raw", "_fp", "_sock", "sock", "buffer")

    while stack:
        current = stack.pop()
        if current is None:
            continue
        identifier = id(current)
        if identifier in seen:
            continue
        seen.add(identifier)

        settimeout = getattr(current, "settimeout", None)
        if callable(settimeout):
            try:
                settimeout(timeout)
                return True
            except Exception:
                pass

        for attr in attrs_to_visit:
            try:
                child = getattr(current, attr, None)
            except Exception:
                child = None
            if child is not None:
                stack.append(child)

    return False


def download_file(url, timeout=10, proxy_url=None, progress=None, progress_label=None):
    """下载文件内容。"""
    try:
        opener = build_url_opener(proxy_url)
        request = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"},
        )

        with opener.open(request, timeout=timeout) as response:
            apply_socket_timeout(response, timeout)
            total_bytes = response.length
            downloaded = 0
            chunks = []

            while True:
                chunk = response.read(256 * 1024)
                if not chunk:
                    break

                chunks.append(chunk)
                downloaded += len(chunk)
                if progress and progress_label:
                    progress.update(progress_label, downloaded, total_bytes)

            return b"".join(chunks).decode("utf-8", errors="replace")
    except socket.timeout:
        log(f"下载失败 {url}: 网络超时或长时间 0B/s（>{timeout}s）")
        return None
    except Exception as exc:
        log(f"下载失败 {url}: {exc}")
        return None


def download_file_with_fallback(
    url,
    timeout=10,
    verbose=False,
    use_fallback_direct=False,
    retries=2,
    proxy_url=None,
    progress=None,
    progress_label=None,
):
    """下载文件并自动切换镜像。"""
    if use_fallback_direct:
        all_urls = get_fallback_urls(url) or [url]
    else:
        all_urls = [url] + get_fallback_urls(url)

    for url_index, try_url in enumerate(all_urls):
        for retry_index in range(retries):
            if verbose:
                retry_msg = f" (重试 {retry_index + 1}/{retries})" if retry_index > 0 else ""
                log(f"    尝试: {try_url[:90]}...{retry_msg}")

            content = download_file(
                try_url,
                timeout=timeout,
                proxy_url=proxy_url,
                progress=progress,
                progress_label=progress_label,
            )

            if content and len(content) > 10 and "404" not in content[:200] and "Not Found" not in content[:200]:
                return content

            if verbose and retry_index + 1 < retries:
                log("    当前地址响应异常，准备重试")
            if retry_index + 1 < retries:
                time.sleep(1)

        if url_index + 1 < len(all_urls) and verbose:
            log("    当前地址多次失败，切换下一个镜像")

    return None


def normalize_rule_value(rule_type, value):
    """根据规则类型规范化值。"""
    value = value.strip()
    if not value:
        return None

    if rule_type == "regexp":
        return value

    normalized = value.lower()
    if not re.fullmatch(r"[a-z0-9\-*.]+", normalized):
        return None
    return normalized


def parse_domain_rule(line, source):
    """解析域名规则。"""
    line = line.strip()
    if not line or line.startswith("#"):
        return None

    line = re.sub(r"^\d+\.\s*", "", line)

    domain = None
    rule_type = "domain"

    if line.startswith("DOMAIN-SUFFIX,"):
        domain = line.replace("DOMAIN-SUFFIX,", "", 1).strip()
        rule_type = "domain"
    elif line.startswith("DOMAIN,"):
        domain = line.replace("DOMAIN,", "", 1).strip()
        rule_type = "full"
    elif line.startswith("DOMAIN-KEYWORD,"):
        domain = line.replace("DOMAIN-KEYWORD,", "", 1).strip()
        rule_type = "keyword"
    elif line.startswith("full:"):
        domain = line.replace("full:", "", 1).strip()
        rule_type = "full"
    elif line.startswith("domain:"):
        domain = line.replace("domain:", "", 1).strip()
        rule_type = "domain"
    elif line.startswith("keyword:"):
        domain = line.replace("keyword:", "", 1).strip()
        rule_type = "keyword"
    elif line.startswith("regexp:"):
        domain = line.replace("regexp:", "", 1).strip()
        rule_type = "regexp"
    elif "." in line:
        domain = line
        rule_type = "domain"
    else:
        return None

    normalized_domain = normalize_rule_value(rule_type, domain)
    if normalized_domain is None:
        return None

    return {
        "domain": normalized_domain,
        "type": rule_type,
        "source": source,
        "original": line,
    }


def parse_dlc_yml(content, source_name="v2fly", group_patterns=None):
    """解析 dlc.dat_plain.yml 并按分类组筛选域名。"""
    patterns = group_patterns or ["*-cn"]
    matchers = compile_geosite_group_matchers(patterns)
    rules = []
    current_category = None
    current_category_selected = False
    in_rules_section = False

    for line in content.splitlines():
        stripped = line.strip()

        if "- name:" in line and not stripped.startswith("#"):
            match = re.search(r"- name:\s*(\S+)", line)
            if match:
                current_category = match.group(1)
                current_category_selected = matches_geosite_group(current_category, matchers)
                in_rules_section = False
            continue

        if stripped == "rules:":
            in_rules_section = True
            continue

        if not (in_rules_section and current_category_selected and stripped.startswith('- "')):
            continue

        match = re.search(r'- "(domain|full|keyword|regexp):(.+)"', stripped)
        if not match:
            continue

        rule_type = match.group(1)
        domain = match.group(2)
        rules.append(
            {
                "domain": domain,
                "type": rule_type,
                "source": source_name,
                "category": current_category,
                "original": f"{rule_type}:{domain}",
            }
        )

    return rules


def convert_to_paopaodns_format(rule_type, domain):
    """转换为 PaoPaoDNS 格式。"""
    prefix = f"{rule_type}:"

    if domain.startswith(("domain:", "full:", "keyword:", "regexp:")):
        return domain

    if domain.startswith("*") and domain.endswith("*"):
        return f"keyword:{domain.strip('*')}"
    if domain.startswith("+."):
        return f"domain:{domain[2:]}"
    if domain.startswith("*"):
        return f"keyword:{domain[1:]}"
    return f"{prefix}{domain}"


def parse_rule_content(content, source_name, geosite_groups=None):
    """根据来源解析规则内容。"""
    if source_name == "v2fly":
        return parse_dlc_yml(content, source_name=source_name, group_patterns=geosite_groups)

    rules = []
    for line in content.splitlines():
        rule = parse_domain_rule(line, source_name)
        if rule:
            rules.append(rule)
    return rules


def deduplicate_rules(rules):
    """去重，保留最高优先级。"""
    seen = {}
    for rule in rules:
        key = (rule["type"], rule["domain"])
        priority = RULE_SOURCE_PRIORITIES.get(rule["source"], 99)

        if key not in seen:
            seen[key] = rule
            continue

        existing_priority = RULE_SOURCE_PRIORITIES.get(seen[key]["source"], 99)
        if priority < existing_priority:
            seen[key] = rule

    return list(seen.values())


def get_custom_output_section(source_name):
    """返回 custom_cn_mark.txt 的输出分组。"""
    if source_name == "custom":
        return "custom"
    if source_name == "custom_rule":
        return "custom_rule"
    return "generated"


def sort_rules_for_custom_output(rules):
    """按输出分组和匹配优先级排序。"""
    indexed_rules = list(enumerate(rules))
    indexed_rules.sort(
        key=lambda item: (
            CUSTOM_OUTPUT_SECTION_PRIORITIES.get(get_custom_output_section(item[1]["source"]), 99),
            RULE_MATCH_PRIORITIES.get(item[1]["type"], 99),
            item[0],
        )
    )
    return [rule for _, rule in indexed_rules]


def group_rules_for_custom_output(rules):
    """按输出分组整理规则。"""
    grouped = {section: [] for section in CUSTOM_OUTPUT_SECTION_PRIORITIES}
    for rule in sort_rules_for_custom_output(rules):
        grouped[get_custom_output_section(rule["source"])].append(rule)
    return grouped


def load_custom_rules(filepath):
    """加载自定义规则。"""
    if not os.path.exists(filepath):
        return []

    rules = []
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            rule = parse_domain_rule(line, "custom")
            if rule:
                rules.append(rule)
    return rules


def load_rule_source_urls(filepath):
    """读取第三方规则链接列表。"""
    if not os.path.exists(filepath):
        return []

    urls = []
    with open(filepath, "r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue

            parsed = urllib.parse.urlparse(stripped)
            if parsed.scheme not in {"http", "https"} or not parsed.netloc:
                raise RuntimeError(f"错误: {os.path.basename(filepath)} 第 {line_no} 行不是有效链接: {stripped}")

            urls.append(stripped)
    return urls


def get_cache_file_path(source_name, filename):
    """获取缓存文件路径。"""
    safe_source = re.sub(r"[^a-zA-Z0-9._-]+", "_", source_name)
    safe_filename = re.sub(r"[^a-zA-Z0-9._-]+", "_", filename)
    return os.path.join(CACHE_DIR, f"{safe_source}__{safe_filename}")


def save_cache_file(source_name, filename, content):
    """保存内容到缓存。"""
    os.makedirs(CACHE_DIR, exist_ok=True)
    cache_path = get_cache_file_path(source_name, filename)
    with open(cache_path, "w", encoding="utf-8") as f:
        f.write(content)


def load_cache_file(source_name, filename):
    """从缓存读取内容。"""
    cache_path = get_cache_file_path(source_name, filename)
    if not os.path.exists(cache_path):
        return None
    with open(cache_path, "r", encoding="utf-8") as f:
        return f.read()


def build_remote_cache_name(url):
    """为远程规则链接生成稳定缓存文件名。"""
    parsed = urllib.parse.urlparse(url)
    basename = os.path.basename(parsed.path) or "remote_rules.txt"
    safe_basename = re.sub(r"[^a-zA-Z0-9._-]+", "_", basename)
    digest = hashlib.sha256(url.encode("utf-8")).hexdigest()[:12]
    return f"{digest}_{safe_basename}"


def build_fetch_jobs(enabled_sources, custom_rule_urls, timeout):
    """构造下载任务列表。"""
    jobs = []
    order = 0

    for source_name in enabled_sources:
        source_config = SOURCES[source_name]
        for filename, urls in source_config["files"]:
            jobs.append(
                {
                    "order": order,
                    "source_name": source_name,
                    "filename": filename,
                    "urls": list(urls),
                    "timeout": timeout,
                    "display_label": f"{source_name}/{filename}",
                    "download_priority": DOWNLOAD_PRIORITY_HINTS.get(filename, 5),
                }
            )
            order += 1

    for url in custom_rule_urls:
        cache_name = build_remote_cache_name(url)
        jobs.append(
            {
                "order": order,
                "source_name": "custom_rule",
                "filename": cache_name,
                "urls": [url],
                "timeout": timeout,
                "display_label": f"custom_rule/{cache_name}",
                "original_url": url,
                "download_priority": 1,
            }
        )
        order += 1

    return jobs


def fetch_job(job, args, progress, log_file=None):
    """执行单个下载任务。"""
    display_label = job["display_label"]
    if args.verbose:
        action = "读取缓存" if args.no_download else "下载"
        log(f"{action}: {display_label}", log_file)

    if args.no_download:
        content = load_cache_file(job["source_name"], job["filename"])
        if content is None:
            progress.fail_task(display_label, "缓存不存在")
            raise RuntimeError(f"错误: {job['filename']} 缓存不存在，无法在 --no-download 模式下继续")
        progress.finish_task(display_label, len(content.encode("utf-8")), from_cache=True)
        return {**job, "content": content}

    progress.start_task(display_label)
    content = None
    for url in job["urls"]:
        content = download_file_with_fallback(
            url,
            timeout=job["timeout"],
            verbose=args.verbose,
            use_fallback_direct=args.use_fallback,
            retries=args.retries,
            proxy_url=args.proxy,
            progress=progress,
            progress_label=display_label,
        )
        if content:
            save_cache_file(job["source_name"], job["filename"], content)
            progress.finish_task(display_label, len(content.encode("utf-8")), from_cache=False)
            return {**job, "content": content}

    progress.fail_task(display_label, "所有镜像均失败")
    raise RuntimeError(f"错误: {job['filename']} 下载失败，脚本退出")


def fetch_all_jobs(jobs, args, log_file=None):
    """并发执行全部下载任务。"""
    if not jobs:
        return []

    progress = DownloadProgress(total_tasks=len(jobs), enabled=args.progress)
    results = [None] * len(jobs)
    max_workers = max(1, min(args.threads, len(jobs)))
    ordered_jobs = sorted(jobs, key=lambda job: (job["download_priority"], job["order"]))
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)
    try:
        future_map = {
            executor.submit(fetch_job, job, args, progress, log_file): job for job in ordered_jobs
        }
        for future in concurrent.futures.as_completed(future_map):
            job = future_map[future]
            result = future.result()
            results[job["order"]] = result
    except BaseException:
        executor.shutdown(wait=False, cancel_futures=True)
        progress.stop()
        raise
    else:
        executor.shutdown(wait=True, cancel_futures=False)
        progress.stop()
        return [result for result in results if result is not None]


def build_argument_parser():
    """构建命令行参数解析器。"""
    parser = argparse.ArgumentParser(
        description="批量抓取、去重并生成中国大陆直连域名规则。",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="显示详细输出")
    parser.add_argument("-l", "--log", action="store_true", help="生成日志文件")
    parser.add_argument("-n", "--no-download", action="store_true", help="跳过网络下载，仅使用缓存")
    parser.add_argument("-f", "--use-fallback", action="store_true", help="优先使用备用镜像下载")
    parser.add_argument("-p", "--proxy", help="下载代理地址，例如 http://127.0.0.1:7890")
    parser.add_argument("-t", "--threads", type=int, default=6, help="并发下载线程数")
    parser.add_argument("-T", "--timeout", type=int, default=10, help="网络超时时间（秒），也用于判定长时间 0B/s")
    parser.add_argument("-r", "--retries", type=int, default=2, help="每个镜像地址的重试次数")
    parser.add_argument("-P", "--no-progress", dest="progress", action="store_false", help="关闭下载进度展示")
    parser.set_defaults(progress=True)

    parser.add_argument("-N", "--no-default-sources", action="store_true", help="不使用默认上游规则源")
    parser.add_argument("-s", "--source", dest="sources", action="append", help="仅启用指定默认数据源，可重复或逗号/分号分隔")
    parser.add_argument("-x", "--exclude-source", dest="exclude_sources", action="append", help="排除指定默认数据源，可重复或逗号/分号分隔")
    parser.add_argument("-L", "--list-sources", action="store_true", help="列出可用默认数据源并退出")

    parser.add_argument(
        "-g",
        "--geosite-group",
        dest="geosite_groups",
        action="append",
        help="指定从 dlc.dat_plain.yml 中提取的 geosite 分类组，可重复或逗号/分号分隔；支持 re:正则；默认使用 *-cn",
    )

    return parser


def generate_rules(args):
    """生成规则文件。"""
    all_rules = []
    log_file = open(OUTPUT_LOG, "w", encoding="utf-8") if args.log else None

    try:
        log("开始生成 CN 域名规则", log_file)
        log(
            f"下载设置: 线程={args.threads}, 超时={args.timeout}s, 重试={args.retries}, "
            f"备用镜像={'开' if args.use_fallback else '关'}, 进度={'开' if args.progress else '关'}",
            log_file,
        )
        if args.proxy:
            log(f"下载代理: {args.proxy}", log_file)

        geosite_groups = resolve_geosite_groups(args)
        enabled_sources = resolve_enabled_sources(args)
        log(
            "启用默认上游: " + (", ".join(enabled_sources) if enabled_sources else "无"),
            log_file,
        )
        if "v2fly" in enabled_sources:
            log(f"v2fly 提取分类组: {', '.join(geosite_groups)}", log_file)

        custom_rule_urls = load_rule_source_urls(OUTPUT_CUSTOM_RULE_SRC)
        if custom_rule_urls:
            log(f"第三方规则链接数: {len(custom_rule_urls)}", log_file)
        jobs = build_fetch_jobs(enabled_sources, custom_rule_urls, timeout=args.timeout)
        fetched_results = fetch_all_jobs(jobs, args, log_file)

        for result in fetched_results:
            rules = parse_rule_content(
                result["content"],
                result["source_name"],
                geosite_groups=geosite_groups,
            )
            if not rules:
                raise RuntimeError(f"错误: {result['filename']} 解析规则为 0，可能网络错误或链接无效")

            all_rules.extend(rules)
            label = result.get("original_url", result["filename"])
            log(f"获取 {len(rules)} 条规则: {label}", log_file)

        if os.path.exists(OUTPUT_CUSTOM_SRC):
            log(f"加载本地自定义规则: {OUTPUT_CUSTOM_SRC}", log_file)
            custom_rules = load_custom_rules(OUTPUT_CUSTOM_SRC)
            all_rules.extend(custom_rules)
            log(f"添加 {len(custom_rules)} 条自定义规则", log_file)

        log(f"去重前共 {len(all_rules)} 条规则", log_file)
        all_rules = deduplicate_rules(all_rules)
        log(f"去重后共 {len(all_rules)} 条规则", log_file)

        with open(OUTPUT_ORGANIZED, "w", encoding="utf-8") as f:
            f.write("# ============================================\n")
            f.write("# CN 域名规则列表 (原始格式)\n")
            f.write(f"# 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("# ============================================\n\n")

            current_source = None
            for rule in all_rules:
                if rule["source"] != current_source:
                    current_source = rule["source"]
                    f.write(f"\n# --- {current_source} ---\n")
                f.write(f"{rule['original']}\n")

        grouped_custom_output_rules = group_rules_for_custom_output(all_rules)
        with open(OUTPUT_CUSTOM, "w", encoding="utf-8") as f:
            f.write("# ============================================\n")
            f.write("# PaoPaoDNS CN 标记域名列表\n")
            f.write(f"# 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("# ============================================\n")
            f.write("# 此文件由 generate_cn_rules.py 自动生成，请勿直接修改\n")
            f.write("# 自定义规则请编辑 custom.txt 或 custom_rule.txt 后重新生成\n")
            f.write("# \n")
            f.write("# 格式说明:\n")
            f.write("#   full:xxx  - 完整精确匹配\n")
            f.write("#   domain:xxx - 域名后缀匹配 (包含子域名)\n")
            f.write("#   regexp:xxx - 正则匹配\n")
            f.write("#   keyword:xxx - 关键字匹配\n")
            f.write("#   省略前缀时按 domain: 处理\n")
            f.write("#   同一文本匹配优先级: full > domain > regexp > keyword\n")
            f.write("# ============================================\n\n")

            for section_key in ("custom", "custom_rule", "generated"):
                section_rules = grouped_custom_output_rules[section_key]
                f.write(f"# --- {CUSTOM_OUTPUT_SECTION_TITLES[section_key]} ---\n")
                f.write(f"# 共 {len(section_rules)} 条\n")
                if not section_rules:
                    f.write("# 无\n\n")
                    continue

                for rule in section_rules:
                    f.write(f"{convert_to_paopaodns_format(rule['type'], rule['domain'])}\n")
                f.write("\n")

        log(f"生成原始规则文件: {OUTPUT_ORGANIZED}", log_file)
        log(f"生成格式化规则文件: {OUTPUT_CUSTOM}", log_file)

        print("\n完成！")
        print(f"  原始规则: {OUTPUT_ORGANIZED}")
        print(f"  格式化规则: {OUTPUT_CUSTOM}")
        print(f"  总规则数: {len(all_rules)}")
    except RuntimeError as exc:
        log(str(exc), log_file)
        raise
    finally:
        if log_file:
            log_file.close()


def main(argv=None):
    """脚本入口。"""
    parser = build_argument_parser()
    args = parser.parse_args(argv)

    if args.threads < 1:
        parser.error("--threads 必须大于等于 1")
    if args.timeout < 1:
        parser.error("--timeout 必须大于等于 1")
    if args.retries < 1:
        parser.error("--retries 必须大于等于 1")

    if args.list_sources:
        for source_name, source_config in SOURCES.items():
            print(f"{source_name} ({source_config['display_name']})")
        return 0

    try:
        generate_rules(args)
        return 0
    except RuntimeError:
        return 1
    except KeyboardInterrupt:
        print("\n已取消生成。", flush=True)
        os._exit(130)


if __name__ == "__main__":
    sys.exit(main())
