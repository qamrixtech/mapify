#!/usr/bin/env python3
"""
Mapify Web Crawler
Respects robots.txt and generates comprehensive sitemaps
"""

import time
import re
import xml.etree.ElementTree as ET
from urllib.parse import urljoin, urlparse, urlunparse, parse_qs, urlencode
from urllib.robotparser import RobotFileParser
from bs4 import BeautifulSoup
from datetime import datetime
import os
import logging
import threading
import random

try:
    from curl_cffi import requests as curl_requests
    CURL_CFFI_AVAILABLE = True
except ImportError:
    CURL_CFFI_AVAILABLE = False

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

try:
    import yaml
    CONFIG_AVAILABLE = True
except ImportError:
    CONFIG_AVAILABLE = False

IMPERSONATE_TARGETS = [
    "chrome146",
    "chrome145",
    "chrome142",
    "chrome136",
    "chrome133a",
    "chrome131",
    "chrome131_android",
    "chrome124",
    "chrome123",
    "chrome120",
    "chrome119",
    "chrome116",
    "chrome110",
    "firefox147",
    "firefox144",
    "firefox135",
    "firefox133",
    "safari184",
    "safari180",
    "safari172_ios",
    "safari155",
    "edge101",
    "edge99",
]

BROWSER_HEADERS = [
    {
        "sec_ch_ua": '"Chromium";v="146", "Google Chrome";v="146", "Not-A.Brand";v="99"',
        "sec_ch_ua_mobile": "?0",
        "sec_ch_ua_platform": '"Windows"',
    },
    {
        "sec_ch_ua": '"Chromium";v="136", "Google Chrome";v="136", "Not-A.Brand";v="99"',
        "sec_ch_ua_mobile": "?0",
        "sec_ch_ua_platform": '"macOS"',
    },
    {
        "sec_ch_ua": '"Chromium";v="131", "Google Chrome";v="131", "Not-A.Brand";v="99"',
        "sec_ch_ua_mobile": "?0",
        "sec_ch_ua_platform": '"Linux"',
    },
    {
        "sec_ch_ua": '"Chromium";v="131", "Google Chrome";v="131", "Not-A.Brand";v="99"',
        "sec_ch_ua_mobile": "?1",
        "sec_ch_ua_platform": '"Android"',
    },
]

SKIP_EXTENSIONS = {
    '.pdf', '.zip', '.tar', '.gz', '.rar', '.7z',
    '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp', '.ico',
    '.mp3', '.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm',
    '.css', '.js', '.woff', '.woff2', '.ttf', '.eot',
    '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
    '.exe', '.dmg', '.apk', '.deb', '.rpm',
}

XENFORO_JUNK_PATTERNS = [
    r'/members/.*\.\d+/',
    r'/members/\?',
    r'/search/',
    r'/account/',
    r'/login/',
    r'/register/',
    r'/lost-password/',
    r'/misc/',
    r'/help/',
    r'/whats-new/',
    r'/watched/',
    r'/conversations/',
    r'/alerts/',
    r'/find-threads/',
    r'/cdn-cgi/',
    r'[?&]order=',
    r'[?&]direction=',
    r'[?&]page=\d+',
    r'[?&]t=\d+',
    r'[?&]reply_id=',
    r'[?&]_xfToken=',
    r'[?&]_xfResponseType=',
    r'[?&]_xfRequestUri=',
    r'[?&]do=',
    r'/goto/',
    r'/link-forums/',
    r'[?&]prefix_id=',
    r'\.atom$',
    r'/feed$',
    r'/index\.rss',
]

