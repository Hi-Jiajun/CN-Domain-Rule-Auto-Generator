import os
import tempfile
import unittest
from types import SimpleNamespace
from unittest import mock

import generate_cn_rules as generator


def make_args(**overrides):
    defaults = {
        "verbose": False,
        "log": False,
        "no_download": False,
        "use_fallback": False,
        "proxy": None,
        "threads": 2,
        "timeout": 60,
        "retries": 1,
        "progress": False,
        "no_default_sources": False,
        "sources": None,
        "exclude_sources": None,
        "list_sources": False,
        "geosite_groups": None,
    }
    defaults.update(overrides)
    return SimpleNamespace(**defaults)


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

    def test_resolve_enabled_sources_defaults_to_all(self):
        args = make_args()

        enabled_sources = generator.resolve_enabled_sources(args)

        self.assertEqual(["Aethersailor", "Loyalsoldier", "v2fly"], enabled_sources)

    def test_resolve_enabled_sources_supports_aliases_and_excludes(self):
        args = make_args(
            sources=["Custom_OpenClash_Rules;domain-list-community"],
            exclude_sources=["v2fly"],
        )

        enabled_sources = generator.resolve_enabled_sources(args)

        self.assertEqual(["Aethersailor"], enabled_sources)

    def test_resolve_enabled_sources_allows_disabling_default_sources(self):
        args = make_args(no_default_sources=True)

        enabled_sources = generator.resolve_enabled_sources(args)

        self.assertEqual([], enabled_sources)

    def test_resolve_geosite_groups_defaults_to_all_cn_groups(self):
        args = make_args()

        groups = generator.resolve_geosite_groups(args)

        self.assertEqual(["*-cn"], groups)

    def test_resolve_geosite_groups_supports_repeat_and_comma_values(self):
        args = make_args(geosite_groups=["apple-cn;google-cn", "apple-cn"])

        groups = generator.resolve_geosite_groups(args)

        self.assertEqual(["apple-cn", "google-cn"], groups)

    def test_compile_geosite_group_matchers_supports_regex_prefix(self):
        matchers = generator.compile_geosite_group_matchers(["apple-cn", "re:.*-cn$"])

        self.assertTrue(generator.matches_geosite_group("apple-cn", matchers))
        self.assertTrue(generator.matches_geosite_group("google-cn", matchers))
        self.assertFalse(generator.matches_geosite_group("netflix", matchers))

    def test_parse_dlc_yml_defaults_to_cn_groups(self):
        content = """
lists:
  - name: apple-cn
    length: 1
    rules:
      - "domain:apple.com"
  - name: google-cn
    length: 1
    rules:
      - "full:google.cn"
  - name: netflix
    length: 1
    rules:
      - "domain:netflix.com"
""".strip()

        rules = generator.parse_dlc_yml(content, group_patterns=["*-cn"])

        self.assertEqual(["apple.com", "google.cn"], [rule["domain"] for rule in rules])

    def test_parse_dlc_yml_supports_custom_groups(self):
        content = """
lists:
  - name: apple-cn
    length: 1
    rules:
      - "domain:apple.com"
  - name: google-cn
    length: 1
    rules:
      - "full:google.cn"
""".strip()

        rules = generator.parse_dlc_yml(content, group_patterns=["apple-cn"])

        self.assertEqual(["apple.com"], [rule["domain"] for rule in rules])

    def test_parse_dlc_yml_supports_regex_groups(self):
        content = """
lists:
  - name: apple-cn
    length: 1
    rules:
      - "domain:apple.com"
  - name: google-cn
    length: 1
    rules:
      - "full:google.cn"
  - name: netflix
    length: 1
    rules:
      - "domain:netflix.com"
""".strip()

        rules = generator.parse_dlc_yml(content, group_patterns=["re:.*-cn$"])

        self.assertEqual(["apple.com", "google.cn"], [rule["domain"] for rule in rules])

    def test_get_fallback_urls_includes_jsdelivr_fastly_and_ghfast_for_raw(self):
        urls = generator.get_fallback_urls(
            "https://raw.githubusercontent.com/user/repo/main/test.txt"
        )

        self.assertEqual(
            [
                "https://cdn.jsdelivr.net/gh/user/repo@main/test.txt",
                "https://fastly.jsdelivr.net/gh/user/repo@main/test.txt",
                "https://ghfast.top/https://raw.githubusercontent.com/user/repo/main/test.txt",
            ],
            urls,
        )

    def test_generate_rules_supports_custom_rule_urls_without_default_sources(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            organized_path = os.path.join(temp_dir, "organized_cn_mark.txt")
            custom_path = os.path.join(temp_dir, "custom_cn_mark.txt")
            custom_rule_path = os.path.join(temp_dir, "custom_rule.txt")
            custom_src_path = os.path.join(temp_dir, "custom.txt")
            cache_dir = os.path.join(temp_dir, ".cache")
            log_path = os.path.join(temp_dir, "generate.log")

            with open(custom_rule_path, "w", encoding="utf-8") as f:
                f.write("https://example.com/remote-rules.txt\n")

            args = make_args(no_default_sources=True)

            with mock.patch.object(generator, "OUTPUT_ORGANIZED", organized_path), \
                 mock.patch.object(generator, "OUTPUT_CUSTOM", custom_path), \
                 mock.patch.object(generator, "OUTPUT_CUSTOM_RULE_SRC", custom_rule_path), \
                 mock.patch.object(generator, "OUTPUT_CUSTOM_SRC", custom_src_path), \
                 mock.patch.object(generator, "OUTPUT_LOG", log_path), \
                 mock.patch.object(generator, "CACHE_DIR", cache_dir), \
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


if __name__ == "__main__":
    unittest.main()
