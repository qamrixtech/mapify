#!/usr/bin/env python3
"""
Mapify CLI Interface - Beautiful Interactive TUI
Developed By Hayder
"""

import sys
import re
import os
from urllib.parse import urlparse

try:
    import click
    from rich.console import Console
    from rich.panel import Panel
    from rich.text import Text
    from rich.table import Table
    from rich import box
    from rich.align import Align
    import pyfiglet
    from simple_term_menu import TerminalMenu
    from src.crawler import MapifyCrawler
    from src.ui import MapifyUI, DEVELOPER, COMPANY, VERSION
except ImportError as e:
    print(f"Missing dependency: {e}")
    print("Install with: pip install -r requirements.txt")
    sys.exit(1)

console = Console()


def strip_rich(text):
    """Strip Rich markup tags from text for TerminalMenu compatibility."""
    return re.sub(r'\[/?[^\]]+\]', '', text)


def show_banner():
    try:
        banner = pyfiglet.figlet_format("Mapify", font="slant")
    except Exception:
        banner = "  M A P I F Y  "

    colors = ["bright_cyan", "bright_green", "bright_magenta", "bright_yellow"]
    color = colors[hash(banner) % len(colors)]

    console.print()
    console.print(Align.center(Text(banner, style=f"bold {color}")))

    subtitle = Text()
    subtitle.append("  SEO Sitemap Generator", style="bright_white")
    subtitle.append("  |  HTTP/3 Stealth", style="dim cyan")
    subtitle.append("  |  TLS Impersonation", style="dim green")
    console.print(Align.center(subtitle))

    ver = Text()
    ver.append(f"  v{VERSION}", style="dim yellow")
    ver.append("  |  ", style="dim white")
    ver.append(f"By {DEVELOPER}", style="bold magenta")
    ver.append("  |  ", style="dim white")
    ver.append(COMPANY, style="bold cyan")
    console.print(Align.center(ver))
    console.print()


def prompt_url():
    console.print("[bold bright_cyan]>[/bold bright_cyan] [bold bright_white]Enter target URL:[/bold bright_white]")
    url = input("  ").strip()
    if not url:
        console.print("[bold bright_red]URL cannot be empty[/bold bright_red]")
        sys.exit(1)
    return validate_url(url)


