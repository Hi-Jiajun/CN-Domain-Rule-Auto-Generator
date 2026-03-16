# CN-Domain-Rule-Auto-Generator

中国大陆直连域名标记规则自动生成工具

[English README](./README_EN.md)

## 项目简介

本项目专为 [PaoPaoDNS](https://github.com/kkkgo/PaoPaoDNS) 项目生成 `custom_cn_mark.txt` 规则文件，自动聚合多上游优质大陆直连域名，按优先级去重、清理失效规则、格式化输出，每日自动更新，无需手动维护。

## 功能特性

- **多源聚合**：按优先级抓取多源域名规则（Aethersailor > Loyalsoldier > v2fly > 自定义链接规则 > 个人自定义域名）
- **国内网络友好**：所有规则拉取默认使用 ghfast.top 反向代理，国内用户可正常访问
- **智能去重**：自动去除重复规则，严格按优先级保留（高优先级覆盖低优先级）
- **失效清理**：自动清理注释失效域名
- **自定义支持**：支持本地 `custom.txt` 和 `custom_rule.txt` 自定义规则
- **格式转换**：自动格式化输出 PaoPaoDNS 专用规则语法
- **自动更新**：GitHub Actions 每日自动运行更新，保持规则实时最新

## 快速开始

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
```

### 命令行参数

| 参数 | 说明 |
|------|------|
| `-h`, `--help` | 显示帮助信息 |
| `-v`, `--verbose` | 显示详细输出 |
| `--log` | 生成日志文件 |
| `-f`, `--use-fallback` | 直接使用备用链接下载（大陆环境） |

## 配置文件说明

### 输入/配置文件

| 文件 | 说明 |
|------|------|
| `custom.txt` | 个人自定义域名列表（可选） |
| `custom_rule.txt` | 第三方规则链接列表（可选） |

### 输出文件

| 文件 | 说明 |
|------|------|
| `organized_cn_mark.txt` | 合并去重后的原始规则文件 |
| `custom_cn_mark.txt` | PaoPaoDNS 项目专用最终规则文件 |

## 直接订阅使用

### GitHub Raw 链接

- [custom_cn_mark.txt](https://raw.githubusercontent.com/Hi-Jiajun/CN-Domain-Rule-Auto-Generator/main/custom_cn_mark.txt)
- [organized_cn_mark.txt](https://raw.githubusercontent.com/Hi-Jiajun/CN-Domain-Rule-Auto-Generator/main/organized_cn_mark.txt)

### 国内加速链接

- custom_cn_mark.txt: `https://ghfast.top/https://raw.githubusercontent.com/Hi-Jiajun/CN-Domain-Rule-Auto-Generator/main/custom_cn_mark.txt`

## 规则数据来源

本项目规则数据来源于以下开源项目（按优先级排序）：

1. [Aethersailor/Custom_OpenClash_Rules](https://github.com/Aethersailor/Custom_OpenClash_Rules) - 最高优先级
2. [Loyalsoldier/v2ray-rules-dat](https://github.com/Loyalsoldier/v2ray-rules-dat)
3. [v2fly/domain-list-community](https://github.com/v2fly/domain-list-community)
4. [felixonmars/dnsmasq-china-list](https://github.com/felixonmars/dnsmasq-china-list)

## 适用项目

- [PaoPaoDNS](https://github.com/kkkgo/PaoPaoDNS) - 本规则专用适配项目

## 致谢

感谢以下开源项目的贡献者：

- PaoPaoDNS 项目
- Aethersailor
- Loyalsoldier
- v2fly
- felixonmars

## 捐赠支持

如本项目对你有帮助，欢迎赞赏支持，感谢你的鼓励～

<!-- 捐赠码图片路径（本地展示，不上传仓库） -->
<!-- 支付宝：C:\Users\hiliang\Pictures\个人收款码\alipay_qrcode.jpg -->
<!-- 微信支付：C:\Users\hiliang\Pictures\个人收款码\wechat_qrcode.png -->

## License

MIT License
