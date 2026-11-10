"""
2fa.pub production build script.

Splits the dev index.html into:
  Layer 1 — white-box auditable crypto core (kept readable on purpose)
  Layer 2 — obfuscated business shell (string-pool XOR, identifier mangling,
            naive minification, hard domain lock)

Usage:
  python obfuscate_build.py                      # index.html -> index.prod.html
  python obfuscate_build.py --input src.html --output dist.html
  python obfuscate_build.py --zip                # also emit 2fa-pub-site-protected.zip
"""

import argparse
import base64
import os
import re
import zipfile

WHITEBOX_CRYPTO_CORE = """    // =========================================================================
    // [WHITE-BOX AUDITABLE CRYPTO CORE] - 100% Transparent Web Crypto RFC 6238
    // Intentionally unminified so security researchers can verify via F12 that
    // secrets never leave the browser and only enter window.crypto.subtle.
    // =========================================================================
    function base32ToBytes(base32) {
      const alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ234567';
      const cleaned = (base32 || '').toUpperCase().replace(/[^A-Z2-7]/g, '');
      let bits = 0, value = 0, index = 0;
      const output = new Uint8Array(Math.floor((cleaned.length * 5) / 8));
      for (let i = 0; i < cleaned.length; i++) {
        value = (value << 5) | alphabet.indexOf(cleaned[i]);
        bits += 5;
        if (bits >= 8) {
          output[index++] = (value >>> (bits - 8)) & 255;
          bits -= 8;
        }
      }
      return output;
    }

    function bytesToBase32(bytes) {
      const alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ234567';
      let bits = 0, value = 0, output = '';
      for (let i = 0; i < bytes.length; i++) {
        value = (value << 8) | bytes[i];
        bits += 8;
        while (bits >= 5) {
          output += alphabet[(value >>> (bits - 5)) & 31];
          bits -= 5;
        }
      }
      if (bits > 0) {
        output += alphabet[(value << (5 - bits)) & 31];
      }
      return output;
    }

    async function generateTOTP(secret, period, digits, algorithm, timestamp) {
      period = period || 30;
      digits = digits || 6;
      algorithm = algorithm || 'SHA-1';
      timestamp = typeof timestamp === 'number' ? timestamp : Date.now();
      const keyBytes = base32ToBytes(secret);
      if (keyBytes.length === 0) return ''.padStart(digits, '-');
      const counter = Math.floor(timestamp / 1000 / period);
      const counterBuffer = new ArrayBuffer(8);
      const view = new DataView(counterBuffer);
      view.setUint32(0, Math.floor(counter / 0x100000000), false);
      view.setUint32(4, counter & 0xffffffff, false);
      const cryptoKey = await crypto.subtle.importKey(
        'raw',
        keyBytes,
        { name: 'HMAC', hash: { name: algorithm } },
        false,
        ['sign']
      );
      const signature = new Uint8Array(await crypto.subtle.sign('HMAC', cryptoKey, counterBuffer));
      const offset = signature[signature.length - 1] & 0x0f;
      const binary =
        ((signature[offset] & 0x7f) << 24) |
        ((signature[offset + 1] & 0xff) << 16) |
        ((signature[offset + 2] & 0xff) << 8) |
        (signature[offset + 3] & 0xff);
      const otp = binary % Math.pow(10, digits);
      return otp.toString().padStart(digits, '0');
    }

    async function deriveAesGcmKey(password, saltBytes) {
      const enc = new TextEncoder();
      const baseKey = await crypto.subtle.importKey('raw', enc.encode(password), 'PBKDF2', false, ['deriveKey']);
      return crypto.subtle.deriveKey(
        { name: 'PBKDF2', salt: saltBytes, iterations: 100000, hash: 'SHA-256' },
        baseKey,
        { name: 'AES-GCM', length: 256 },
        false,
        ['encrypt', 'decrypt']
      );
    }

    async function computeCryptoCoreSha256() {
      const el = document.getElementById('auditable-crypto-core');
      const raw = el ? el.textContent : '';
      const buf = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(raw));
      return Array.from(new Uint8Array(buf)).map(function(b) { return b.toString(16).padStart(2, '0'); }).join('');
    }
"""