def load_proxy_list(filepath):
    """Load proxies from a file, one per line. Supports comments and blank lines."""
    proxies = []
    try:
        with open(filepath, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    if not re.match(r'^https?://', line) and not line.startswith('socks5://'):
                        line = 'http://' + line
                    proxies.append(line)
    except FileNotFoundError:
        console.print(f"[bold bright_red]Proxy file not found: {filepath}[/bold bright_red]")
    return proxies


def prompt_proxy():
    options = [
        "No Proxy (direct connection)",
        "Single HTTP Proxy  (e.g. http://127.0.0.1:8080)",
        "Single HTTPS Proxy (e.g. https://127.0.0.1:8443)",
        "Single SOCKS5 Proxy (e.g. socks5://127.0.0.1:1080)",
        "Proxy List File    (e.g. proxy.txt)",
        "Custom (enter manually)",
    ]
    menu = TerminalMenu(
        options,
        title="Proxy Configuration",
    )
    idx = menu.show()
    if idx is None:
        return None, None

    if idx == 0:
        return None, None
    elif idx == 1:
        console.print("[bold bright_cyan]>[/bold bright_cyan] [bold bright_white]Enter HTTP proxy host:port:[/bold bright_white]")
        addr = input("  ").strip()
        return (f"http://{addr}" if addr else None), None
    elif idx == 2:
        console.print("[bold bright_cyan]>[/bold bright_cyan] [bold bright_white]Enter HTTPS proxy host:port:[/bold bright_white]")
        addr = input("  ").strip()
        return (f"https://{addr}" if addr else None), None
    elif idx == 3:
        console.print("[bold bright_cyan]>[/bold bright_cyan] [bold bright_white]Enter SOCKS5 proxy host:port:[/bold bright_white]")
        addr = input("  ").strip()
        return (f"socks5://{addr}" if addr else None), None
    elif idx == 4:
        console.print("[bold bright_cyan]>[/bold bright_cyan] [bold bright_white]Enter proxy list file path:[/bold bright_white]")
        filepath = input("  ").strip()
        if not filepath:
            return None, None
        proxies = load_proxy_list(filepath)
        if proxies:
            console.print(f"[bright_green]Loaded {len(proxies)} proxies from {filepath}[/bright_green]")
            return None, proxies
        return None, None
    else:
        console.print("[bold bright_cyan]>[/bold bright_cyan] [bold bright_white]Enter proxy URL (http/https/socks5://host:port):[/bold bright_white]")
        proxy = input("  ").strip()
        return proxy if proxy else None, None


def prompt_depth():
    options = [
        "1 - Shallow (homepage + direct links)",
        "2 - Medium",
        "3 - Standard (recommended)",
        "5 - Deep",
        "10 - Maximum",
    ]
    menu = TerminalMenu(options, title="Crawl Depth")
    idx = menu.show()
    if idx is None:
        sys.exit(0)
    return [1, 2, 3, 5, 10][idx]


def prompt_delay():
    options = [
        "0.3s - Aggressive",
        "0.5s - Fast",
        "1.0s - Standard (recommended)",
        "2.0s - Polite",
        "5.0s - Very polite",
    ]
    menu = TerminalMenu(options, title="Request Delay")
    idx = menu.show()
    if idx is None:
        sys.exit(0)
    return [0.3, 0.5, 1.0, 2.0, 5.0][idx]


def prompt_max_pages():
    options = [
        "100 pages",
        "500 pages",
        "1000 pages (recommended)",
        "5000 pages",
        "10000 pages",
        "Unlimited (careful!)",
    ]
    menu = TerminalMenu(options, title="Max Pages to Crawl")
    idx = menu.show()
    if idx is None:
        sys.exit(0)
    return [100, 500, 1000, 5000, 10000, 999999][idx]


def prompt_features():
    options = [
        "Include images in sitemap",
        "Strip query strings (recommended for forums)",
        "Skip XenForo / vBulletin / phpBB junk URLs",
        "Respect canonical tags",
        "Stealth mode: HTTP/3 + TLS impersonation",
        "Verbose output",
    ]
    menu = TerminalMenu(
        options,
        title="Toggle Features (Space to select, Enter to confirm)",
        multi_select=True,
        show_multi_select_hint=True,
        preselected_entries=[1, 2, 3, 4],
    )
    selected = menu.show()
    if selected is None:
        selected = ()
    if isinstance(selected, int):
        selected = (selected,)

    return {
        'images': 0 in selected,
        'strip_queries': 1 in selected,
        'skip_xenforo': 2 in selected,
        'respect_canonical': 3 in selected,
        'stealth_mode': 4 in selected,
        'verbose': 5 in selected,
    }


def prompt_output():
    default = "output"
    console.print(f"[bold bright_cyan]>[/bold bright_cyan] [bold bright_white]Output directory[/bold bright_white] [dim](default: {default})[/dim]:")
    path = input("  ").strip()
    return path if path else default


def validate_url(url):
    if not url:
        raise click.BadParameter("URL cannot be empty")
    if not re.match(r'^https?://', url):
        url = 'https://' + url
    parsed = urlparse(url)
    if not parsed.netloc:
        raise click.BadParameter(f"Invalid URL format: {url}")
    return url


def show_config_table(url, depth, delay, max_pages, features, output_dir, proxy, proxy_list):
    table = Table(
        title="[bold bright_white]Crawl Configuration[/bold bright_white]",
        box=box.DOUBLE_EDGE,
        border_style="bright_cyan",
        title_style="bold bright_cyan",
        show_header=False,
        padding=(0, 2),
    )
    table.add_column("Key", style="bright_cyan", min_width=18)
    table.add_column("Value", style="bright_green")

    table.add_row("[bold]Target[/bold]", f"[bright_white]{url}[/bright_white]")
    table.add_row("[bold]Depth[/bold]", f"[bright_yellow]{depth}[/bright_yellow]")
    table.add_row("[bold]Delay[/bold]", f"[bright_yellow]{delay}s[/bright_yellow]")
    table.add_row("[bold]Max Pages[/bold]", f"[bright_green]{max_pages:,}[/bright_green]")
    table.add_row("[bold]Images[/bold]", "[bright_green]Yes[/bright_green]" if features['images'] else "[dim]No[/dim]")
    table.add_row("[bold]Strip Queries[/bold]", "[bright_green]Yes[/bright_green]" if features['strip_queries'] else "[dim]No[/dim]")
    table.add_row("[bold]XenForo Filter[/bold]", "[bright_green]Yes[/bright_green]" if features['skip_xenforo'] else "[dim]No[/dim]")
    table.add_row("[bold]Canonical Tags[/bold]", "[bright_green]Yes[/bright_green]" if features['respect_canonical'] else "[dim]No[/dim]")
    table.add_row("[bold]Stealth Mode[/bold]", "[bright_magenta]HTTP/3 + TLS Impersonation[/bright_magenta]" if features['stealth_mode'] else "[dim]Disabled[/dim]")
    if proxy_list:
        table.add_row("[bold]Proxy[/bold]", f"[bright_magenta]Rotating ({len(proxy_list)} proxies)[/bright_magenta]")
    else:
        table.add_row("[bold]Proxy[/bold]", f"[bright_magenta]{proxy or 'Direct'}[/bright_magenta]")
    table.add_row("[bold]Verbose[/bold]", "[bright_green]Yes[/bright_green]" if features['verbose'] else "[dim]No[/dim]")
    table.add_row("[bold]Output[/bold]", f"[bright_green]{output_dir}/[/bright_green]")

    console.print()
    console.print(table)


def run_interactive():
    show_banner()

    main_options = [
        "Start New Crawl",
        "Quick Crawl (stealth defaults)",
        "Exit",
    ]
    menu = TerminalMenu(main_options, title="Main Menu")
    choice = menu.show()

    if choice is None or choice == 2:
        console.print()
        console.print(Align.center(Text("Goodbye!", style="dim bright_white")))
        console.print()
        return

    url = prompt_url()

    if choice == 1:
        depth = 3
        delay = 1.0
        max_pages = 1000
        features = {
            'images': False,
            'strip_queries': True,
            'skip_xenforo': True,
            'respect_canonical': True,
            'stealth_mode': True,
            'verbose': False,
        }
        proxy = None
        proxy_list = None
        output_dir = "output"
    else:
        depth = prompt_depth()
        delay = prompt_delay()
        max_pages = prompt_max_pages()
        features = prompt_features()
        proxy, proxy_list = prompt_proxy()
        output_dir = prompt_output()

    show_config_table(url, depth, delay, max_pages, features, output_dir, proxy, proxy_list)

    confirm_menu = TerminalMenu(
        ["Start Crawl", "Cancel"],
        title="Ready to crawl?",
    )
    if confirm_menu.show() != 0:
        console.print("[dim]Cancelled.[/dim]")
        return

    ui = MapifyUI(verbose=features['verbose'], proxy=proxy or (proxy_list[0] if proxy_list else None))

    crawler = MapifyCrawler(
        base_url=url,
        max_depth=depth,
        delay=delay,
        include_images=features['images'],
        ui=ui,
        strip_queries=features['strip_queries'],
        respect_canonical=features['respect_canonical'],
        max_pages=max_pages,
        skip_xenforo_junk=features['skip_xenforo'],
        stealth_mode=features['stealth_mode'],
        proxy=proxy,
        proxy_list=proxy_list,
    )

    try:
        sitemap = crawler.crawl()
        crawler.save_sitemap(sitemap, output_dir)
        ui.show_crawl_complete(sitemap, output_dir)

    except KeyboardInterrupt:
        console.print("\n[bright_yellow]Crawl interrupted by user.[/bright_yellow]")
        if crawler.sitemap['pages']:
            console.print(f"[bright_yellow]Saving {len(crawler.sitemap['pages'])} pages crawled so far...[/bright_yellow]")
            crawler.save_sitemap(crawler.sitemap, output_dir)
    except Exception as e:
        console.print(Panel(
            f"[bold bright_red]Error:[/] {str(e)}",
            title="[bold bright_red]FAILED[/bold bright_red]",
            border_style="bright_red",
            box=box.DOUBLE_EDGE,
        ))


@click.command()
@click.argument('url', required=False)
@click.option('--depth', default=None, type=click.IntRange(1, 10), help='Crawling depth (default: 3, max: 10)')
@click.option('--output', default='output', type=click.Path(), help='Output directory (default: output)')
@click.option('--delay', default=None, type=click.FloatRange(0.1, 10.0), help='Delay between requests (default: 1.0)')
@click.option('--max-pages', default=1000, type=int, help='Maximum pages to crawl (default: 1000)')
@click.option('--images', is_flag=True, help='Include images in sitemap')
@click.option('--verbose', is_flag=True, help='Verbose output')
@click.option('--strip-queries/--keep-queries', default=True, help='Strip tracking/junk query params')
@click.option('--skip-xenforo/--no-skip-xenforo', default=True, help='Skip XenForo/vBulletin/phpBB junk URLs')
@click.option('--stealth/--no-stealth', default=True, help='HTTP/3 + TLS impersonation (default: on)')
@click.option('--proxy', default=None, type=str, help='Single proxy (http/https/socks5://host:port)')
@click.option('--proxy-list', default=None, type=click.Path(exists=True), help='Proxy list file (one per line)')
@click.option('--config', type=click.Path(exists=True), help='Configuration file path')
@click.option('--interactive', '-i', is_flag=True, help='Launch interactive TUI mode')
def main(url, depth, output, delay, max_pages, images, verbose, strip_queries, skip_xenforo, stealth, proxy, proxy_list, config, interactive):
    """Mapify - SEO Sitemap Generator with HTTP/3 Stealth

    Developed By Hayder
    Generate SEO-rich sitemaps for any website. Run with -i for interactive mode.
    """

    if interactive or url is None:
        run_interactive()
        return

    try:
        url = validate_url(url)
    except click.BadParameter as e:
        console.print(f"[bold bright_red]{e}[/]")
        return

    show_banner()

    if depth is None:
        depth = 3
    if delay is None:
        delay = 1.0

    proxies = None
    if proxy_list:
        proxies = load_proxy_list(proxy_list)
        if proxies:
            console.print(f"[bright_green]Loaded {len(proxies)} proxies from {proxy_list}[/bright_green]")

    features = {
        'images': images,
        'strip_queries': strip_queries,
        'skip_xenforo': skip_xenforo,
        'respect_canonical': True,
        'stealth_mode': stealth,
        'verbose': verbose,
    }

    show_config_table(url, depth, delay, max_pages, features, output, proxy, proxies)

    ui = MapifyUI(verbose=verbose, proxy=proxy or (proxies[0] if proxies else None))

    crawler = MapifyCrawler(
        base_url=url,
        max_depth=depth,
        delay=delay,
        include_images=images,
        ui=ui,
        config_file=config,
        strip_queries=strip_queries,
        max_pages=max_pages,
        skip_xenforo_junk=skip_xenforo,
        stealth_mode=stealth,
        proxy=proxy,
        proxy_list=proxies,
    )

    try:
        sitemap = crawler.crawl()
        crawler.save_sitemap(sitemap, output)
        ui.show_crawl_complete(sitemap, output)

    except KeyboardInterrupt:
        console.print("\n[bright_yellow]Crawl interrupted by user.[/bright_yellow]")
        if crawler.sitemap['pages']:
            console.print(f"[bright_yellow]Saving {len(crawler.sitemap['pages'])} pages crawled so far...[/bright_yellow]")
            crawler.save_sitemap(crawler.sitemap, output)
    except Exception as e:
        console.print(Panel(
            f"[bold bright_red]Error:[/] {str(e)}",
            title="[bold bright_red]FAILED[/bold bright_red]",
            border_style="bright_red",
            box=box.DOUBLE_EDGE,
        ))


if __name__ == "__main__":
    main()
