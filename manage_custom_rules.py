#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import os
import sys
import tomllib
import urllib.parse
from types import SimpleNamespace

import generate_cn_rules as generator


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CUSTOM_RULES_FILE = os.path.join(BASE_DIR, "custom.txt")
CUSTOM_RULE_URLS_FILE = os.path.join(BASE_DIR, "custom_rule.txt")
DEFAULT_CONFIG_FILE = os.path.join(BASE_DIR, "manage_custom_rules.toml")


def read_entries(filepath):
    """读取文件中的非注释条目。"""
    if not os.path.exists(filepath):
        return []

    entries = []
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            stripped = line.strip()
            if stripped and not stripped.startswith("#"):
                entries.append(stripped)

    return entries


def append_entry(filepath, entry):
    """向文件追加一个条目；如果已存在则跳过。"""
    existing_entries = read_entries(filepath)
    if entry in existing_entries:
        return False

    with open(filepath, "a+", encoding="utf-8") as f:
        f.seek(0)
        current_content = f.read()
        if current_content and not current_content.endswith("\n"):
            f.write("\n")
        f.write(entry + "\n")

    return True


def remove_entry(filepath, entry):
    """删除文件中的指定条目，保留注释。"""
    if not os.path.exists(filepath):
        return False

    removed = False
    new_lines = []
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            stripped = line.strip()
            if stripped and not stripped.startswith("#") and stripped == entry:
                removed = True
                continue
            new_lines.append(line)

    if removed:
        with open(filepath, "w", encoding="utf-8") as f:
            f.writelines(new_lines)

    return removed


def validate_custom_rule(rule):
    """验证自定义规则格式。"""
    return generator.parse_domain_rule(rule, "custom") is not None


def validate_rule_url(url):
    """验证第三方规则链接格式。"""
    parsed = urllib.parse.urlparse(url)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def print_entries(title, entries):
    """打印带编号的条目列表。"""
    print(f"\n{title}")
    if not entries:
        print("  暂无条目")
        return

    for index, entry in enumerate(entries, start=1):
        print(f"  {index}. {entry}")


def prompt_text(prompt):
    """读取一行用户输入，支持 EOF 安静退出。"""
    try:
        return input(prompt).strip()
    except EOFError:
        print("\n输入已结束，已取消当前操作。")
        return None


def prompt_entry_index(entries, prompt_text_value):
    """让用户输入条目序号。"""
    if not entries:
        return None

    raw_value = prompt_text(prompt_text_value)
    if raw_value is None or not raw_value:
        return None

    if not raw_value.isdigit():
        print("请输入有效的数字序号。")
        return None

    index = int(raw_value)
    if index < 1 or index > len(entries):
        print("序号超出范围。")
        return None

    return index - 1


def run_generator(no_download=False, use_fallback=False):
    """调用主生成脚本。"""
    args = SimpleNamespace(
        help=False,
        verbose=True,
        log=True,
        no_download=no_download,
        use_fallback=use_fallback,
    )
    generator.generate_rules(args)


def list_custom_rules():
    """列出 custom.txt 中的规则。"""
    print_entries("custom.txt 当前规则", read_entries(CUSTOM_RULES_FILE))


def add_custom_rule(rule):
    """添加 custom.txt 规则。"""
    if not validate_custom_rule(rule):
        print("规则格式无效。支持 domain:/full:/regexp:/keyword: 或裸域名。")
        return 1

    if append_entry(CUSTOM_RULES_FILE, rule):
        print("已添加到 custom.txt。")
    else:
        print("该规则已存在，无需重复添加。")
    return 0


def remove_custom_rule(rule):
    """删除 custom.txt 规则。"""
    if remove_entry(CUSTOM_RULES_FILE, rule):
        print("已从 custom.txt 删除。")
        return 0

    print("custom.txt 中未找到该规则。")
    return 1


def list_rule_urls():
    """列出 custom_rule.txt 中的链接。"""
    print_entries("custom_rule.txt 当前链接", read_entries(CUSTOM_RULE_URLS_FILE))