XOR_KEY = 0x5A


def encode_str_to_hex(s: str) -> str:
    raw = s.encode('utf-8')
    xored = bytes([b ^ XOR_KEY for b in raw])
    return base64.b64encode(xored).decode('ascii')


STRING_POOL_PLAIN = [
    "2fa.pub",                          # 0
    "localhost",                        # 1
    "127.0.0.1",                        # 2
    "googleusercontent.com",            # 3
    "google.com",                       # 4
    "otpauth://",                       # 5
    "otpauth-migration://",             # 6
    "23456789BCDFGHJKMNPQRTVWXY",       # 7
    "2fa_pub_aes_gcm_vault_v1",         # 8
    "PBKDF2-HMAC-SHA256",               # 9
    "AES-256-GCM",                      # 10
    "2fa_pub_monetization_cfg_v1",      # 11
    "2fa_pub_telemetry_stats_v1",       # 12
    ".pages.dev"                        # 13 - Cloudflare Pages official preview domains
]

INTERNAL_IDENTIFIERS = {
    'parsedAccounts': '_0x4f1a',
    'extractedMigrationAccounts': '_0x7c2b',
    'rowCopiedState': '_0x9e3d',
    'simulatedRolloverUntil': '_0x3b1f',
    'getSanitizedPageUrl': '_0x4e9a',
    'trackSiteEvent': '_0x9c4b',
    'injectAnalyticsAndAdsenseScripts': '_0x6b2e',
    'formatGroupedCodeHtml': '_0x2b8c',
    'parseBatchInput': '_0x8d4e',
    'getTotpSettings': '_0x5a9f',
    'escapeHtml': '_0x3c7a',
    'decodeQrFromImageFile': '_0x6e1b',
    'processDecodedQrString': '_0x1f4d',
    'base64UrlToUint8Array': '_0x9a2c',
    'readVarint': '_0x7b3e',
    'decodeOtpParametersEntry': '_0x4d8f',
    'decodeGoogleMigrationUri': '_0x2e6a',
    'buildDemoMigrationUri': '_0x5c1d',
    'STEAM_CHARS': '_0x8f2b',
    'extractSteamSecretBytes': '_0x3a6e',
    'computeSteamCodeForTimestamp': '_0x6d9c',
    'VAULT_STORAGE_KEY': '_0x1c5e',
    'uint8ToBase64': '_0x9b4a',
    'base64ToUint8': '_0x7e2d',
    'refreshVaultStatusPreview': '_0x4a7c',
    'checkUrlHashRoute': '_0x2d9e',
    'normalizeOtpAlgo': '_0x5e3a',
    'ROUTE_TO_TAB': '_0x6c8d',
    'TAB_TO_ROUTE': '_0x7a1f',
    'TAB_TITLE_KEY': '_0x8b4c',
    'TAB_DESC_KEY': '_0x4c9e',
    'OG_LOCALE_MAP': '_0x1d4a',
    'GUIDE_EXPORT_URL_MAP': '_0x2f8b',
    'syncRouteMeta': '_0x9d2e',
    'resolveInitialTabFromPath': '_0x3f7b',
    'hasActiveTextSelection': '_0x8e1c'
}

