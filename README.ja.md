<div align="right">
  <a href="README.md">English</a> · <a href="README.zh-CN.md">简体中文</a> · <a href="README.ja.md">日本語</a>
</div>

<div align="center">

# 2fa.pub

**ミニマルで 100% ローカル完結の 2FA / TOTP 認証コード計算ツール——シークレットは端末の外に出ません。**

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![公式サイト](https://img.shields.io/badge/Live-2fa.pub-10b981.svg)](https://2fa.pub/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-blue.svg)](https://github.com/yizheshen26-gif/2fa.pub/pulls)

</div>

> ⚠️ **公式デプロイは [https://2fa.pub](https://2fa.pub/) のみです。** 改変版を動かしている他のサイトとは無関係です——管理権のないインスタンスにシークレットを貼らないでください。自己利用でのセルフホストは自由です。

## これは何？

2fa.pub はブラウザ内で完全に動作する、キーボード駆動のゼロトラスト 2FA ツールキットです。
Base32 シークレット、`otpauth://` リンク、QR スクリーンショットを貼り付けると、
ブラウザのネイティブ Web Crypto API で TOTP コードをリアルタイム計算します。
**バックエンドは存在しません**：送信先が無ければ、漏えいも起り得ません。
F12 のネットワークパネルでご自身で検証できます。

## 6 つのツール

| ツール | 機能 |
|---|---|
| **TOTP 計算ツール** | RFC 6238（SHA-1/256/512、6/8 桁、カスタム周期）、複数行まとめて解析（`アカウント----パスワード----シークレット`、CSV、パイプ区切り） |
| **Google Authenticator エクスポート解析** | `otpauth-migration://` のエクスポート QR／リンクをオフラインで Base32 シークレットに変換 |
| **QR 生成ツール** | シークレットをスキャン可能な `otpauth://` QR コードに戻す |
| **Steam Guard 計算ツール** | `maFile`／shared_secret から Steam モバイル認証の 5 桁トークンを計算 |
| **暗号化ボールト** | AES-256-GCM のローカル保存、マスターパスワードで保護 |
| **CLI と監査** | oathtool／Python ワンライナー、シークレット零送信を実証するライブ監査 |

## キーボードワークフロー

| ショートカット | 動作 |
|---|---|
| `Ctrl+V`（ページのどこでも） | シークレット／QR スクショを貼り付け → 即解析 |
| `Ctrl+C`（文字未選択時） | 現在のコードをコピー。残り ≤4 秒なら次周期のコードを自動コピー（スマートロールオーバー） |
| `Alt+1` … `Alt+6` | 6 つのツールを切り替え |
| `/` | 入力欄にフォーカス |
| `Esc` | メモリ消去——ページ上のデータを即座に全消去 |

オプション：アカウント一覧で**「コピー後に次の行へ」**を有効にすると、Ctrl+C がアカウント列を順に進み、1 押しずつ次のアカウントのコードをコピーします。

URL ハッシュブックマークにも対応：`https://2fa.pub/#secret=JBSWY3DPEHPK3PXP&label=GitHub` ——ハッシュは HTTP リクエストに含まれないため、サーバーを経由しません。

## セキュリティモデル（正直な説明）

- **100% ローカル計算** —— TOTP／Steam／AES はすべてブラウザネイティブの `crypto.subtle` を使用。シークレットはページのメモリと（任意の）暗号化ボールトの localStorage にのみ存在します。
- **ホワイトボックス監査可能な暗号コア** —— 本番ビルドでは意図的に暗号層を難読化せず、F12 で誰でも一行ずつ監査できます。
- **ドメインロック** —— 難読化済みビジネスシェルは未許可のミラードメインでは実行を拒否します。
- **最小化されたアナリティクス** —— GA4 と AdSense の ID はソースにハードコードされており（変更できる管理画面はありません）、全レポートから URL ハッシュは剥離されるため、シークレットが統計に入ることはありません。
- **成果物の再現性** —— 本リポジトリのビルドスクリプトから 2fa.pub と同一の本番成果物を生成でき、比較検証できます。

## ビルド

```bash
# 1. 静的 Tailwind CSS の生成（ユーティリティクラス変更時のみ）
npx tailwindcss@3.4.17 -i tailwind.input.css -o assets/tailwind.css --minify

# 2. 難読化本番 HTML とデプロイ zip の生成
python obfuscate_build.py --zip
```

ビルドは 2 層構造です：可読なホワイトボックス暗号コア + 難読化ビジネスシェル
（文字列プール XOR、識別子リネーム、ドメインロック）。`2fa-pub-deploy.zip` は
そのまま配信可能な静的サイトです（`index.prod.html` は zip 内で `index.html` と
なり、ツール別のプリレンダリング済みルートも同梱）。

## デプロイ（Cloudflare Pages）

公式サイトは **direct upload** で運用しています：Pages プロジェクトを作成し、
`2fa-pub-deploy.zip` を新しいデプロイにドラッグするだけです。`_headers`（CSP）、
`_redirects`（クリーン URL リライト）、`sw.js`（Service Worker：ナビゲーションは
network-first、アセットは stale-while-revalidate）、`ads.txt` はすべて zip に同梱済みです。

## ガイド

詳解記事（各記事とも 简体中文 / English / 日本語 版あり）：

- [Google Authenticator エクスポートの解析（otpauth-migration）](https://2fa.pub/guides/ja/google-authenticator-export)
- [Google Authenticator の機種変更・移行](https://2fa.pub/guides/ja/google-authenticator-transfer-new-phone)
- [2FA シークレット紛失時の復旧](https://2fa.pub/guides/ja/lost-2fa-secret-recovery)

## コントリビューション

Issue・PR を歓迎します——特に暗号コアへのセキュリティレビューを。シークレットを
サーバーへ送る変更は、プロジェクトの趣旨に反するためお控えください。

## ライセンス

[MIT](LICENSE)。同梱のサードパーティコンポーネント（lucide、jsQR、
qrcode-generator、Inter／JetBrains Mono フォント）は各自のライセンス（ISC / Apache-2.0 / MIT / SIL OFL-1.1）に従います。
