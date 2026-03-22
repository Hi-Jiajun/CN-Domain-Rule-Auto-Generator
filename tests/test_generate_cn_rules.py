import os
import tempfile
import unittest
from types import SimpleNamespace
from unittest import mock
from argparse import Namespace

import generate_cn_rules as generator
import manage_custom_rules as manager


class GenerateCnRulesTests(unittest.TestCase):
    def test_parse_domain_rule_supports_regexp(self):
        rule = generator.parse_domain_rule(r"regexp:^Api\.Example\.COM$", "custom")

        self.assertIsNotNone(rule)
        self.assertEqual("regexp", rule["type"])
        self.assertEqual(r"^Api\.Example\.COM$", rule["domain"])

    def test_parse_domain_rule_keeps_go_style_regexp(self):
        rule = generator.parse_domain_rule(r"regexp:\p{Han}+\.example\.com$", "custom")

        self.assertIsNotNone(rule)
        self.assertEqual(r"\p{Han}+\.example\.com$", rule["domain"])

    def test_deduplicate_rules_preserves_different_types(self):
        rules = [
            {"domain": "download.microsoft.com", "type": "domain", "source": "Loyalsoldier", "original": "download.microsoft.com"},
            {"domain": "download.microsoft.com", "type": "full", "source": "Loyalsoldier", "original": "full:download.microsoft.com"},
        ]

        deduplicated = generator.deduplicate_rules(rules)

        self.assertEqual(2, len(deduplicated))
        self.assertEqual({"domain", "full"}, {rule["type"] for rule in deduplicated})

    def test_deduplicate_rules_prefers_higher_priority_for_same_type(self):
        rules = [
            {"domain": "example.com", "type": "domain", "source": "v2fly", "original": "domain:example.com"},
            {"domain": "example.com", "type": "domain", "source": "Aethersailor", "original": "DOMAIN-SUFFIX,example.com"},
        ]

        deduplicated = generator.deduplicate_rules(rules)

        self.assertEqual(1, len(deduplicated))
        self.assertEqual("Aethersailor", deduplicated[0]["source"])

    def test_resolve_enabled_sources_supports_aliases(self):
        args = SimpleNamespace(
            list_sources=False,
            sources=["Custom_OpenClash_Rules", "domain-list-community"],
            exclude_sources=None,
        )

        enabled_sources = generator.resolve_enabled_sources(args)

        self.assertEqual(["Aethersailor", "v2fly"], enabled_sources)

    def test_load_rule_source_urls_skips_comments(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            filepath = os.path.join(temp_dir, "custom_rule.txt")
            with open(filepath, "w", encoding="utf-8") as f:
                f.write("# comment\n")
                f.write("\n")
                f.write("https://example.com/rules.txt\n")
                f.write("https://raw.githubusercontent.com/user/repo/main/list.txt\n")

            urls = generator.load_rule_source_urls(filepath)

        self.assertEqual(
            [
                "https://example.com/rules.txt",
                "https://raw.githubusercontent.com/user/repo/main/list.txt",
            ],
            urls,
        )

    def test_load_rule_source_urls_rejects_invalid_link(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            filepath = os.path.join(temp_dir, "custom_rule.txt")
            with open(filepath, "w", encoding="utf-8") as f:
                f.write("not-a-url\n")

            with self.assertRaisesRegex(RuntimeError, "不是有效链接"):
                generator.load_rule_source_urls(filepath)

    def test_generate_rules_includes_custom_rule_urls(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            organized_path = os.path.join(temp_dir, "organized_cn_mark.txt")
            custom_path = os.path.join(temp_dir, "custom_cn_mark.txt")
            custom_rule_path = os.path.join(temp_dir, "custom_rule.txt")
            custom_src_path = os.path.join(temp_dir, "custom.txt")
            cache_dir = os.path.join(temp_dir, ".cache")
            log_path = os.path.join(temp_dir, "generate.log")

            with open(custom_rule_path, "w", encoding="utf-8") as f:
                f.write("https://example.com/remote-rules.txt\n")

            args = SimpleNamespace(log=False, verbose=False, no_download=False, use_fallback=False)

            with mock.patch.object(generator, "OUTPUT_ORGANIZED", organized_path), \
                 mock.patch.object(generator, "OUTPUT_CUSTOM", custom_path), \
                 mock.patch.object(generator, "OUTPUT_CUSTOM_RULE_SRC", custom_rule_path), \
                 mock.patch.object(generator, "OUTPUT_CUSTOM_SRC", custom_src_path), \
                 mock.patch.object(generator, "OUTPUT_LOG", log_path), \
                 mock.patch.object(generator, "CACHE_DIR", cache_dir), \
                 mock.patch.object(generator, "SOURCES", {}), \
                 mock.patch.object(
                     generator,
                     "download_file_with_fallback",
                     return_value="DOMAIN-SUFFIX,example.com\nDOMAIN,example.com\n",
                 ):
                generator.generate_rules(args)

            with open(custom_path, "r", encoding="utf-8") as f:
                custom_output = f.read()

        self.assertIn("domain:example.com", custom_output)
        self.assertIn("full:example.com", custom_output)

    def test_sort_rules_for_custom_output_uses_paopaodns_priority(self):
        rules = [
            {"domain": "keyword.example", "type": "keyword", "source": "custom", "original": "keyword:keyword.example"},
            {"domain": "regexp.example", "type": "regexp", "source": "custom", "original": r"regexp:^.+\.regexp\.example$"},
            {"domain": "domain.example", "type": "domain", "source": "custom", "original": "domain:domain.example"},
            {"domain": "full.example", "type": "full", "source": "custom", "original": "full:full.example"},
        ]

        sorted_rules = generator.sort_rules_for_custom_output(rules)

        self.assertEqual(
            ["full", "domain", "regexp", "keyword"],
            [rule["type"] for rule in sorted_rules],
        )

    def test_group_rules_for_custom_output_places_custom_section_first(self):
        rules = [
            {"domain": "upstream.example", "type": "full", "source": "Loyalsoldier", "original": "full:upstream.example"},
            {"domain": "local.example", "type": "domain", "source": "custom", "original": "domain:local.example"},
            {"domain": "remote.example", "type": "domain", "source": "custom_rule", "original": "domain:remote.example"},
        ]

        grouped = generator.group_rules_for_custom_output(rules)

        self.assertEqual(["local.example"], [rule["domain"] for rule in grouped["custom"]])
        self.assertEqual(["remote.example"], [rule["domain"] for rule in grouped["custom_rule"]])
        self.assertEqual(["upstream.example"], [rule["domain"] for rule in grouped["generated"]])

    def test_manage_custom_rules_append_and_remove_entry(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            filepath = os.path.join(temp_dir, "custom.txt")
            with open(filepath, "w", encoding="utf-8") as f:
                f.write("# header\n")

            self.assertTrue(manager.append_entry(filepath, "domain:example.com"))
            self.assertFalse(manager.append_entry(filepath, "domain:example.com"))
            self.assertEqual(["domain:example.com"], manager.read_entries(filepath))

            self.assertTrue(manager.remove_entry(filepath, "domain:example.com"))
            self.assertEqual([], manager.read_entries(filepath))

    def test_execute_command_add_rule(self):
        args = Namespace(command="add-rule", rule="domain:example.com")

        with mock.patch.object(manager, "add_custom_rule", return_value=0) as mocked_add:
            exit_code = manager.execute_command(args)

        mocked_add.assert_called_once_with("domain:example.com")
        self.assertEqual(0, exit_code)

    def test_execute_command_generate(self):
        args = Namespace(command="generate", no_download=True, use_fallback=False, sources=None, exclude_sources=["v2fly"])

        with mock.patch.object(manager, "run_generator") as mocked_generate:
            exit_code = manager.execute_command(args)

        mocked_generate.assert_called_once_with(
            no_download=True,
            use_fallback=False,
            sources=None,
            exclude_sources=["v2fly"],
        )
        self.assertEqual(0, exit_code)

    def test_main_add_url_command(self):
        with mock.patch.object(manager, "add_rule_url", return_value=0) as mocked_add_url:
            exit_code = manager.main(["add-url", "https://example.com/rules.txt"])

        mocked_add_url.assert_called_once_with("https://example.com/rules.txt")
        self.assertEqual(0, exit_code)

    def test_apply_config_file_updates_entries_and_runs_generator(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            rules_file = os.path.join(temp_dir, "custom.txt")
            urls_file = os.path.join(temp_dir, "custom_rule.txt")
            config_file = os.path.join(temp_dir, "manage_custom_rules.toml")

            with open(rules_file, "w", encoding="utf-8") as f:
                f.write("domain:old.example.com\n")
            with open(urls_file, "w", encoding="utf-8") as f:
                f.write("https://old.example.com/rules.txt\n")
            with open(config_file, "w", encoding="utf-8") as f:
                f.write(
                    """
[rules]
remove = ["domain:old.example.com"]
add = ["domain:new.example.com"]

[rule_urls]
remove = ["https://old.example.com/rules.txt"]
add = ["https://new.example.com/rules.txt"]

[sources]
enabled = ["Aethersailor", "v2fly"]

[generate]
run = true
no_download = true
use_fallback = false
""".strip()
                )

            with mock.patch.object(manager, "CUSTOM_RULES_FILE", rules_file), \
                 mock.patch.object(manager, "CUSTOM_RULE_URLS_FILE", urls_file), \
                 mock.patch.object(manager, "run_generator_with_sources") as mocked_generate:
                exit_code = manager.apply_config_file(config_file)

            self.assertEqual(0, exit_code)
            self.assertEqual(["domain:new.example.com"], manager.read_entries(rules_file))
            self.assertEqual(["https://new.example.com/rules.txt"], manager.read_entries(urls_file))
            mocked_generate.assert_called_once_with(
                enabled_sources=["Aethersailor", "v2fly"],
                no_download=True,
                use_fallback=False,
            )

    def test_execute_command_run_config(self):
        args = Namespace(command="run-config", config="manage_custom_rules.toml")

        with mock.patch.object(manager, "apply_config_file", return_value=0) as mocked_apply:
            exit_code = manager.execute_command(args)

        mocked_apply.assert_called_once_with("manage_custom_rules.toml")
        self.assertEqual(0, exit_code)

    def test_toggle_source_in_config_updates_enabled_sources(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = os.path.join(temp_dir, "manage_custom_rules.toml")
            manager.write_config_file(config_file, manager.merge_config_with_defaults({}))

            exit_code = manager.toggle_source_in_config("v2fly", config_path=config_file)
            config = manager.load_config_file(config_file)

        self.assertEqual(0, exit_code)
        self.assertNotIn("v2fly", config["sources"]["enabled"])


if __name__ == "__main__":
    unittest.main()