NEW_AUDIT_FN = """    async function runLiveSecurityAudit() {
      const box = document.getElementById('securityAuditResultBox');
      if (!box) return;
      const entries = (window.performance && window.performance.getEntriesByType)
        ? window.performance.getEntriesByType('resource')
        : [];
      const xhrFetchCalls = entries.filter(function(e) {
        return e.initiatorType === 'xmlhttprequest' || e.initiatorType === 'fetch' || e.initiatorType === 'beacon';
      });
      const subtleAvailable = !!(window.crypto && window.crypto.subtle);
      const coreHash = await computeCryptoCoreSha256();
      const shortHash = coreHash.slice(0, 12) + '…' + coreHash.slice(-12);
      const domainOk = _0xVerifyDomain();
      const tile = function(label, value, tone) {
        const color = tone === 'ok' ? 'text-emerald-400' : (tone === 'bad' ? 'text-red-400' : 'text-zinc-100');
        return '<div class="p-3 rounded-xl bg-zinc-950 border border-zinc-800">' +
          '<div class="text-[11px] text-zinc-400">' + label + '</div>' +
          '<div class="text-sm font-semibold font-mono-tabular mt-1 ' + color + '">' + value + '</div>' +
        '</div>';
      };
      box.innerHTML =
        tile(_t('auditCrypto'), subtleAvailable ? _t('auditCryptoOk') : _t('auditCryptoBad'), subtleAvailable ? 'ok' : 'bad') +
        tile(_t('auditRequests'), xhrFetchCalls.length + _t('auditReqUnit'), null) +
        tile(_t('auditCore'), shortHash, null) +
        tile(_t('auditDomain'), domainOk ? _t('auditDomainOk') : _t('auditDomainBad'), domainOk ? 'ok' : 'bad');
    }"""


