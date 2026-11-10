# 2fa.pub — 下一代纯前端零信任 2FA 工具站

面向开发者、QA 测试人员、跨境电商/矩阵工作室及极客群体的零信任、全键盘流、高颜值纯本地 2FA 瑞士军刀。

## 核心特性

1. **首屏即用，全局 `Ctrl+V` 盲粘秒出码**：无需点击输入框，任意位置粘贴单密钥或二维码截图即刻计算并自动写回剪贴板。
2. **`≤4s` 濒临过期智能顺延**：双周期并发计算，剩余 `≤4s` 自动激活珊瑚红脉冲并顺延复制下一周期验证码。
3. **URL `#Hash` 隐私书签直出**：支持 `2fa.pub/#secret=...&label=...` 书签秒算，锚点参数不随 HTTP 请求发送、物理级不经过服务器。
4. **Raycast 风格全键盘流**：`Ctrl+V` 盲粘、`Ctrl+C` 全局智能复制（支持划词自动放行与 ≤4s 顺延）、`/` 聚焦输入、`Alt+1~6` 切换工具、`Esc` 一键焚毁内存。
5. **六大工具**：TOTP 计算器（含多行账密批量清洗）、Google Authenticator 迁移码提取、二维码生成器、Steam Guard 令牌、AES-256-GCM 加密保险箱、CLI 命令与安全审计。

## 安全模型（如实描述）

- **密钥零外发**：所有 TOTP/Steam/AES 运算 100% 使用浏览器原生 `crypto.subtle`，密钥只存在于内存与 localStorage，代码可在 F12 白盒加密核中逐行审计。
- **统计与广告为固定配置**：GA4 (`G-LQ7821X2KZ`) 与 AdSense (`ca-pub-7685572758265529`) 硬编码在源码中，无后台修改入口。所有上报强制经过 `getSanitizedPageUrl()` 剥离 URL `#Hash` 锚点，密钥绝不进入上报内容。CSP（见 `_headers`）相应放行 Google Analytics / AdSense / Cloudflare Insights 域名——这是启用变现后的已知且最小化的外联白名单。
- **域名锁硬拦截**：生产构建（`obfuscate_build.py`）内置 `_0xVerifyDomain` 校验，非授权镜像域名上业务脚本直接拒绝执行并显示提示。
- **无管理后台**：站点不提供任何在线配置/管理功能，需要变更 ID 时直接改源码并重新构建。

## 构建

```bash
python obfuscate_build.py            # index.html -> index.prod.html
python obfuscate_build.py --zip      # 同时打包全站 zip
```

构建产物为双层结构：Layer 1 白盒可审计加密核（刻意不混淆）+ Layer 2 混淆业务壳（字符串池 XOR、标识符重命名、域名锁）。

## 部署（Cloudflare Pages）

1. 将 `index.prod.html` 重命名为 `index.html` 作为线上入口（开发版源码不要直接上线）。
2. `_headers`（CSP/安全头）、`_redirects`（`/google-extractor`、`/qr-generator`、`/steam`、`/cli` 的 SPA 重写，避免 sitemap 路由 404）、`ads.txt`（已配置真实发布商 ID）随站点根目录一起部署。
3. `sw.js` 为导航请求 network-first（保证更新即时生效）、静态资源 cache-first，离线时回退缓存页面。

## SEO

- 完整 `<meta>` 关键词矩阵、Canonical、`hreflang`（zh-CN / en / x-default）、Open Graph 与 Twitter Card。
- JSON-LD 结构化数据（`WebSite` + `WebApplication` + `FAQPage`）。
- `sitemap.xml` 与 `robots.txt` 齐全；sitemap 中的子路由由 `_redirects` 重写到单页应用。
