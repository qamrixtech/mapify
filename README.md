<div align="center">

```
 __  ___            _ ____     
/  |/  /___ _____  (_) __/_  __
/ /|_/ / __ `/ __ \/ / /_/ / / /
/ /  / / /_/ / /_/ / __/ /_/ / 
/_/  /_/\__,_/ .___/_/_/  \__, / 
            /_/          /____/   
```

# SEO Sitemap Generator with HTTP/3 Stealth & TLS Impersonation

**v2.0.0** | Developed By **Hayder** | Property of **Qamrix Tech**

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Qamrix Tech](https://img.shields.io/badge/Made_by-Qamrix_Tech-cyan.svg)](https://github.com/qamrixtech/mapify)

*Building intelligent solutions that drive progress and shape the future.*

</div>

---

## About

**Mapify** is a powerful ethical SEO sitemap generator built by **Hayder**, Owner of **Qamrix Tech** — a future tech company focused on building intelligent solutions that drive progress and shape the future.

It crawls websites while respecting `robots.txt` and produces comprehensive SEO-rich XML sitemaps. Features HTTP/3 QUIC protocol support, real browser TLS impersonation, rotating proxy support, and a beautiful interactive TUI.

| | |
|---|---|
| **Email** | [qamrixtech@gmail.com](mailto:qamrixtech@gmail.com) |
| **GitHub** | [github.com/qamrixtech/mapify](https://github.com/qamrixtech/mapify) |

---

## Features

### Stealth & Anti-Detection

| Feature | Description |
|---------|-------------|
| **HTTP/3 QUIC Protocol** | Uses the latest HTTP/3 via `curl_cffi` for faster, harder-to-block connections |
| **TLS Fingerprint Impersonation** | Mimics real Chrome, Firefox, Safari, Edge TLS fingerprints (JA3/JA4) |
| **24 Browser Targets** | Chrome 99-146, Firefox 133-147, Safari 15-26, Edge 99-101 |
| **User-Agent Rotation** | Rotates browser identity per request |
| **Real Browser Headers** | Full `Sec-Fetch-*`, `sec-ch-ua`, `Accept` headers matching real browsers |

### Proxy Support

| Type | Example |
|------|---------|
| **Single HTTP** | `http://127.0.0.1:8080` |
| **Single HTTPS** | `https://127.0.0.1:8443` |
| **Single SOCKS5** | `socks5://127.0.0.1:1080` |
| **Proxy List Rotation** | `--proxy-list proxy.txt` (rotates per request) |

### Smart Crawling

| Feature | Description |
|---------|-------------|
| **URL Canonicalization** | Strips tracking params, normalizes paths, deduplicates |
| **XenForo/vBulletin/phpBB Filter** | Skips member profiles, search, login, pagination junk |
| **Canonical Tag Respect** | Follows `<link rel="canonical">` to avoid duplicate pages |
| **Junk URL Detection** | Skips PDFs, images, archives, JS/CSS, session IDs, UTM params |
| **robots.txt Compliance** | Parses and respects all crawl rules |

### SEO Analysis

- Title length analysis (short/long warnings)
- Meta description coverage
- H1/H2 header structure
- Image ALT text coverage
- Internal/external link analysis
- Content size metrics

### Output Formats

| File | Description |
|------|-------------|
| `sitemap.xml` | Standard XML sitemap |
| `sitemap-images.xml` | Image sitemap with captions |
| `sitemap.json` | Full crawl data with SEO metadata |

---

## Screenshots

### Interactive TUI

<div align="center">

| Main Menu | Crawl Depth |
|:---------:|:-----------:|
| ![Main Menu](images/1.jpg) | ![Crawl Depth](images/2.jpg) |

| Request Delay | Max Pages |
|:-------------:|:---------:|
| ![Request Delay](images/3.jpg) | ![Max Pages](images/4.jpg) |

| Feature Toggle | Proxy Configuration |
|:--------------:|:-------------------:|
| ![Features](images/5.jpg) | ![Proxy](images/6.jpg) |

| Configuration Summary | Ready to Crawl |
|:---------------------:|:--------------:|
| ![Config](images/7.jpg) | ![Confirm](images/7.jpg) |

</div>

### Crawl in Progress

<div align="center">