def build_prod(orig_html: str) -> str:
    script_start_marker = '  <!-- ==================== CORE APPLICATION LOGIC ==================== -->\n  <script>'
    script_end_marker = '  </script>\n</body>'
    start_idx = orig_html.index(script_start_marker)
    end_idx = orig_html.index(script_end_marker, start_idx)
    orig_script_body = orig_html[start_idx + len(script_start_marker):end_idx]

    business_shell_js = orig_script_body

    # The four core crypto functions move to the white-box layer, drop them here.
    for fn_pattern in [
        r'function base32ToBytes\(base32\)\s*\{.*?\n    \}\n',
        r'function bytesToBase32\(bytes\)\s*\{.*?\n    \}\n',
        r'async function generateTOTP\(secret, period, digits, algorithm, timestamp\)\s*\{.*?\n    \}\n',
        r'async function deriveAesGcmKey\(password, saltBytes\)\s*\{.*?\n    \}\n',
    ]:
        business_shell_js = re.sub(fn_pattern, '', business_shell_js, flags=re.DOTALL)

    encoded_pool = [encode_str_to_hex(s) for s in STRING_POOL_PLAIN]

    for plain, idx in [
        ("'23456789BCDFGHJKMNPQRTVWXY'", 7),
        ("'2fa_pub_aes_gcm_vault_v1'", 8),
        ("'PBKDF2-HMAC-SHA256'", 9),
        ("'AES-256-GCM'", 10),
        ("'2fa_pub_monetization_cfg_v1'", 11),
        ("'2fa_pub_telemetry_stats_v1'", 12),
    ]:
        business_shell_js = business_shell_js.replace(plain, f"_0xS({idx})")

    for old_name, new_name in INTERNAL_IDENTIFIERS.items():
        business_shell_js = re.sub(rf'\b{old_name}\b', new_name, business_shell_js)

    business_shell_js = re.sub(
        r'function runLiveSecurityAudit\(\)\s*\{.*?\n    \}',
        NEW_AUDIT_FN.strip(),
        business_shell_js,
        flags=re.DOTALL
    )

    # Naive line minifier: drop blank lines, comment lines and trailing // comments.
    # Lines containing '://' (URLs) are kept verbatim to avoid eating protocol strings.
    lines = business_shell_js.splitlines()
    compact_lines = []
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith('//'):
            continue
        if '//' in stripped and '://' not in stripped and not stripped.startswith("'") and not stripped.startswith('"'):
            stripped = stripped.split('//')[0].strip()
        compact_lines.append(stripped)

    minified_business_js = ' '.join(compact_lines)

    protection_header_js = f"""    // =========================================================================
    // [PROTECTED BUSINESS & PARSER SHELL] - String Pool XOR + Hex Mangling + Domain Lock
    // =========================================================================
    const _0xPOOL = {encoded_pool!r};
    function _0xS(_0xIdx) {{
      const _0xRaw = atob(_0xPOOL[_0xIdx]);
      const _0xBytes = new Uint8Array(_0xRaw.length);
      for (let _0xI = 0; _0xI < _0xRaw.length; _0xI++) {{
        _0xBytes[_0xI] = _0xRaw.charCodeAt(_0xI) ^ {XOR_KEY};
      }}
      return new TextDecoder('utf-8').decode(_0xBytes);
    }}
    function _0xVerifyDomain() {{
      const _0xH = (window.location && window.location.hostname ? window.location.hostname : '').toLowerCase();
      if (!_0xH) return true;
      return (
        _0xH === _0xS(0) ||
        _0xH.endsWith('.' + _0xS(0)) ||
        _0xH === _0xS(1) ||
        _0xH === _0xS(2) ||
        _0xH.endsWith(_0xS(3)) ||
        _0xH.endsWith(_0xS(4)) ||
        _0xH.endsWith(_0xS(13))
      );
    }}
    // Hard domain lock: on unauthorized mirror domains the entire shell refuses to run.
    if (!_0xVerifyDomain()) {{
      document.body.innerHTML = '<div style="position:fixed;inset:0;display:flex;align-items:center;justify-content:center;background:#09090B;color:#f87171;font-family:monospace;text-align:center;padding:24px;font-size:14px;line-height:1.9;z-index:9999">2fa.pub<br>Unauthorized mirror domain.<br>Please visit the official website.</div>';
      throw new Error('unauthorized-domain');
    }}
"""

    protected_scripts_block = f"""  <!-- ==================== LAYER 1: WHITE-BOX AUDITABLE CRYPTO CORE ==================== -->
  <script id="auditable-crypto-core">
{WHITEBOX_CRYPTO_CORE}  </script>

  <!-- ==================== LAYER 2: OBFUSCATED BUSINESS & PARSER SHELL ==================== -->
  <script id="protected-app-shell">
{protection_header_js}
    {minified_business_js}
  </script>
"""

    prod_html = (
        orig_html[:start_idx]
        + protected_scripts_block
        + orig_html[end_idx + len('  </script>'):]
    )

    # ---- Full-function mangling -------------------------------------------
    # Every function referenced from HTML event attributes (onclick= etc.) or
    # from dynamically generated onclick strings must be renamed in BOTH the
    # JS and the HTML so the mapping stays consistent. Collect them all, then
    # apply a word-boundary rename across the whole document.
    handler_re = re.compile(r'\bon[a-z]+\s*=\s*"(\w+)\(')
    referenced = set(handler_re.findall(prod_html))
    # Extra helpers with no event-attribute references (called from JS only).
    referenced.update({
        'showToast', 'copyTextToClipboard', 'getDualTOTP', 'applyLanguage',
    })
    # Never touch the white-box audit layer or JS/platform built-ins.
    whitelist = {'generateTOTP', 'base32ToBytes', 'bytesToBase32', 'deriveAesGcmKey', 'computeCryptoCoreSha256'}
    referenced -= whitelist
    referenced -= set(INTERNAL_IDENTIFIERS)  # already renamed inside the shell

    import hashlib
    for name in sorted(referenced):
        new_name = '_0xF' + hashlib.md5(name.encode()).hexdigest()[:4]
        prod_html = re.sub(rf'\b{re.escape(name)}\b', new_name, prod_html)

    return prod_html



