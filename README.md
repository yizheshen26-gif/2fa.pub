<div align="right">
  <a href="README.md">English</a> · <a href="README.zh-CN.md">简体中文</a> · <a href="README.ja.md">日本語</a>
</div>

<div align="center">

# 2fa.pub

**A minimal, 100% local 2FA / TOTP code calculator — keys never leave your device.**

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Live site](https://img.shields.io/badge/Live-2fa.pub-10b981.svg)](https://2fa.pub/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-blue.svg)](https://github.com/yizheshen26-gif/2fa.pub/pulls)

</div>

> ⚠️ **Official deployment: [https://2fa.pub](https://2fa.pub/) only.** Any other site running modified versions of this code is not affiliated — never paste secrets into an instance you don't control. Self-hosting for yourself is fine and encouraged.

## What is this?

2fa.pub is a keyboard-driven, zero-trust 2FA toolkit that runs entirely in your browser.
Paste a Base32 secret, an `otpauth://` link, or a QR screenshot — get a live TOTP code
computed with the native Web Crypto API. There is **no backend**: nothing to upload to,
nothing to leak to. Verify it yourself with the F12 network panel.

## Tools

| Tool | What it does |
|---|---|
| **TOTP Calculator** | RFC 6238 codes (SHA-1/256/512, 6/8 digits, custom periods), multi-line batch cleanup (`account----password----secret`, CSV, pipes) |
| **Google Authenticator Export Decoder** | Decode `otpauth-migration://` export QR codes / links into Base32 secrets, fully offline |
| **QR Generator** | Turn secrets back into scannable `otpauth://` QR codes |
| **Steam Guard Calculator** | Steam mobile authenticator 5-character codes from `maFile` / shared secrets |
| **Encrypted Vault** | AES-256-GCM local secret storage, protected by a master password |
| **CLI & Audit** | oathtool / Python one-liners, live network audit proving zero key egress |

## Keyboard workflow

| Shortcut | Action |
|---|---|
| `Ctrl+V` (anywhere) | Paste a secret / QR screenshot → parsed instantly |
| `Ctrl+C` (no selection) | Copy the live code; within ≤4 s of expiry it copies the next period's code (smart rollover) |
| `Alt+1` … `Alt+6` | Switch between the six tools |
| `/` | Focus the input box |
| `Esc` | Burn memory — wipe everything from the page instantly |

Optional: enable **"Advance to next row after copy"** in the account list to keep Ctrl+C
walking down a batch of accounts, one code per press.

URL hash bookmarks work too: `https://2fa.pub/#secret=JBSWY3DPEHPK3PXP&label=GitHub` —
hash parameters are never sent to the server.

## Security model

- **100% local computation** — TOTP/Steam/AES all use the browser's native `crypto.subtle`.
  Secrets exist only in page memory and (optionally) the encrypted vault's localStorage.
- **White-box auditable crypto core** — the production build deliberately keeps the crypto
  layer unminified so anyone can audit it via F12.
- **Domain-locked production build** — the obfuscated business shell refuses to run on
  unauthorized mirror domains.
- **Analytics, minimized** — GA4 and AdSense IDs are hardcoded (there is no backend to
  reconfigure them); all reporting strips URL hash anchors, so secrets never enter analytics.
- The obfuscated production artifacts are reproducible from this repo via the build script —
  what you see on 2fa.pub can be verified against what you build here.

## Build

```bash
# 1. Generate the static Tailwind CSS (only needed when utility classes change)
npx tailwindcss@3.4.17 -i tailwind.input.css -o assets/tailwind.css --minify

# 2. Build the obfuscated production HTML and the deployment zip
python obfuscate_build.py --zip
```

The build splits the code into two layers: a readable, white-box auditable crypto core, and
an obfuscated business shell (string-pool XOR, identifier mangling, domain lock).
`2fa-pub-deploy.zip` contains the ready-to-serve static site (`index.prod.html` is zipped as
`index.html`, plus per-tool pre-rendered routes).

## Deploy (Cloudflare Pages)

The official site deploys via **direct upload**: create a Pages project, drag
`2fa-pub-deploy.zip` into a new deployment, done. `_headers` (CSP), `_redirects`
(clean-URL rewrites), `sw.js` (service worker: network-first navigations,
stale-while-revalidate assets) and `ads.txt` are all included in the zip.

## Guides

Deep-dive articles, each available in 简体中文 / English / 日本語:

- [Decoding Google Authenticator exports (otpauth-migration)](https://2fa.pub/guides/en/google-authenticator-export)
- [Transferring Google Authenticator to a new phone](https://2fa.pub/guides/en/google-authenticator-transfer-new-phone)
- [Lost 2FA secret recovery](https://2fa.pub/guides/en/lost-2fa-secret-recovery)

## Contributing

Issues and PRs are welcome — especially security reviews of the crypto core.
Please don't open PRs that add server-side key transmission; that would defeat
the entire point of the project.

## License

[MIT](LICENSE). Bundled third-party components (lucide, jsQR, qrcode-generator,
Inter/JetBrains Mono fonts) keep their own licenses — see the notes in `LICENSE`.
