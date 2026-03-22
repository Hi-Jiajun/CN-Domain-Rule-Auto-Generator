# 🌏 CN-Domain-Rule-Auto-Generator

### Automated Generator for China Mainland Direct Connect Domain Marking Rules

[![GitHub Stars](https://img.shields.io/github/stars/Hi-Jiajun/CN-Domain-Rule-Auto-Generator?style=flat)](https://github.com/Hi-Jiajun/CN-Domain-Rule-Auto-Generator/stargazers)
[![GitHub License](https://img.shields.io/github/license/Hi-Jiajun/CN-Domain-Rule-Auto-Generator)](LICENSE)
[![Auto Update](https://github.com/Hi-Jiajun/CN-Domain-Rule-Auto-Generator/actions/workflows/auto-update.yml/badge.svg)](https://github.com/Hi-Jiajun/CN-Domain-Rule-Auto-Generator/actions)

[English](./README_EN.md) | [中文](./README.md)

---

## 📋 Introduction

This project generates `custom_cn_mark.txt` rule file for [PaoPaoDNS](https://github.com/kkkgo/PaoPaoDNS) with the following features:

- 🔄 **Multi-source Aggregation** - Automatically fetch domain rules from multiple upstream sources
- 🇨🇳 **China Network Friendly** - Uses JsDelivr CDN / ghfast.top reverse proxy for China users
- 🔀 **Smart Deduplication** - Automatically removes duplicate rules by priority
- 🧹 **Invalid Cleanup** - Automatically cleans commented invalid domains
- ⚙️ **Custom Support** - Supports local custom rule extension
- 🔄 **Auto Update** - GitHub Actions runs daily and supports manual dispatch to keep rules up-to-date

---

## 🚀 Quick Start

### Local Run

```bash
# Clone repository
git clone https://github.com/Hi-Jiajun/CN-Domain-Rule-Auto-Generator.git
cd CN-Domain-Rule-Auto-Generator

# Run script
python3 generate_cn_rules.py

# View help
python3 generate_cn_rules.py -h

# Verbose output
python3 generate_cn_rules.py -v

# Use fallback links (for China network)
python3 generate_cn_rules.py -v -f

# Generate log and refresh local cache
python3 generate_cn_rules.py --log

# Use local cache only, without any network download
python3 generate_cn_rules.py --no-download

# Launch the interactive custom rule manager
python3 manage_custom_rules.py

# Add a local custom rule directly from CLI
python3 manage_custom_rules.py add-rule domain:example.com

# Apply a batch config file
python3 manage_custom_rules.py run-config manage_custom_rules.toml

# Regenerate using cache only
python3 manage_custom_rules.py generate --no-download
```

### Command Line Options

| Option | Description |
|--------|-------------|
| `-h`, `--help` | Show help information |
| `-v`, `--verbose` | Show detailed output |
| `--log` | Generate log file and refresh `.cache/` in normal mode |
| `--no-download` | Skip network download and use cached source files from `.cache/` only |
| `-f`, `--use-fallback` | Use fallback CDN links (for China network) |

---

## 📁 File Description

### Input/Config Files

| File | Description |
|------|-------------|
| `custom.txt` | Personal custom domain list (optional) |
| `custom_rule.txt` | Third-party rule link list (optional) |

### Output Files

| File | Description |
|------|-------------|
| `organized_cn_mark.txt` | Merged and deduplicated original rules |
| `custom_cn_mark.txt` | Final formatted rules for PaoPaoDNS |

### Interactive Management

Use `manage_custom_rules.py` if you want to maintain `custom.txt` / `custom_rule.txt` without editing files manually.

Examples:

```bash
python3 manage_custom_rules.py list-rules
python3 manage_custom_rules.py add-rule full:api.example.com
python3 manage_custom_rules.py add-url https://example.com/rules.txt
python3 manage_custom_rules.py run-config manage_custom_rules.toml
python3 manage_custom_rules.py generate --no-download
```

The repository also includes [manage_custom_rules.toml](./manage_custom_rules.toml), which can be used for batch non-interactive operations such as:

- add/remove local rules
- add/remove third-party rule URLs
- optionally trigger rule generation after applying the changes

---

## 📊 Data Sources

Domain rules are aggregated from the following open source projects:

| Source | Repository |
|--------|------------|
| Custom_OpenClash_Rules | [Aethersailor/Custom_OpenClash_Rules](https://github.com/Aethersailor/Custom_OpenClash_Rules) |
| v2ray-rules-dat | [Loyalsoldier/v2ray-rules-dat](https://github.com/Loyalsoldier/v2ray-rules-dat) |
| domain-list-community | [v2fly/domain-list-community](https://github.com/v2fly/domain-list-community) |
| dnsmasq-china-list | [felixonmars/dnsmasq-china-list](https://github.com/felixonmars/dnsmasq-china-list) |

---

## 🔗 Direct Subscription

### GitHub Raw Links

| File | Link |
|------|------|
| custom_cn_mark.txt | [https://raw.githubusercontent.com/Hi-Jiajun/CN-Domain-Rule-Auto-Generator/main/custom_cn_mark.txt](https://raw.githubusercontent.com/Hi-Jiajun/CN-Domain-Rule-Auto-Generator/main/custom_cn_mark.txt) |
| organized_cn_mark.txt | [https://raw.githubusercontent.com/Hi-Jiajun/CN-Domain-Rule-Auto-Generator/main/organized_cn_mark.txt](https://raw.githubusercontent.com/Hi-Jiajun/CN-Domain-Rule-Auto-Generator/main/organized_cn_mark.txt) |

### JsDelivr CDN Links

| File | Link |
|------|------|
| custom_cn_mark.txt | [https://cdn.jsdelivr.net/gh/Hi-Jiajun/CN-Domain-Rule-Auto-Generator@main/custom_cn_mark.txt](https://cdn.jsdelivr.net/gh/Hi-Jiajun/CN-Domain-Rule-Auto-Generator@main/custom_cn_mark.txt) |
| organized_cn_mark.txt | [https://cdn.jsdelivr.net/gh/Hi-Jiajun/CN-Domain-Rule-Auto-Generator@main/organized_cn_mark.txt](https://cdn.jsdelivr.net/gh/Hi-Jiajun/CN-Domain-Rule-Auto-Generator@main/organized_cn_mark.txt) |

### China CDN Links (ghfast.top)

| File | Link |
|------|------|
| custom_cn_mark.txt | [https://ghfast.top/https://raw.githubusercontent.com/Hi-Jiajun/CN-Domain-Rule-Auto-Generator/main/custom_cn_mark.txt](https://ghfast.top/https://raw.githubusercontent.com/Hi-Jiajun/CN-Domain-Rule-Auto-Generator/main/custom_cn_mark.txt) |
| organized_cn_mark.txt | [https://ghfast.top/https://raw.githubusercontent.com/Hi-Jiajun/CN-Domain-Rule-Auto-Generator/main/organized_cn_mark.txt](https://ghfast.top/https://raw.githubusercontent.com/Hi-Jiajun/CN-Domain-Rule-Auto-Generator/main/organized_cn_mark.txt) |

---

## 👏 Acknowledgments

Thanks to the contributors of the following open source projects:

- **[PaoPaoDNS](https://github.com/kkkgo/PaoPaoDNS)** - Dedicated project for this rule set
- **[Aethersailor](https://github.com/Aethersailor)** - Custom_OpenClash_Rules
- **[Loyalsoldier](https://github.com/Loyalsoldier)** - v2ray-rules-dat
- **[v2fly](https://github.com/v2fly)** - domain-list-community
- **[felixonmars](https://github.com/felixonmars)** - dnsmasq-china-list

---

## ⭐ Star History

[![Star History Chart](https://api.star-history.com/svg?repos=Hi-Jiajun/CN-Domain-Rule-Auto-Generator&type=Date)](https://star-history.com/#Hi-Jiajun/CN-Domain-Rule-Auto-Generator&Date)

---

## 💖 Donation Support

If this project is helpful to you, your donations are greatly appreciated!

| Alipay | WeChat Pay |
|:------:|:----------:|
| <img src="https://Hi-Jiajun.github.io/picx-images-hosting/alipay_qrcode.7p45v27tjq.webp" width="150" /> | <img src="https://Hi-Jiajun.github.io/picx-images-hosting/wechat_qrcode.icohq9bcf.webp" width="150" /> |

---

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.
de.icohq9bcf.webp" width="150" /> |

---

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.