SUBROUTE_STATIC_META = {
    'google-extractor.html': {
        'tab': 'migration',
        'route': '/google-extractor',
        'title': 'Google Authenticator Export Extractor - 100% Local | 2fa.pub',
        'desc': 'Decode Google Authenticator export QR codes (otpauth-migration://) and extract plaintext Base32 secrets 100% locally in your browser. Zero uploads.',
        'h1': 'Google Authenticator Export QR Extractor (otpauth-migration://)',
    },
    'qr-generator.html': {
        'tab': 'qrgen',
        'route': '/qr-generator',
        'title': '2FA QR Generator - 100% Local | 2fa.pub',
        'desc': 'Generate standard otpauth:// 2FA QR codes from Base32 secrets 100% locally in your browser and download scannable PNG images for any authenticator app.',
        'h1': '100% Local 2FA / TOTP QR Code Generator',
    },
    'steam.html': {
        'tab': 'steam',
        'route': '/steam',
        'title': 'Steam Guard Token Calculator - 100% Local | 2fa.pub',
        'desc': 'Calculate 5-character Steam Guard tokens 100% locally in your browser from Base64 shared_secret, maFile JSON, or Base32 secrets with <=4s smart rollover.',
        'h1': '100% Local Steam Guard Token Calculator',
    },
    'vault.html': {
        'tab': 'vault',
        'route': '/vault',
        'title': 'Encrypted Vault (AES-256-GCM) - 100% Local | 2fa.pub',
        'desc': 'Encrypt and store your 2FA secrets locally in the browser using Web Crypto PBKDF2 (100,000 iterations) and AES-256-GCM zero-trust encryption.',
        'h1': 'Zero-Trust Browser-Local 2FA Encrypted Vault (AES-256-GCM)',
    },
    'cli.html': {
        'tab': 'cli',
        'route': '/cli',
        'title': 'One-line CLI 2FA generation - 100% Local | 2fa.pub',
        'desc': 'One-line terminal CLI snippets (oathtool & zero-dependency Python 3) for 2FA generation and live client-side Web Crypto security audit.',
        'h1': 'One-Line Terminal CLI 2FA & Live Web Crypto Security Audit',
    },
}


def build_subroute_html(base_prod_html: str, meta: dict) -> str:
    html = base_prod_html
    route = meta['route']
    tab = meta['tab']
    title = meta['title']
    desc = meta['desc']
    h1 = meta['h1']

    # Replace <title>, meta description, og:*, twitter:*, canonical, and hreflang URLs
    html = re.sub(r'<title>.*?</title>', f'<title>{title}</title>', html, count=1)
    html = re.sub(
        r'<meta name="description" content="[^"]*" />',
        f'<meta name="description" content="{desc}" />',
        html, count=1
    )
    html = re.sub(
        r'<link rel="canonical" href="[^"]*" />',
        f'<link rel="canonical" href="https://2fa.pub{route}" />',
        html, count=1
    )
    html = re.sub(
        r'<link rel="alternate" hreflang="en" href="[^"]*" />',
        f'<link rel="alternate" hreflang="en" href="https://2fa.pub{route}" />',
        html, count=1
    )
    html = re.sub(
        r'<link rel="alternate" hreflang="zh-CN" href="[^"]*" />',
        f'<link rel="alternate" hreflang="zh-CN" href="https://2fa.pub{route}?lang=zh" />',
        html, count=1
    )
    html = re.sub(
        r'<link rel="alternate" hreflang="ja" href="[^"]*" />',
        f'<link rel="alternate" hreflang="ja" href="https://2fa.pub{route}?lang=ja" />',
        html, count=1
    )
    html = re.sub(
        r'<link rel="alternate" hreflang="x-default" href="[^"]*" />',
        f'<link rel="alternate" hreflang="x-default" href="https://2fa.pub{route}" />',
        html, count=1
    )
    html = re.sub(
        r'<meta property="og:title" content="[^"]*" />',
        f'<meta property="og:title" content="{title}" />',
        html, count=1
    )
    html = re.sub(
        r'<meta property="og:description" content="[^"]*" />',
        f'<meta property="og:description" content="{desc}" />',
        html, count=1
    )
    html = re.sub(
        r'<meta property="og:url" content="[^"]*" />',
        f'<meta property="og:url" content="https://2fa.pub{route}" />',
        html, count=1
    )
    html = re.sub(
        r'<meta name="twitter:title" content="[^"]*" />',
        f'<meta name="twitter:title" content="{title}" />',
        html, count=1
    )
    html = re.sub(
        r'<meta name="twitter:description" content="[^"]*" />',
        f'<meta name="twitter:description" content="{desc}" />',
        html, count=1
    )
    html = re.sub(
        r'(<h1[^>]*>).*?(</h1>)',
        rf'\g<1>{h1}\g<2>',
        html, count=1
    )
    html = re.sub(
        r'(id="tabBtn-totp"[^>]*class=")[^"]*(")',
        r'\g<1>tab-nav-btn px-2.5 py-1.5 rounded-lg font-medium whitespace-nowrap transition text-zinc-400 hover:text-white\g<2>',
        html, count=1
    )
    html = re.sub(
        rf'(id="tabBtn-{tab}"[^>]*class=")[^"]*(")',
        r'\g<1>tab-nav-btn px-2.5 py-1.5 rounded-lg font-semibold whitespace-nowrap transition bg-emerald-500 text-zinc-950\g<2>',
        html, count=1
    )

    # Pre-activate the target tab section in static HTML so crawlers without JS see the tool immediately
    html = html.replace(
        '<section id="view-totp" class="space-y-4">',
        '<section id="view-totp" class="hidden space-y-4">'
    )
    html = html.replace(
        f'<section id="view-{tab}" class="hidden space-y-4">',
        f'<section id="view-{tab}" class="space-y-4">'
    )
    html = html.replace("let currentTab = 'totp';", f"let currentTab = '{tab}';")
    return html


