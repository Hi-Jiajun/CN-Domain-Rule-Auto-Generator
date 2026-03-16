# CN-Domain-Rule-Auto-Generator

Automated Generator for China Mainland Direct Connect Domain Marking Rules

[中文 README](./README.md)

## Introduction

This project is specifically designed for [PaoPaoDNS](https://github.com/kkkgo/PaoPaoDNS) to generate the `custom_cn_mark.txt` rule file. It automatically aggregates multiple upstream high-quality China mainland direct connect domains, performs priority-based deduplication, cleans invalid rules, formats output, and updates daily without manual maintenance.

## Features

- **Multi-source Aggregation**: Fetch domain rules from multiple sources with priority (Athersailor > Loyalsoldier > v2fly > Custom Links > Personal Custom)
- **China Network Friendly**: All rule fetching uses ghfast.top reverse proxy by default, accessible for China users
- **Smart Deduplication**: Automatically removes duplicate rules, keeping higher priority rules
- **Invalid Rule Cleanup**: Automatically cleans commented invalid domains
- **Custom Support**: Supports local `custom.txt` and `custom_rule.txt` for custom rules
- **Format Conversion**: Automatically formats output to PaoPaoDNS rule syntax
- **Auto Update**: GitHub Actions runs daily to keep rules up-to-date

## Quick Start

### Local Run

```bash
# Clone repository
git clone https://github.com/Hi-Jiajun/CN-Domain-Rule-Auto-Generator.git
cd CN-Domain-Generator

# Run script
python-Rule-Auto3 generate_cn_rules.py

# View help
python3 generate_cn_rules.py -h

# Verbose output
python3 generate_cn_rules.py -v

# Use fallback links (for China network)
python3 generate_cn_rules.py -v -f
```

### Command Line Options

| Option | Description |
|--------|-------------|
| `-h`, `--help` | Show help information |
| `-v`, `--verbose` | Show detailed output |
| `--log` | Generate log file |
| `-f`, `--use-fallback` | Use fallback links directly (for China network) |

## Configuration Files

### Input/Config Files

| File | Description |
|------|-------------|
| `custom.txt` | Personal custom domain list (optional) |
| `custom_rule.txt` | Third-party rule link list (optional) |

### Output Files

| File | Description |
|------|-------------|
| `organized_cn_mark.txt` | Merged and deduplicated original rule file |
| `custom_cn_mark.txt` | PaoPaoDNS专用最终规则文件 |

## Direct Subscription

### GitHub Raw Links

- [custom_cn_mark.txt](https://raw.githubusercontent.com/Hi-Jiajun/CN-Domain-Rule-Auto-Generator/main/custom_cn_mark.txt)
- [organized_cn_mark.txt](https://raw.githubusercontent.com/Hi-Jiajun/CN-Domain-Rule-Auto-Generator/main/organized_cn_mark.txt)

### China CDN Links

- custom_cn_mark.txt: `https://ghfast.top/https://raw.githubusercontent.com/Hi-Jiajun/CN-Domain-Rule-Auto-Generator/main/custom_cn_mark.txt`

## Data Sources

This project's rule data comes from the following open source projects (sorted by priority):

1. [Aethersailor/Custom_OpenClash_Rules](https://github.com/Aethersailor/Custom_OpenClash_Rules) - Highest Priority
2. [Loyalsoldier/v2ray-rules-dat](https://github.com/Loyalsoldier/v2ray-rules-dat)
3. [v2fly/domain-list-community](https://github.com/v2fly/domain-list-community)
4. [felixonmars/dnsmasq-china-list](https://github.com/felixonmars/dnsmasq-china-list)

## Applicable Projects

- [PaoPaoDNS](https://github.com/kkkgo/PaoPaoDNS) - Dedicated for this rule set

## Acknowledgments

Thanks to the contributors of the following open source projects:

- PaoPaoDNS Project
- Aethersailor
- Loyalsoldier
- v2fly
- felixonmars

## Donation Support

If this project is helpful to you, your donations are greatly appreciated!

<!-- Local donation QR code paths (displayed locally, not uploaded to repo) -->
<!-- Alipay: C:\Users\hiliang\Pictures\个人收款码\alipay_qrcode.jpg -->
<!-- WeChat Pay: C:\Users\hiliang\Pictures\个人收款码\wechat_qrcode.png -->

## License

MIT License
