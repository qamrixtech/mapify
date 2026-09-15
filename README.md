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

**v2.0** | Developed By **Hayder** | Property of **Qamrix Tech**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

*Building intelligent solutions that drive progress and shape the future.*

</div>

---

## What is Mapify?

Mapify is a website crawler that generates SEO sitemaps while respecting robots.txt. It browses like a real visitor -- using real browser fingerprints and HTTP/3 -- so websites see it as normal traffic.

Feed it a URL, and it gives you a complete XML sitemap with SEO data: titles, descriptions, headers, images, and link structure.

**Contact:** [qamrixtech@gmail.com](mailto:qamrixtech@gmail.com) | [GitHub](https://github.com/qamrixtech/mapify)

---

## Screenshots

<table>
  <tr>
    <td align="center"><b>Launcher</b><br><sub>Auto-detects Python, installs deps</sub></td>
    <td align="center"><b>Main Menu</b><br><sub>Navigate with arrow keys</sub></td>
    <td align="center"><b>Crawl Depth</b><br><sub>How deep to follow links</sub></td>
  </tr>
  <tr>
    <td><img src="images/1.jpg" width="320"></td>
    <td><img src="images/2.jpg" width="320"></td>
    <td><img src="images/3.jpg" width="320"></td>
  </tr>
  <tr>
    <td align="center"><b>Request Delay</b><br><sub>Time between requests</sub></td>
    <td align="center"><b>Max Pages</b><br><sub>Limit total pages crawled</sub></td>
    <td align="center"><b>Feature Toggle</b><br><sub>Stealth, images, XenForo filter</sub></td>
  </tr>
  <tr>
    <td><img src="images/4.jpg" width="320"></td>
    <td><img src="images/5.jpg" width="320"></td>
    <td><img src="images/6.jpg" width="320"></td>
  </tr>
  <tr>
    <td align="center"><b>Proxy Config</b><br><sub>SOCKS5/HTTP proxy support</sub></td>
    <td align="center"><b>Config Summary</b><br><sub>Review before starting</sub></td>
    <td align="center"><b>Ready to Crawl</b><br><sub>Confirm and start</sub></td>
  </tr>
  <tr>
    <td><img src="images/7.jpg" width="320"></td>
    <td><img src="images/8.jpg" width="320"></td>
    <td><img src="images/9.jpg" width="320"></td>
  </tr>
  <tr>
    <td align="center"><b>Crawl in Progress</b><br><sub>Live progress tracking</sub></td>
    <td align="center"><b>SEO Analysis</b><br><sub>Title, meta, headers, links</sub></td>
    <td align="center"><b>Crawl Complete</b><br><sub>Summary with stats</sub></td>
  </tr>
  <tr>
    <td><img src="images/10.jpg" width="320"></td>
    <td><img src="images/11.jpg" width="320"></td>
    <td></td>
  </tr>
</table>

---

## Quick Start (Easiest Way)

**1. Clone the repo:**

```bash
git clone https://github.com/qamrixtech/mapify.git
cd mapify
```

**2. Run the launcher -- it handles everything:**

<table>
  <tr>
    <th>Platform</th>
    <th>Command</th>
  </tr>
  <tr>
    <td><b>Linux</b></td>
    <td><code>./run.sh</code></td>
  </tr>
  <tr>
    <td><b>macOS</b></td>
    <td><code>./run.sh</code></td>
  </tr>
  <tr>
    <td><b>Windows</b></td>
    <td><code>python run.py</code></td>
  </tr>
  <tr>
    <td><b>WSL</b></td>
    <td><code>./run.sh</code></td>
  </tr>
</table>

The launcher will:
- Find Python 3.10+ on your system
- Create a virtual environment automatically
- Install all required packages (curl_cffi, PySocks, rich, etc.)
- Launch Mapify

You don't need to install anything manually.

---

## Features

<table>
  <tr>
    <th>Stay Hidden</th>
    <th>Crawl Smart</th>
  </tr>
  <tr>
    <td>

- Looks like a real browser to websites
- Uses HTTP/3 (the latest protocol)
- Mimics Chrome, Firefox, Safari, Edge TLS fingerprints
- 24 browser identities to rotate through
- Real browser headers on every request

</td>
    <td>

- Respects robots.txt rules
- Skips junk URLs (login pages, search, pagination)
- Deduplicates pages automatically
- Filters XenForo/vBulletin forum junk
- Follows canonical tags to avoid repeats

</td>
  </tr>
</table>

<table>
  <tr>
    <th>SEO Data</th>
    <th>Flexible Output</th>
  </tr>
  <tr>
    <td>

- Title length analysis
- Meta description coverage
- H1/H2 header structure
- Image ALT text check
- Internal/external link count
- Content size metrics

</td>
    <td>

- XML sitemap for search engines
- Image sitemap with captions
- JSON file with full crawl data
- Choose output directory
- Proxy rotation support

</td>
  </tr>
</table>

---

## How to Use

### Interactive Mode (Recommended)

```bash
./run.sh
```

The launcher opens a menu where you use arrow keys to select:

1. **Enter target URL** -- the website you want to crawl
2. **Set crawl depth** -- how many links deep to follow (default: 3)
3. **Set request delay** -- seconds between requests (default: 1.0)
4. **Set max pages** -- limit total pages (default: 1000)
5. **Toggle features** -- stealth mode, images, XenForo filter
6. **Proxy config** -- optional HTTP/SOCKS5 proxy
7. **Confirm and start**

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

### CLI Options

| Option | Default | What it does |
|--------|---------|-------------|
| `--depth` | 3 | How deep to follow links (1-10) |
| `--delay` | 1.0 | Seconds to wait between requests |
| `--max-pages` | 1000 | Maximum pages to crawl |
| `--images` | off | Include images in the sitemap |
| `--proxy` | none | Use a single proxy (HTTP/HTTPS/SOCKS5) |
| `--proxy-list` | none | File with proxy list (rotates per request) |
| `--stealth` | on | Use HTTP/3 + browser TLS impersonation |
| `--strip-queries` | on | Remove tracking params from URLs |
| `--skip-xenforo` | on | Filter out forum junk URLs |
| `--verbose` | off | Show each page as it's crawled |
| `--output` | output | Where to save results |
| `--config` | none | Load settings from YAML file |
| `-i` | off | Interactive TUI mode |

---

## Proxy Support

Create a `proxy.txt` file with one proxy per line:

```
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

## Output

After crawling, Mapify saves to the `output/` directory:

```
output/
  sitemap.xml          # XML sitemap for search engines
  sitemap-images.xml   # Image sitemap (if --images)
  sitemap.json         # Full crawl data + SEO metadata
```

---

## File Structure

```
mapify/
  mapify.py            # Main tool (entry point)
  run.py               # Launcher (Windows / cross-platform)
  run.sh               # Launcher (Linux / macOS / WSL)
  requirements.txt     # Python dependencies
  setup.py             # Package setup
  config.yaml.example  # Example config
  LICENSE              # MIT License
  README.md            # Documentation
  images/              # Screenshots
  src/
    cli.py             # CLI and interactive menu
    crawler.py         # Core crawling engine
    ui.py              # TUI rendering
```

---

## Platform Support

| Platform | Status | How to launch |
|----------|--------|---------------|
| Linux | Supported | `./run.sh` |
| macOS | Supported | `./run.sh` |
| Windows | Supported | `python run.py` |
| WSL | Supported | `./run.sh` |

---

## Requirements

- Python 3.10 or higher
- That's it -- the launcher installs everything else automatically

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

*Made with <3 by Hayder -- Qamrix Tech*

</div>