def main() -> None:
    parser = argparse.ArgumentParser(description='Build obfuscated 2fa.pub production HTML.')
    parser.add_argument('--input', default='index.html', help='dev HTML source (default: index.html)')
    parser.add_argument('--output', default='index.prod.html', help='obfuscated HTML output (default: index.prod.html)')
    parser.add_argument('--zip', action='store_true', help='also package the site into 2fa-pub-site-protected.zip')
    args = parser.parse_args()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_path = args.input if os.path.exists(args.input) else os.path.join(script_dir, args.input)
    output_path = args.output if os.path.isabs(args.output) or os.path.dirname(args.output) else os.path.join(script_dir, args.output)

    with open(input_path, 'r', encoding='utf-8') as f:
        orig_html = f.read().replace('\r\n', '\n')

    prod_html = build_prod(orig_html)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(prod_html)
    print(f"Generated {args.output} ({len(prod_html)} bytes) from {args.input}.")

    subroute_pages = {}
    for fname, meta in SUBROUTE_STATIC_META.items():
        sub_html = build_subroute_html(prod_html, meta)
        subroute_pages[fname] = sub_html
        sub_out = os.path.join(script_dir, fname)
        with open(sub_out, 'w', encoding='utf-8') as sf:
            sf.write(sub_html)
        print(f"Pre-rendered static route page: {fname} ({len(sub_html)} bytes)")

    if args.zip:
        zip_path = os.path.join(script_dir, '2fa-pub-deploy.zip')
        static_files = ['ads.txt', '_headers', '_redirects', 'manifest.json', 'sw.js', 'robots.txt', 'sitemap.xml']
        static_dirs = ['assets', 'guides']
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            zf.writestr('index.html', prod_html)
            for fname, sub_html in subroute_pages.items():
                zf.writestr(fname, sub_html)
            for fname in static_files:
                fpath = os.path.join(script_dir, fname)
                if os.path.exists(fpath):
                    zf.write(fpath, arcname=fname)
            for dname in static_dirs:
                dpath = os.path.join(script_dir, dname)
                if os.path.isdir(dpath):
                    for root, _, files in os.walk(dpath):
                        for file in sorted(files):
                            full_p = os.path.join(root, file)
                            rel_p = os.path.relpath(full_p, script_dir)
                            zf.write(full_p, arcname=rel_p)
        print(f"Packaged clean deployment archive: {zip_path}.")


if __name__ == '__main__':
    main()
