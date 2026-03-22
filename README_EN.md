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
python3 generate_cn_rules.py -l

# Use local cache only, without any network download
python3 generate_cn_rules.py -n

# Download with 6 worker threads
python3 generate_cn_rules.py -t 6

# Use a download proxy
python3 generate_cn_rules.py -p http://127.0.0.1:7890

# Disable default upstream sources
python3 generate_cn_rules.py -N

# Enable only selected default upstream sources (comma or semicolon separated; quote semicolons in shell)
python3 generate_cn_rules.py -s "Aethersailor;v2fly"

# Extract selected geosite groups from dlc.dat_plain.yml (comma or semicolon separated; quote semicolons in shell)
python3 generate_cn_rules.py -g "apple-cn;google-cn"

# Extract geosite groups by regex
python3 generate_cn_rules.py -g "re:.*-cn$"
```

By default, the script shows a live download progress bar and transfer rate. For GitHub Actions, redirected logs, or other non-interactive environments, prefer adding `-P` to disable dynamic progress output.

Fallback logic:
the script tries the original URL first; for `raw.githubusercontent.com` static links, it then falls back to `cdn.jsdelivr.net`, `fastly.jsdelivr.net`, and only then switches to other available mirrors.

### Command Line Options

| Option | Description |
|--------|-------------|
| `-h`, `--help` | Show help information |
| `-v`, `--verbose` | Show detailed output |
| `-l`, `--log` | Generate log file and refresh `.cache/` in normal mode |
| `-n`, `--no-download` | Skip network download and use cached source files from `.cache/` only |
| `-f`, `--use-fallback` | Use fallback CDN links (for China network) |
| `-t`, `--threads` | Set concurrent download worker count |
| `-p`, `--proxy` | Set download proxy |
| `-T`, `--timeout` | Set per-request timeout |
| `-r`, `--retries` | Set retry count for each mirror URL |
| `-P`, `--no-progress` | Disable download progress display |
| `-N`, `--no-default-sources` | Disable default upstream rule sources |
| `-s`, `--source` | Enable only selected default upstream sources; supports comma- or semicolon-separated values |
| `-x`, `--exclude-source` | Exclude selected default upstream sources; supports comma- or semicolon-separated values |
| `-g`, `--geosite-group` | Select geosite groups extracted from `dlc.dat_plain.yml`; supports comma- or semicolon-separated values and `re:` / `regex:` regex expressions, default `*-cn` |
| `-L`, `--list-sources` | List available default upstream sources |

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

---

## 📊 Data Sources

Domain rules are aggregated from the following open source projects:

| Source | Repository |
|--------|------------|
| Custom_OpenClash_Rules | [Aethersailor/Custom_OpenClash_Rules](https://github.com/Aethersailor/Custom_OpenClash_Rules) |
| v2ray-rules-dat | [Loyalsoldier/v2ray-rules-dat](https://github.com/Loyalsoldier/v2ray-rules-dat) |
| domain-list-community | [v2fly/domain-list-community](https://github.com/v2fly/domain-list-community) |

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
