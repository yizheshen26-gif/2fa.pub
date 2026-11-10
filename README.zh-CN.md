<div align="right">
  <a href="README.md">English</a> · <a href="README.zh-CN.md">简体中文</a> · <a href="README.ja.md">日本語</a>
</div>

<div align="center">

# 2fa.pub

**极简、100% 本地计算的 2FA / TOTP 验证码工具——密钥永不离开你的设备。**

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![在线使用](https://img.shields.io/badge/在线版-2fa.pub-10b981.svg)](https://2fa.pub/)
[![欢迎 PR](https://img.shields.io/badge/PRs-welcome-blue.svg)](https://github.com/yizheshen26-gif/2fa.pub/pulls)

</div>

> ⚠️ **官方部署仅有 [https://2fa.pub](https://2fa.pub/)。** 其他运行修改版代码的站点与本站无关——不要往你不控制的实例里粘贴密钥。自己自托管使用是允许且受欢迎的。

## 这是什么？

2fa.pub 是一套全键盘流、零信任的 2FA 工具集，完全运行在你的浏览器里。
粘贴 Base32 密钥、`otpauth://` 链接或二维码截图，即可用浏览器原生 Web Crypto API
实时算出 TOTP 验证码。**没有后端**：没有上传目标，也就没有泄露目标。
你可以用 F12 网络面板亲自验证。

## 六大工具

| 工具 | 功能 |
|---|---|
| **TOTP 计算器** | RFC 6238（SHA-1/256/512、6/8 位、自定义周期），多行账密批量清洗（`账号----密码----密钥`、CSV、竖线分隔） |
| **Google Authenticator 导出解析** | 把 `otpauth-migration://` 导出二维码/链接解码为 Base32 密钥，全程离线 |
| **二维码生成器** | 把密钥转回可扫描的 `otpauth://` 二维码 |
| **Steam Guard 计算器** | 从 `maFile` / shared secret 计算 Steam 移动验证器 5 位令牌 |
| **加密保险柜** | AES-256-GCM 本地密钥存储，主密码保护 |
| **CLI 与审计** | oathtool / Python 一行命令，实时网络审计证明密钥零外发 |

## 全键盘工作流

| 快捷键 | 功能 |
|---|---|
| `Ctrl+V`（任意位置） | 粘贴密钥 / 二维码截图 → 立即解析 |
| `Ctrl+C`（无划词时） | 复制当前验证码；剩余 ≤4 秒时自动复制下一周期（智能顺延） |
| `Alt+1` … `Alt+6` | 切换六个工具 |
| `/` | 聚焦输入框 |
| `Esc` | 焚毁内存——立即清空页面上的一切 |

可选：在账号列表勾选**"复制后移到下一行"**，Ctrl+C 会沿账号批量逐行推进，一键一码。

也支持 URL 书签：`https://2fa.pub/#secret=JBSWY3DPEHPK3PXP&label=GitHub` ——
锚点参数不会随 HTTP 请求发送，物理级不经过服务器。

## 安全模型（如实描述）

- **100% 本地计算** —— TOTP/Steam/AES 全部使用浏览器原生 `crypto.subtle`。
  密钥只存在于页面内存与（可选的）加密保险柜 localStorage 中。
- **白盒可审计加密核** —— 生产构建刻意保持加密层不混淆，任何人都能用 F12 逐行审计。
- **域名锁** —— 混淆后的业务壳在未授权镜像域名上拒绝执行。
- **统计最小化** —— GA4 与 AdSense ID 硬编码在源码中（没有可篡改的后台）；
  所有上报强制剥离 URL 锚点，密钥绝不进入统计。
- **产物可复现** —— 本仓库通过构建脚本即可生成与 2fa.pub 线上一致的混淆产物，
  可自行对比验证。

## 构建

```bash
# 1. 生成静态 Tailwind CSS（仅在工具类变化时需要）
npx tailwindcss@3.4.17 -i tailwind.input.css -o assets/tailwind.css --minify

# 2. 构建混淆产物与部署 zip
python obfuscate_build.py --zip
```

构建产物分两层：可读的白盒可审计加密核 + 混淆业务壳（字符串池 XOR、标识符重命名、
域名锁）。`2fa-pub-deploy.zip` 即可直接部署的静态站点（`index.prod.html` 在 zip 中
作为 `index.html`，另含每个工具的预渲染子路由页）。

## 部署（Cloudflare Pages）

官方站点使用 **direct upload** 部署：创建 Pages 项目后，把 `2fa-pub-deploy.zip`
拖进新部署即可。`_headers`（CSP）、`_redirects`（clean URL 重写）、`sw.js`
（Service Worker：导航 network-first、静态资源 stale-while-revalidate）与
`ads.txt` 均包含在 zip 内。

## 指南

深度教程，每篇均有 简体中文 / English / 日本語 版本：

- [解析 Google Authenticator 导出码（otpauth-migration）](https://2fa.pub/guides/google-authenticator-export)
- [Google Authenticator 换手机迁移](https://2fa.pub/guides/google-authenticator-transfer-new-phone)
- [2FA 密钥丢失恢复](https://2fa.pub/guides/lost-2fa-secret-recovery)

## 参与

欢迎 Issue 与 PR——尤其是对加密核的安全审计。请不要提交会把密钥传往服务端的改动，
那与本项目的目标背道而驰。

## 许可

[MIT](LICENSE)。打包的第三方组件（lucide、jsQR、qrcode-generator、
Inter/JetBrains Mono 字体）遵循各自的原许可——见 `LICENSE` 中的说明。