def add_rule_url(url):
    """添加 custom_rule.txt 链接。"""
    if not validate_rule_url(url):
        print("链接格式无效。请输入 http/https 链接。")
        return 1

    if append_entry(CUSTOM_RULE_URLS_FILE, url):
        print("已添加到 custom_rule.txt。")
    else:
        print("该链接已存在，无需重复添加。")
    return 0


def remove_rule_url(url):
    """删除 custom_rule.txt 链接。"""
    if remove_entry(CUSTOM_RULE_URLS_FILE, url):
        print("已从 custom_rule.txt 删除。")
        return 0

    print("custom_rule.txt 中未找到该链接。")
    return 1


def load_config_file(config_path):
    """读取 TOML 配置文件。"""
    with open(config_path, "rb") as f:
        data = tomllib.load(f)

    if not isinstance(data, dict):
        raise RuntimeError("配置文件内容无效，顶层必须是 TOML 表。")

    return data


def validate_config_list(config, section_name, field_name):
    """读取并校验配置中的字符串列表。"""
    section = config.get(section_name, {})
    if section is None:
        return []
    if not isinstance(section, dict):
        raise RuntimeError(f"配置段 [{section_name}] 必须是表。")

    values = section.get(field_name, [])
    if values is None:
        return []
    if not isinstance(values, list) or any(not isinstance(item, str) for item in values):
        raise RuntimeError(f"配置项 [{section_name}].{field_name} 必须是字符串数组。")

    return values


def validate_config_bool(config, section_name, field_name, default_value=False):
    """读取并校验配置中的布尔值。"""
    section = config.get(section_name, {})
    if section is None:
        return default_value
    if not isinstance(section, dict):
        raise RuntimeError(f"配置段 [{section_name}] 必须是表。")

    value = section.get(field_name, default_value)
    if not isinstance(value, bool):
        raise RuntimeError(f"配置项 [{section_name}].{field_name} 必须是布尔值。")

    return value


def apply_config_file(config_path):
    """按配置文件批量执行规则维护和生成。"""
    config = load_config_file(config_path)
    exit_code = 0

    print(f"读取配置文件: {config_path}")

    for rule in validate_config_list(config, "rules", "remove"):
        exit_code = max(exit_code, remove_custom_rule(rule))
    for rule in validate_config_list(config, "rules", "add"):
        exit_code = max(exit_code, add_custom_rule(rule))

    for url in validate_config_list(config, "rule_urls", "remove"):
        exit_code = max(exit_code, remove_rule_url(url))
    for url in validate_config_list(config, "rule_urls", "add"):
        exit_code = max(exit_code, add_rule_url(url))

    should_generate = validate_config_bool(config, "generate", "run", default_value=False)
    no_download = validate_config_bool(config, "generate", "no_download", default_value=False)
    use_fallback = validate_config_bool(config, "generate", "use_fallback", default_value=False)

    if should_generate:
        try:
            run_generator(no_download=no_download, use_fallback=use_fallback)
        except RuntimeError as exc:
            print(f"生成失败: {exc}")
            return 1

    return exit_code


def show_menu():
    """显示交互菜单。"""
    print("\n==============================")
    print("自定义规则管理")
    print("==============================")
    print("1. 查看 custom.txt 规则")
    print("2. 添加 custom.txt 规则")
    print("3. 删除 custom.txt 规则")
    print("4. 查看 custom_rule.txt 链接")
    print("5. 添加 custom_rule.txt 链接")
    print("6. 删除 custom_rule.txt 链接")
    print("7. 在线重新生成规则")
    print("8. 使用缓存重新生成规则 (--no-download)")
    print("0. 退出")