COMMON_JUNK_PARAMS = {
    'utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content',
    'fbclid', 'gclid', 'gclsrc', 'dclid', 'zanpid',
    'ref', 'referer', 'referrer', 'source',
    'sessionid', 'session_id', 'sid', 'phpsessid', 'jsessionid',
    '_ga', '_gl', '_gac', 'mc_cid', 'mc_eid',
    'fb_action_ids', 'fb_action_types', 'fb_source', 'fb_ref',
    'action_object_map', 'action_type_map', 'action_ref_map',
    'gs_l', 'ved', 'ei', 'usg',
    '_hsenc', '_hsmi', 'hsa_cam', 'hsa_grp', 'hsa_mt', 'hsa_src',
    'hsa_ad', 'hsa_acc', 'hsa_net', 'hsa_ver', 'hsa_la', 'hsa_ol',
    'hsa_kw', 'hsa_tgt',
    'trk', 'trkCampaign', 'sc_campaign', 'sc_channel', 'sc_content',
    'sc_medium', 'sc_outcome', 'sc_geo', 'sc_country',
    '_xfToken', '_xfResponseType', '_xfRequestUri', '_xfWithData',
    '_xfRedirect', '_xfNoRedirect',
}


class MapifyCrawler:
    def __init__(self, base_url, max_depth=3, delay=1.0, include_images=True,
                 ui=None, log_level=logging.INFO, config_file=None,
                 strip_queries=True, respect_canonical=True, max_pages=1000,
                 skip_xenforo_junk=True, allowed_params=None, stealth_mode=True,
                 proxy=None, proxy_list=None):
        self.base_url = self.normalize_url(base_url)
        self.max_depth = max_depth
        self.delay = delay
        self.include_images = include_images
        self.ui = ui
        self.visited = set()
        self.canonical_map = {}
        self.strip_queries = strip_queries
        self.respect_canonical = respect_canonical
        self.skip_xenforo_junk = skip_xenforo_junk
        self.stealth_mode = stealth_mode
        self.proxy = proxy
        self.proxy_list = proxy_list if proxy_list else []
        self._proxy_index = 0
        self.allowed_params = set(allowed_params) if allowed_params else set()
        self.sitemap = {
            'pages': [],
            'images': [],
            'internal_links': 0,
            'external_links': 0,
            'crawl_date': datetime.now().isoformat(),
            'skipped_urls': 0,
            'duplicate_urls': 0,
        }
        self.robots_parser = None
        self.request_timeout = 10
        self._use_http3 = False

        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(log_level)

        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

        self.session = self._create_session()

        self.config = self._load_config(config_file) if config_file and CONFIG_AVAILABLE else {}

        if self.config:
            crawler_config = self.config.get('crawler', {})
            self.max_depth = crawler_config.get('max_depth', max_depth)
            self.delay = crawler_config.get('delay', delay)
            self.include_images = crawler_config.get('include_images', include_images)
            self.max_workers = crawler_config.get('max_workers', min(4, os.cpu_count() or 1))
            self.memory_limit = crawler_config.get('max_pages', max_pages)
            self.request_timeout = crawler_config.get('timeout', 10)
            self.strip_queries = crawler_config.get('strip_queries', strip_queries)
            self.skip_xenforo_junk = crawler_config.get('skip_xenforo_junk', skip_xenforo_junk)
            self.stealth_mode = crawler_config.get('stealth_mode', stealth_mode)
            self.proxy = crawler_config.get('proxy', proxy)

            if 'user_agent' in self.config:
                if hasattr(self.session, 'headers'):
                    self.session.headers['User-Agent'] = self.config['user_agent']
        else:
            self.max_workers = min(4, os.cpu_count() or 1)
            self.memory_limit = max_pages

        self._xenforo_compiled = [re.compile(p) for p in XENFORO_JUNK_PATTERNS]
        self._lock = threading.Lock()

    def _get_next_proxy(self):
        """Get next proxy from the rotating list, or fall back to single proxy."""
        if self.proxy_list:
            proxy = self.proxy_list[self._proxy_index % len(self.proxy_list)]
            self._proxy_index += 1
            return proxy
        return self.proxy

    def _create_session(self):
        current_proxy = self._get_next_proxy()
        if CURL_CFFI_AVAILABLE and self.stealth_mode:
            target = random.choice(IMPERSONATE_TARGETS)
            self._last_impersonate = target
            self.logger.info(f"HTTP/3 stealth mode: impersonating {target}" + (f" via {current_proxy}" if current_proxy else ""))
            session = curl_requests.Session(
                impersonate=target,
                timeout=self.request_timeout,
                verify=False,
                proxies={"https": current_proxy, "http": current_proxy} if current_proxy else None,
            )
            session.headers.update({
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                "Accept-Language": "en-US,en;q=0.9",
                "Accept-Encoding": "gzip, deflate, br, zstd",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-User": "?1",
                "Sec-GPC": "1",
                "Upgrade-Insecure-Requests": "1",
                "Cache-Control": "max-age=0",
                "DNT": "1",
            })
            return session
        elif REQUESTS_AVAILABLE:
            session = requests.Session()
            if current_proxy:
                session.proxies = {"http": current_proxy, "https": current_proxy}
            session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
                "Accept-Encoding": "gzip, deflate, br, zstd",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "none",
                "Sec-Fetch-User": "?1",
                "Sec-GPC": "1",
                "Upgrade-Insecure-Requests": "1",
                "Cache-Control": "max-age=0",
                "DNT": "1",
            })
            return session
        else:
            raise RuntimeError("No HTTP library available. Install curl_cffi or requests.")

    def _rotate_impersonation(self):
        if not CURL_CFFI_AVAILABLE or not self.stealth_mode:
            return
        target = random.choice(IMPERSONATE_TARGETS)
        while target == self._last_impersonate:
            target = random.choice(IMPERSONATE_TARGETS)
        self._last_impersonate = target
        try:
            self.session.impersonate = target
        except Exception:
            fp = random.choice(BROWSER_HEADERS)
            for k in ("sec-ch-ua", "sec-ch-ua-mobile", "sec-ch-ua-platform"):
                if k in fp:
                    self.session.headers[k] = fp[k]

    def _safe_get(self, url, **kwargs):
        kwargs.setdefault('timeout', self.request_timeout)
        self._rotate_impersonation()
        try:
            resp = self.session.get(url, **kwargs)
            if CURL_CFFI_AVAILABLE and hasattr(resp, 'http_version'):
                if str(resp.http_version) == "3" and not self._use_http3:
                    self._use_http3 = True
                    self.logger.info(f"HTTP/3 negotiated with {urlparse(url).netloc}")
            return resp
        except Exception:
            if CURL_CFFI_AVAILABLE and self.stealth_mode:
                new_target = random.choice(IMPERSONATE_TARGETS)
                new_proxy = self._get_next_proxy()
                self.session.close()
                self.session = curl_requests.Session(
                    impersonate=new_target,
                    timeout=self.request_timeout,
                    verify=False,
                    proxies={"https": new_proxy, "http": new_proxy} if new_proxy else None,
                )
                self._last_impersonate = new_target
                return self.session.get(url, **kwargs)
            raise

    def _load_config(self, config_file):
        if not CONFIG_AVAILABLE:
            self.logger.warning("PyYAML not available, cannot load config file")
            return {}

        try:
            import yaml
            with open(config_file, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            self.logger.warning(f"Could not load config file {config_file}: {e}")
            return {}

    def normalize_url(self, url):
        if not url:
            raise ValueError("URL cannot be empty")

        parsed = urlparse(url)
        if not parsed.scheme:
            url = 'https://' + url
            parsed = urlparse(url)

        if not parsed.netloc:
            raise ValueError(f"Invalid URL format: {url}")

        return url.rstrip('/')

    def canonicalize_url(self, url):
        parsed = urlparse(url)

        path = parsed.path.rstrip('/') or '/'
        path = re.sub(r'/+', '/', path)

        fragment = ''

        if self.strip_queries:
            if parsed.query:
                params = parse_qs(parsed.query, keep_blank_values=False)
                filtered = {}
                for key, values in sorted(params.items()):
                    if key.lower() not in COMMON_JUNK_PARAMS and (
                        not self.allowed_params or key.lower() in self.allowed_params
                    ):
                        filtered[key] = values[0] if len(values) == 1 else values
                query = urlencode(filtered, doseq=True) if filtered else ''
            else:
                query = ''
        else:
            query = parsed.query

        canonical = urlunparse((
            parsed.scheme.lower(),
            parsed.netloc.lower(),
            path,
            parsed.params,
            query,
            fragment,
        ))

        return canonical

    def is_junk_url(self, url):
        parsed = urlparse(url)
        path_lower = parsed.path.lower()

        ext = os.path.splitext(path_lower)[1]
        if ext in SKIP_EXTENSIONS:
            return True

        if self.skip_xenforo_junk:
            full = url
            for pattern in self._xenforo_compiled:
                if pattern.search(full):
                    return True

        if parsed.query:
            params = parse_qs(parsed.query)
            junk_count = sum(1 for k in params if k.lower() in COMMON_JUNK_PARAMS)
            if junk_count == len(params) and junk_count > 0:
                return True

        return False

    def parse_robots_txt(self):
        try:
            robots_url = urljoin(self.base_url, '/robots.txt')
            self.logger.info(f"Fetching robots.txt from {robots_url}")
            response = self._safe_get(robots_url)

            if response.status_code == 200:
                self.logger.info("Successfully retrieved robots.txt")
                self.robots_parser = RobotFileParser()
                self.robots_parser.set_url(robots_url)
                self.robots_parser.parse(response.text.splitlines())

                disallowed = []
                for line in response.text.splitlines():
                    if line.strip().lower().startswith('disallow:'):
                        path = line.strip().split(':', 1)[1].strip()
                        if path:
                            disallowed.append(path)

                crawl_delay = None
                for line in response.text.splitlines():
                    if line.strip().lower().startswith('crawl-delay:'):
                        try:
                            crawl_delay = float(line.strip().split(':', 1)[1].strip())
                        except ValueError:
                            pass
                        break

                self.logger.info(f"Found {len(disallowed)} disallowed paths")
                if crawl_delay:
                    self.logger.info(f"Robots.txt crawl-delay: {crawl_delay}s")

                if self.ui:
                    self.ui.show_robots_info(
                        allowed=0,
                        disallowed=len(disallowed),
                        crawl_delay=crawl_delay
                    )

                if crawl_delay and crawl_delay > self.delay:
                    self.delay = crawl_delay
                    self.logger.info(f"Updated delay to {self.delay}s based on robots.txt")
            else:
                self.logger.warning(f"robots.txt not found (status: {response.status_code})")

        except Exception as e:
            self.logger.error(f"Error parsing robots.txt: {e}")
            if self.ui and self.ui.verbose:
                self.ui.console.print(f"[yellow]Could not parse robots.txt: {e}[/yellow]")

    def is_allowed(self, url):
        if not self.robots_parser:
            return True
        return self.robots_parser.can_fetch('*', url)

    def _should_crawl(self, url):
        canonical = self.canonicalize_url(url)

        if canonical in self.visited:
            self.sitemap['duplicate_urls'] += 1
            return False, canonical

        if self.is_junk_url(url):
            self.sitemap['skipped_urls'] += 1
            return False, canonical

        if not self.is_allowed(url):
            self.logger.info(f"Skipped (robots.txt): {url}")
            return False, canonical

        if len(self.visited) >= self.memory_limit:
            self.logger.warning(f"Reached page limit ({self.memory_limit})")
            return False, canonical

        return True, canonical

    def get_page_info(self, url):
        try:
            if not url.startswith(('http://', 'https://')):
                if self.ui and self.ui.verbose:
                    self.ui.console.print(f"[red]Invalid URL scheme: {url}[/red]")
                return None

            response = self._safe_get(url)
            response.raise_for_status()

            content_type = response.headers.get('content-type', '').lower()
            if not content_type.startswith('text/html'):
                if self.ui and self.ui.verbose:
                    self.ui.console.print(f"[yellow]Skipping non-HTML content: {url} ({content_type})[/yellow]")
                return None

            soup = BeautifulSoup(response.text, 'html.parser')

            canonical_tag = soup.find('link', rel='canonical')
            canonical_url = None
            if canonical_tag and canonical_tag.get('href') and self.respect_canonical:
                canonical_href = urljoin(url, str(canonical_tag['href']))
                if canonical_href != url and canonical_href.startswith(self.base_url):
                    page_canon = self.canonicalize_url(url)
                    if self.canonicalize_url(canonical_href) != page_canon:
                        canonical_url = canonical_href

            title = soup.find('title')
            title_text = title.get_text().strip() if title else ''

            meta_desc = soup.find('meta', attrs={'name': 'description'})
            meta_desc_content = meta_desc.get('content') if meta_desc else ''
            meta_desc_text = str(meta_desc_content).strip() if meta_desc_content else ''

            meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
            meta_keywords_content = meta_keywords.get('content') if meta_keywords else ''
            meta_keywords_text = str(meta_keywords_content).strip() if meta_keywords_content else ''

            h1_tags = [h.get_text().strip() for h in soup.find_all('h1')]
            h2_tags = [h.get_text().strip() for h in soup.find_all('h2')]

            links = []
            for a_tag in soup.find_all('a', href=True):
                href = a_tag['href']
                if href:
                    absolute_url = urljoin(url, str(href))
                    if absolute_url.startswith(('http://', 'https://')):
                        rel_attr = a_tag.get('rel') or []
                        links.append({
                            'url': absolute_url,
                            'text': a_tag.get_text().strip(),
                            'internal': absolute_url.startswith(self.base_url),
                            'nofollow': 'nofollow' in rel_attr
                        })

            images = []
            if self.include_images:
                for img_tag in soup.find_all('img'):
                    src = img_tag.get('src')
                    if src:
                        img_url = urljoin(url, str(src))
                        images.append({
                            'src': img_url,
                            'alt': img_tag.get('alt', ''),
                            'title': img_tag.get('title', ''),
                            'width': img_tag.get('width', ''),
                            'height': img_tag.get('height', '')
                        })

            return {
                'url': url,
                'canonical_url': canonical_url,
                'title': title_text,
                'meta_description': meta_desc_text,
                'meta_keywords': meta_keywords_text,
                'h1_tags': h1_tags,
                'h2_tags': h2_tags,
                'status_code': response.status_code,
                'content_length': len(response.content),
                'content_type': response.headers.get('content-type', ''),
                'last_modified': response.headers.get('last-modified', ''),
                'links': links,
                'images': images,
                'crawl_date': datetime.now().isoformat()
            }

        except Exception as e:
            if self.ui and self.ui.verbose:
                self.ui.console.print(f"[red]Error crawling {url}: {e}[/red]")
            return None

    def crawl_page(self, url, depth=0, task_id=None, progress=None):
        should_crawl, canonical = self._should_crawl(url)
        if depth > self.max_depth or not should_crawl:
            return

        with self._lock:
            if canonical in self.visited:
                return
            self.visited.add(canonical)

        self.logger.info(f"Crawling (depth {depth}): {url}")
        jitter = random.uniform(0.1, self.delay * 0.5)
        time.sleep(self.delay + jitter)

        if progress and task_id is not None:
            try:
                progress.update(task_id, description=f"[green]Crawling:[/] {url[:60]}...", advance=1)
            except Exception:
                pass

        page_info = self.get_page_info(url)
        if page_info:
            if page_info.get('canonical_url'):
                canon = self.canonicalize_url(page_info['canonical_url'])
                page_canon = self.canonicalize_url(url)
                if canon != page_canon and canon in self.visited:
                    self.sitemap['duplicate_urls'] += 1
                    return

            with self._lock:
                self.sitemap['pages'].append(page_info)
                self.sitemap['images'].extend(page_info['images'])

                internal_count = sum(1 for link in page_info['links'] if link['internal'])
                external_count = sum(1 for link in page_info['links'] if not link['internal'])
                self.sitemap['internal_links'] += internal_count
                self.sitemap['external_links'] += external_count

            self.logger.debug(f"Found {len(page_info['images'])} images, {len(page_info['links'])} links")

            if self.ui:
                self.ui.show_page_info(
                    url,
                    page_info['title'],
                    len(page_info['images']),
                    len(page_info['links'])
                )

            if depth < self.max_depth:
                internal_links = []
                for link in page_info['links']:
                    if link['internal']:
                        link_canonical = self.canonicalize_url(link['url'])
                        if link_canonical not in self.visited and not self.is_junk_url(link['url']):
                            internal_links.append(link['url'])

                self.logger.info(f"Found {len(internal_links)} new internal links to crawl")
                for link in internal_links:
                    if len(self.visited) >= self.memory_limit:
                        break
                    self.crawl_page(link, depth + 1, task_id, progress)
        else:
            self.logger.warning(f"Failed to get page info for: {url}")

    def crawl(self):
        if self.ui:
            self.ui.show_start_message(self.base_url)
        self.parse_robots_txt()

        if self.ui:
            progress = self.ui.progress
            task_id = self.ui.show_progress(self.memory_limit)
            self.crawl_page(self.base_url, 0, task_id, progress)
        else:
            self.crawl_page(self.base_url, 0)

        if self.ui:
            self.ui.show_summary_table(self.sitemap)
            self.ui.show_page_tree(self.sitemap)
            self.ui.show_seo_analysis(self.sitemap)

        return self.sitemap

    def generate_xml_sitemap(self, sitemap_data, output_dir):
        os.makedirs(output_dir, exist_ok=True)

        urlset = ET.Element('urlset', xmlns='http://www.sitemaps.org/schemas/sitemap/0.9')

        for page in sitemap_data['pages']:
            url_elem = ET.SubElement(urlset, 'url')

            loc = ET.SubElement(url_elem, 'loc')
            loc.text = page['url']

            if page.get('last_modified'):
                lastmod = ET.SubElement(url_elem, 'lastmod')
                lastmod.text = page['last_modified']
            else:
                lastmod = ET.SubElement(url_elem, 'lastmod')
                lastmod.text = datetime.now().strftime('%Y-%m-%d')

            changefreq = ET.SubElement(url_elem, 'changefreq')
            changefreq.text = 'weekly'

            priority = ET.SubElement(url_elem, 'priority')
            priority.text = '0.8'

        image_urlset = None
        if sitemap_data['images']:
            image_urlset = ET.Element('urlset')
            image_urlset.set('xmlns', 'http://www.sitemaps.org/schemas/sitemap/0.9')
            image_urlset.set('xmlns:image', 'http://www.google.com/schemas/sitemap-image/1.1')

            for image in sitemap_data['images'][:1000]:
                url_elem = ET.SubElement(image_urlset, 'url')

                loc = ET.SubElement(url_elem, 'loc')
                loc.text = image['src']

                image_elem = ET.SubElement(url_elem, 'image:image')
                image_loc = ET.SubElement(image_elem, 'image:loc')
                image_loc.text = image['src']

                if image.get('alt'):
                    image_caption = ET.SubElement(image_elem, 'image:caption')
                    image_caption.text = image['alt']

        tree = ET.ElementTree(urlset)
        ET.indent(tree, space="  ", level=0)
        tree.write(f"{output_dir}/sitemap.xml", encoding='utf-8', xml_declaration=True)

        if sitemap_data['images'] and image_urlset is not None:
            image_tree = ET.ElementTree(image_urlset)
            ET.indent(image_tree, space="  ", level=0)
            image_tree.write(f"{output_dir}/sitemap-images.xml", encoding='utf-8', xml_declaration=True)

        import json
        json_file = f"{output_dir}/sitemap.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(sitemap_data, f, indent=2, ensure_ascii=False)

        if len(sitemap_data['images']) > 1000:
            self.logger.info("Clearing large image dataset from memory to optimize performance")
            self.sitemap['images'] = self.sitemap['images'][:1000]

        return {
            'sitemap_xml': f"{output_dir}/sitemap.xml",
            'sitemap_images': f"{output_dir}/sitemap-images.xml" if sitemap_data['images'] else None,
            'sitemap_json': f"{output_dir}/sitemap.json"
        }

    def save_sitemap(self, sitemap_data, output_dir):
        return self.generate_xml_sitemap(sitemap_data, output_dir)
