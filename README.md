# 🌏 CN-Domain-Rule-Auto-Generator

### 中国大陆直连域名规则自动生成工具

[![GitHub Stars](https://img.shields.io/github/stars/Hi-Jiajun/CN-Domain-Rule-Auto-Generator?style=flat)](https://github.com/Hi-Jiajun/CN-Domain-Rule-Auto-Generator/stargazers)
[![GitHub License](https://img.shields.io/github/license/Hi-Jiajun/CN-Domain-Rule-Auto-Generator)](LICENSE)
[![Auto Update](https://github.com/Hi-Jiajun/CN-Domain-Rule-Auto-Generator/actions/workflows/auto-update.yml/badge.svg)](https://github.com/Hi-Jiajun/CN-Domain-Rule-Auto-Generator/actions)

[English](./README_EN.md) | [中文](./README.md)

---

## 📋 项目简介

本项目专为 [PaoPaoDNS](https://github.com/kkkgo/PaoPaoDNS) 生成 `custom_cn_mark.txt` 规则文件，实现以下功能：

- 🔄 **多源聚合** - 自动抓取多个上游优质大陆直连域名规则
- 🇨🇳 **国内网络友好** - 使用 JsDelivr CDN / ghfast.top 反向代理，国内用户可正常访问
- 🔀 **智能去重** - 自动去除重复规则，严格按优先级保留
- 🧹 **失效清理** - 自动清理注释失效域名
- ⚙️ **自定义支持** - 支持本地自定义规则扩展
- 🔄 **自动更新** - GitHub Actions 每日自动运行，并支持手动触发，保持规则实时最新

---

## 🚀 快速开始

### 本地运行

```bash
# 克隆仓库
git clone https://github.com/Hi-Jiajun/CN-Domain-Rule-Auto-Generator.git
cd CN-Domain-Rule-Auto-Generator

# 运行脚本
python3 generate_cn_rules.py

# 查看帮助
python3 generate_cn_rules.py -h

# 详细输出
python3 generate_cn_rules.py -v

# 大陆环境使用备用链接
python3 generate_cn_rules.py -v -f

# 生成日志并刷新本地缓存
python3 generate_cn_rules.py --log

# 仅使用本地缓存，不发起网络下载
python3 generate_cn_rules.py --no-download

# 启动交互式自定义规则管理工具
python3 manage_custom_rules.py

# 直接通过命令行添加一条自定义规则
python3 manage_custom_rules.py add-rule domain:example.com

# 通过配置文件批量执行非交互操作
python3 manage_custom_rules.py run-config manage_custom_rules.toml

# 仅使用缓存重新生成
python3 manage_custom_rules.py generate --no-download
```

### 命令行参数

| 参数 | 说明 |
|------|------|
| `-h`, `--help` | 显示帮助信息 |
| `-v`, `--verbose` | 显示详细输出 |
| `--log` | 生成日志文件，并在默认模式下刷新 `.cache/` |
| `--no-download` | 跳过网络下载，仅使用 `.cache/` 中已缓存的源文件 |
| `-f`, `--use-fallback` | 直接使用备用链接下载（大陆环境） |

---

## 📁 文件说明

### 输入/配置文件

| 文件 | 说明 |
|------|------|
| `custom.txt` | 个人自定义域名列表（可选） |
| `custom_rule.txt` | 第三方规则链接列表（可选） |
| `manage_custom_rules.toml` | 批量非交互配置文件（可选） |

### 输出文件

| 文件 | 说明 |
|------|------|
| `organized_cn_mark.txt` | 合并去重后的原始规则文件 |
| `custom_cn_mark.txt` | PaoPaoDNS 项目专用最终规则文件 |

### 交互式与配置化管理

如果你不想手动编辑 `custom.txt` / `custom_rule.txt`，可以使用 `manage_custom_rules.py` 进行交互式或命令行管理。

示例：

```bash
python3 manage_custom_rules.py list-rules
python3 manage_custom_rules.py add-rule full:api.example.com
python3 manage_custom_rules.py add-url https://example.com/rules.txt
python3 manage_custom_rules.py run-config manage_custom_rules.toml
python3 manage_custom_rules.py generate --no-download
```

仓库内也提供了 [manage_custom_rules.toml](./manage_custom_rules.toml) 示例配置，可用于批量非交互操作，例如：

- 添加或删除 `custom.txt` 中的本地规则
- 添加或删除 `custom_rule.txt` 中的第三方规则链接
- 在完成增删后按配置决定是否自动重新生成规则

---

## 📊 规则数据来源

本项目规则数据来源于以下开源项目：

| 来源 | 仓库 |
|------|------|
| Custom_OpenClash_Rules | [Aethersailor/Custom_OpenClash_Rules](https://github.com/Aethersailor/Custom_OpenClash_Rules) |
| v2ray-rules-dat | [Loyalsoldier/v2ray-rules-dat](https://github.com/Loyalsoldier/v2ray-rules-dat) |
| domain-list-community | [v2fly/domain-list-community](https://github.com/v2fly/domain-list-community) |
| dnsmasq-china-list | [felixonmars/dnsmasq-china-list](https://github.com/felixonmars/dnsmasq-china-list) |

---

## 🔗 直接订阅使用

### GitHub Raw 链接

| 文件 | 链接 |
|------|------|
| custom_cn_mark.txt | [https://raw.githubusercontent.com/Hi-Jiajun/CN-Domain-Rule-Auto-Generator/main/custom_cn_mark.txt](https://raw.githubusercontent.com/Hi-Jiajun/CN-Domain-Rule-Auto-Generator/main/custom_cn_mark.txt) |
| organized_cn_mark.txt | [https://raw.githubusercontent.com/Hi-Jiajun/CN-Domain-Rule-Auto-Generator/main/organized_cn_mark.txt](https://raw.githubusercontent.com/Hi-Jiajun/CN-Domain-Rule-Auto-Generator/main/organized_cn_mark.txt) |

### JsDelivr CDN 链接

| 文件 | 链接 |
|------|------|
| custom_cn_mark.txt | [https://cdn.jsdelivr.net/gh/Hi-Jiajun/CN-Domain-Rule-Auto-Generator@main/custom_cn_mark.txt](https://cdn.jsdelivr.net/gh/Hi-Jiajun/CN-Domain-Rule-Auto-Generator@main/custom_cn_mark.txt) |
| organized_cn_mark.txt | [https://cdn.jsdelivr.net/gh/Hi-Jiajun/CN-Domain-Rule-Auto-Generator@main/organized_cn_mark.txt](https://cdn.jsdelivr.net/gh/Hi-Jiajun/CN-Domain-Rule-Auto-Generator@main/organized_cn_mark.txt) |

### 国内加速链接 (ghfast.top)

| 文件 | 链接 |
|------|------|
| custom_cn_mark.txt | [https://ghfast.top/https://raw.githubusercontent.com/Hi-Jiajun/CN-Domain-Rule-Auto-Generator/main/custom_cn_mark.txt](https://ghfast.top/https://raw.githubusercontent.com/Hi-Jiajun/CN-Domain-Rule-Auto-Generator/main/custom_cn_mark.txt) |
| organized_cn_mark.txt | [https://ghfast.top/https://raw.githubusercontent.com/Hi-Jiajun/CN-Domain-Rule-Auto-Generator/main/organized_cn_mark.txt](https://ghfast.top/https://raw.githubusercontent.com/Hi-Jiajun/CN-Domain-Rule-Auto-Generator/main/organized_cn_mark.txt) |

---

## 👏 致谢

感谢以下开源项目的贡献者：

- **[PaoPaoDNS](https://github.com/kkkgo/PaoPaoDNS)** - 本规则专用适配项目
- **[Aethersailor](https://github.com/Aethersailor)** - Custom_OpenClash_Rules
- **[Loyalsoldier](https://github.com/Loyalsoldier)** - v2ray-rules-dat
- **[v2fly](https://github.com/v2fly)** - domain-list-community
- **[felixonmars](https://github.com/felixonmars)** - dnsmasq-china-list

---

## ⭐ Star History

[![Star History Chart](https://api.star-history.com/svg?repos=Hi-Jiajun/CN-Domain-Rule-Auto-Generator&type=Date)](https://star-history.com/#Hi-Jiajun/CN-Domain-Rule-Auto-Generator&Date)

---

## 💖 赞赏支持

如果本项目对你有帮助，欢迎赞赏支持，感谢你的鼓励！

| 支付宝 | 微信支付 |
|:------:|:--------:|
| <img src="https://Hi-Jiajun.github.io/picx-images-hosting/alipay_qrcode.7p45v27tjq.webp" width="150" /> | <img src="https://Hi-Jiajun.github.io/picx-images-hosting/wechat_qrcode.icohq9bcf.webp" width="150" /> |

---

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.
