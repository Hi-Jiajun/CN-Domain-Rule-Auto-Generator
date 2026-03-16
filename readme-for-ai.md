# CN-Domain-Rule-Auto-Generator

## Project Purpose

This project generates domain marking rules for PaoPaoDNS project. It automatically aggregates multiple upstream China mainland direct connect domain rules, performs priority-based deduplication, cleans invalid rules, and outputs formatted rules for PaoPaoDNS.

## Applicable Project

- PaoPaoDNS: https://github.com/kkkgo/PaoPaoDNS

## Script Function

The main script `generate_cn_rules.py` performs the following operations:

1. Fetch domain rules from multiple upstream sources
2. Perform priority-based deduplication
3. Clean invalid/commented rules
4. Convert format to PaoPaoDNS syntax
5. Output final rule files

## File Description

### Input Files

| File | Purpose |
|------|---------|
| custom.txt | User custom domain list (optional) |
| custom_rule.txt | Third-party rule link list (optional) |

### Output Files

| File | Purpose |
|------|---------|
| organized_cn_mark.txt | Merged and deduplicated original rules |
| custom_cn_mark.txt | Final formatted rules for PaoPaoDNS |

### Core Script

- generate_cn_rules.py: Main script for generating rules

### Configuration Files

- .github/workflows/auto-update.yml: GitHub Actions workflow configuration
- .gitignore: Git ignore rules

## Usage

### Command Line

```bash
python3 generate_cn_rules.py [options]
```

### Options

| Option | Description |
|--------|-------------|
| -h, --help | Show help information |
| -v, --verbose | Show detailed output |
| --log | Generate log file |
| -f, --use-fallback | Use fallback CDN links (for China network) |

### Output Files

After execution, the script generates:
- organized_cn_mark.txt
- custom_cn_mark.txt
- generate.log (if --log specified)

## Data Sources

Rules are aggregated from the following sources (in priority order):

1. Aethersailor/Custom_OpenClash_Rules
   - URL: https://github.com/Aethersailor/Custom_OpenClash_Rules

2. Loyalsoldier/v2ray-rules-dat
   - URL: https://github.com/Loyalsoldier/v2ray-rules-dat

3. v2fly/domain-list-community
   - URL: https://github.com/v2fly/domain-list-community

4. felixonmars/dnsmasq-china-list
   - URL: https://github.com/felixonmars/dnsmasq-china-list

## Deduplication Rules

- Duplicate domains keep the highest priority version
- Priority: Aethersailor > Loyalsoldier > v2fly > Other > Personal Custom

## Output Format

The script outputs rules in PaoPaoDNS format:

```
domain:example.com      # Domain suffix match (includes subdomains)
full:example.com      # Exact match only
keyword:example       # Keyword match
regexp:.*\.example\.com$  # Regex match
```

## Automation

GitHub Actions workflow (`.github/workflows/auto-update.yml`):

- Trigger: Daily at 03:00 UTC + Manual trigger + Push to main branch
- Process: Fetch rules -> Run script -> Commit and push updates
- Output: Automatically generated custom_cn_mark.txt and organized_cn_mark.txt

## Network Configuration

The script supports fallback URLs for China network:

- Default: Use raw.githubusercontent.com and github.com
- Fallback for raw.githubusercontent.com: Use jsdelivr.net CDN
- Fallback for github.com: Use ghfast.top proxy
- Option `-f` or `--use-fallback`: Directly use fallback URLs

## Custom Rule Format

### custom.txt Format

```
domain:example.com
full:example.org
keyword:google
```

### custom_rule.txt Format

```
https://raw.githubusercontent.com/username/repo/main/rules.txt
```

## Error Handling

- If download fails after all fallback attempts: Script exits with error
- If parsed rules count is 0: Script exits with error (possible network issue or invalid URL)
- If download is abnormal: Switch to fallback URL automatically

## Subscription URLs

- GitHub Raw: https://raw.githubusercontent.com/Hi-Jiajun/CN-Domain-Rule-Auto-Generator/main/custom_cn_mark.txt
- China CDN: https://ghfast.top/https://raw.githubusercontent.com/Hi-Jiajun/CN-Domain-Rule-Auto-Generator/main/custom_cn_mark.txt