| Crawl Initiated | robots.txt Analysis |
|:---------------:|:-------------------:|
| ![Crawl Start](images/8.jpg) | ![robots.txt](images/8.jpg) |

</div>

### SEO Analysis & Results

<div align="center">

| SEO Analysis | Detailed Metrics |
|:------------:|:----------------:|
| ![SEO](images/9.jpg) | ![Metrics](images/10.jpg) |

| Crawl Complete | Output Files |
|:--------------:|:------------:|
| ![Complete](images/10.jpg) | ![Output](images/11.jpg) |

</div>

---

## Installation

```bash
git clone https://github.com/qamrixtech/mapify.git
cd mapify
python -m venv venv
source venv/bin/activate   # Linux/macOS
pip install -r requirements.txt
```

### Requirements

- Python 3.8+
- `curl_cffi` (HTTP/3 + TLS impersonation)
- `PySocks` (SOCKS5 proxy support)

---

## Quick Start

### Interactive Mode (Recommended)

```bash
python mapify.py -i
```

Launches a beautiful TUI where you select options with arrow keys:

```
                 Main Menu
  > Start New Crawl
    Quick Crawl (stealth defaults)
    Exit
```

### Command Line

```bash
# Basic crawl
python mapify.py https://example.com

# Full options
python mapify.py https://example.com \
  --depth 5 \
  --delay 0.5 \
  --max-pages 5000 \
  --images \
  --proxy socks5://127.0.0.1:1080 \
  --verbose

# With proxy list
python mapify.py https://example.com --proxy-list proxy.txt

# Quick defaults (depth 3, 1000 pages, stealth on)
python mapify.py https://example.com --stealth
```

---

## Proxy List Format

Create a `proxy.txt` file with one proxy per line:

```
# Comments are ignored
http://127.0.0.1:8080
https://proxy.example.com:8443
socks5://127.0.0.1:1080
http://user:pass@proxy.example.com:3128
```

Mapify rotates through proxies automatically, using a different proxy for each request.

---

## Configuration File

Create a `config.yaml`:

```yaml
crawler:
  max_depth: 5
  delay: 0.5
  max_pages: 5000
  max_workers: 4
  timeout: 15
  strip_queries: true
  skip_xenforo_junk: true
  stealth_mode: true
  proxy: "socks5://127.0.0.1:1080"
```

```bash
python mapify.py https://example.com --config config.yaml
```

---

## CLI Options

| Option | Default | Description |
|--------|---------|-------------|
| `--depth` | 3 | Crawl depth (1-10) |
| `--delay` | 1.0 | Seconds between requests |
| `--max-pages` | 1000 | Max pages to crawl |
| `--images` | off | Include images in sitemap |
| `--proxy` | none | Single proxy URL |
| `--proxy-list` | none | Proxy list file path |
| `--stealth/--no-stealth` | on | HTTP/3 + TLS impersonation |
| `--strip-queries/--keep-queries` | strip | Remove tracking query params |
| `--skip-xenforo/--no-skip-xenforo` | on | Filter XenForo/vBulletin junk |
| `--verbose` | off | Show each page as crawled |
| `--output` | output | Output directory |
| `--config` | none | YAML config file |
| `-i` | off | Interactive TUI mode |

---

## Output Structure

```
output/
  sitemap.xml          # Standard XML sitemap
  sitemap-images.xml   # Image sitemap (if --images)
  sitemap.json         # Full crawl data + SEO metadata
```

---

## How It Works

1. **Fetches robots.txt** and parses crawl rules
2. **Starts from homepage**, discovers internal links
3. **For each page**: rotates browser fingerprint, makes HTTP/3 request with real TLS
4. **Parses HTML** — extracts titles, meta, headers, links, images
5. **Canonicalizes URLs** — strips junk params, deduplicates
6. **Recurses** internal links up to configured depth
7. **Generates** XML sitemap + JSON summary

---

## Platform Support

- Linux (primary)
- macOS
- Windows (WSL recommended)

---

## License

```
Copyright (c) 2026 Qamrix Tech. All Rights Reserved.
Developed By Hayder
```

See [LICENSE](LICENSE) for details.

---

<div align="center">

![Qamrix Tech](images/QamrixBanner.png)

</div>