def run_interactive():
    """菜单式交互入口。"""
    print("交互式规则管理工具")
    print(f"项目目录: {BASE_DIR}")

    while True:
        show_menu()
        choice = prompt_text("\n请选择操作: ")
        if choice is None:
            print("已退出。")
            return 0
        if not choice:
            continue

        if choice == "1":
            list_custom_rules()
        elif choice == "2":
            rule = prompt_text("请输入要添加的规则: ")
            if rule:
                add_custom_rule(rule)
        elif choice == "3":
            entries = read_entries(CUSTOM_RULES_FILE)
            print_entries("custom.txt 当前规则", entries)
            index = prompt_entry_index(entries, "请输入要删除的序号: ")
            if index is not None:
                remove_custom_rule(entries[index])
        elif choice == "4":
            list_rule_urls()
        elif choice == "5":
            url = prompt_text("请输入要添加的规则链接: ")
            if url:
                add_rule_url(url)
        elif choice == "6":
            entries = read_entries(CUSTOM_RULE_URLS_FILE)
            print_entries("custom_rule.txt 当前链接", entries)
            index = prompt_entry_index(entries, "请输入要删除的序号: ")
            if index is not None:
                remove_rule_url(entries[index])
        elif choice == "7":
            try:
                run_generator(no_download=False)
            except RuntimeError as exc:
                print(f"生成失败: {exc}")
        elif choice == "8":
            try:
                run_generator(no_download=True)
            except RuntimeError as exc:
                print(f"生成失败: {exc}")
        elif choice == "0":
            print("已退出。")
            return 0
        else:
            print("不支持的选项，请重新输入。")


def build_parser():
    """构建命令行参数解析器。"""
    parser = argparse.ArgumentParser(
        description="管理 custom.txt 和 custom_rule.txt，并可直接触发规则生成。"
    )
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("interactive", help="启动交互式菜单")
    subparsers.add_parser("list-rules", help="列出 custom.txt 中的规则")

    add_rule_parser = subparsers.add_parser("add-rule", help="向 custom.txt 添加一条规则")
    add_rule_parser.add_argument("rule", help="规则内容，如 domain:example.com")

    remove_rule_parser = subparsers.add_parser("remove-rule", help="从 custom.txt 删除一条规则")
    remove_rule_parser.add_argument("rule", help="要删除的规则内容")

    subparsers.add_parser("list-urls", help="列出 custom_rule.txt 中的链接")

    add_url_parser = subparsers.add_parser("add-url", help="向 custom_rule.txt 添加一个规则链接")
    add_url_parser.add_argument("url", help="http/https 规则链接")

    remove_url_parser = subparsers.add_parser("remove-url", help="从 custom_rule.txt 删除一个规则链接")
    remove_url_parser.add_argument("url", help="要删除的规则链接")

    run_config_parser = subparsers.add_parser("run-config", help="读取 TOML 配置文件并批量执行")
    run_config_parser.add_argument(
        "config",
        nargs="?",
        default=DEFAULT_CONFIG_FILE,
        help=f"TOML 配置文件路径，默认: {os.path.basename(DEFAULT_CONFIG_FILE)}",
    )

    generate_parser = subparsers.add_parser("generate", help="调用 generate_cn_rules.py 重新生成规则")
    generate_parser.add_argument("--no-download", action="store_true", help="仅使用缓存生成")
    generate_parser.add_argument("-f", "--use-fallback", action="store_true", help="优先使用备用下载链接")

    return parser


def execute_command(args):
    """执行命令行子命令。"""
    if args.command in {None, "interactive"}:
        return run_interactive()
    if args.command == "list-rules":
        list_custom_rules()
        return 0
    if args.command == "add-rule":
        return add_custom_rule(args.rule)
    if args.command == "remove-rule":
        return remove_custom_rule(args.rule)
    if args.command == "list-urls":
        list_rule_urls()
        return 0
    if args.command == "add-url":
        return add_rule_url(args.url)
    if args.command == "remove-url":
        return remove_rule_url(args.url)
    if args.command == "run-config":
        try:
            return apply_config_file(args.config)
        except (OSError, tomllib.TOMLDecodeError, RuntimeError) as exc:
            print(f"配置执行失败: {exc}")
            return 1
    if args.command == "generate":
        try:
            run_generator(no_download=args.no_download, use_fallback=args.use_fallback)
        except RuntimeError as exc:
            print(f"生成失败: {exc}")
            return 1
        return 0

    print(f"未知命令: {args.command}")
    return 1


def main(argv=None):
    """脚本入口。"""
    parser = build_parser()
    args = parser.parse_args(argv)
    return execute_command(args)


if __name__ == "__main__":
    sys.exit(main())
