#!/usr/bin/env python3
"""
Mapify UI Components - Beautiful Colorful Interface
Developed By Hayder
"""

import time
from rich.console import Console
from rich.progress import (
    Progress, BarColumn, TextColumn, TimeRemainingColumn,
    SpinnerColumn, MofNCompleteColumn, TransferSpeedColumn
)
from rich.table import Table
from rich.tree import Tree
from rich.panel import Panel
from rich.text import Text
from rich.columns import Columns
from rich.layout import Layout
from rich.align import Align
from rich import box


DEVELOPER = "Hayder"
COMPANY = "Qamrix Tech"
VERSION = "2.0.0"


def show_developer_banner(console):
    console.print()
    dev_text = Text()
    dev_text.append("  Made by ", style="dim white")
    dev_text.append(DEVELOPER, style="bold magenta")
    dev_text.append("  |  ", style="dim white")
    dev_text.append(COMPANY, style="bold cyan")
    dev_text.append("  |  ", style="dim white")
    dev_text.append(f"v{VERSION}", style="dim yellow")
    console.print(Align.center(dev_text))
    console.print()


def build_gradient_panel(content, title="", border_style="cyan", width=None):
    return Panel(
        content,
        title=f"[bold white]{title}[/bold white]" if title else None,
        border_style=border_style,
        box=box.ROUNDED,
        width=width,
        padding=(1, 2),
    )


class MapifyUI:
    def __init__(self, verbose=False, proxy=None):
        self.console = Console()
        self.verbose = verbose
        self.progress = None
        self.proxy = proxy
        self.start_time = time.time()

    def show_start_message(self, url):
        self.start_time = time.time()
        self.console.print()
        self.console.print(Panel(
            f"[bold white]Target:[/]       [bright_cyan]{url}[/bright_cyan]\n"
            f"[bold white]Stealth:[/]      [bright_green]HTTP/3 + TLS Impersonation[/bright_green]\n"
            f"[bold white]Protocol:[/]     [bright_yellow]QUIC / h3[/bright_yellow]\n"
            f"[bold white]Proxy:[/]        [bright_magenta]{self.proxy or 'Direct Connection'}[/bright_magenta]\n"
            f"[bold white]Started:[/]      [bright_white]{time.strftime('%H:%M:%S')}[/bright_white]",
            title="[bold cyan]CRAWL INITIATED[/bold cyan]",
            border_style="bright_cyan",
            box=box.DOUBLE_EDGE,
        ))
        self.console.print()

    def show_progress(self, total_pages):
        self.progress = Progress(
            SpinnerColumn("dots", style="bold bright_cyan"),
            TextColumn("[bold bright_white]{task.description}[/bold bright_white]"),
            BarColumn(
                bar_width=45,
                complete_style="bright_green",
                finished_style="bold bright_green",
                pulse_style="bright_cyan",
            ),
            MofNCompleteColumn(),
            TextColumn("[bright_yellow]pages[/bright_yellow]"),
            TimeRemainingColumn(),
            console=self.console,
            transient=False,
        )
        return self.progress.add_task(
            "[bright_green]Crawling...",
            total=total_pages,
        )

    def update_progress(self, task_id, url):
        if self.progress:
            short_url = url[:55] + "..." if len(url) > 55 else url
            self.progress.update(
                task_id,
                description=f"[bright_green]{short_url}[/bright_green]",
            )

    def show_page_info(self, url, title, images_count, links_count):
        if self.verbose:
            self.console.print(
                f"  [bright_cyan]>[/bright_cyan] [bright_white]{title[:45]}[/bright_white]"
                f"  [dim white]({images_count} imgs, {links_count} links)[/dim white]"
            )

    def show_robots_info(self, allowed, disallowed, crawl_delay):
        table = Table(
            title="[bold bright_white]robots.txt Analysis[/bold bright_white]",
            box=box.ROUNDED,
            border_style="bright_cyan",
            title_style="bold bright_cyan",
            show_header=True,
            header_style="bold bright_white on dark_blue",
        )
        table.add_column("Property", style="bright_cyan", min_width=20)
        table.add_column("Value", style="bright_green", min_width=15)

        table.add_row("Allowed Paths", f"[bright_green]{allowed}[/bright_green]")
        table.add_row("Disallowed Paths", f"[bright_red]{disallowed}[/bright_red]")
        table.add_row(
            "Crawl Delay",
            f"[bright_yellow]{crawl_delay}s[/bright_yellow]" if crawl_delay else "[dim]Not specified[/dim]",
        )
        self.console.print(table)

    def show_summary_table(self, sitemap):
        elapsed = time.time() - self.start_time
        mins, secs = divmod(int(elapsed), 60)

        table = Table(
            title="[bold bright_white]Crawl Summary[/bold bright_white]",
            box=box.DOUBLE_EDGE,
            border_style="bright_green",
            title_style="bold bright_green",
            show_header=True,
            header_style="bold bright_white on dark_green",
            padding=(0, 2),
        )
        table.add_column("Metric", style="bright_cyan", min_width=25)
        table.add_column("Count", style="bright_green", min_width=15, justify="right")

        pages = len(sitemap.get('pages', []))
        images = len(sitemap.get('images', []))
        internal = sitemap.get('internal_links', 0)
        external = sitemap.get('external_links', 0)
        dupes = sitemap.get('duplicate_urls', 0)
        junk = sitemap.get('skipped_urls', 0)

        table.add_row("[bold bright_white]Total Pages Crawled[/bold bright_white]", f"[bold bright_green]{pages}[/bold bright_green]")
        table.add_row("[bright_white]Images Found[/bright_white]", f"[bright_green]{images}[/bright_green]")
        table.add_row("[bright_white]Internal Links[/bright_white]", f"[bright_cyan]{internal}[/bright_cyan]")
        table.add_row("[bright_white]External Links[/bright_white]", f"[bright_yellow]{external}[/bright_yellow]")
        table.add_row("[bright_white]Duplicate URLs Skipped[/bright_white]", f"[bright_red]{dupes}[/bright_red]")
        table.add_row("[bright_white]Junk URLs Skipped[/bright_white]", f"[bright_red]{junk}[/bright_red]")
        table.add_row("[bright_white]Crawl Duration[/bright_white]", f"[bright_magenta]{mins}m {secs}s[/bright_magenta]")
        if pages > 0:
            avg_time = elapsed / pages
            table.add_row("[bright_white]Avg Time per Page[/bright_white]", f"[bright_yellow]{avg_time:.2f}s[/bright_yellow]")

        self.console.print()
        self.console.print(table)

    def show_page_tree(self, sitemap):
        tree = Tree(
            "[bold bright_white]Site Structure[/bold bright_white]",
            guide_style="bright_cyan",
        )

        pages = sitemap.get('pages', [])
        shown = min(len(pages), 15)
        for i, page in enumerate(pages[:shown]):
            url_short = page['url']
            if len(url_short) > 70:
                url_short = url_short[:67] + "..."
            branch = tree.add(f"[bright_cyan]{url_short}[/bright_cyan]")
            if page.get('images'):
                branch.add(f"[bright_yellow]{len(page['images'])} images[/bright_yellow]")
            if page.get('links'):
                branch.add(f"[bright_green]{len(page['links'])} links[/bright_green]")

        if len(pages) > shown:
            tree.add(f"[dim]... and {len(pages) - shown} more pages[/dim]")

        self.console.print()
        self.console.print(tree)

    def show_seo_analysis(self, sitemap):
        pages = sitemap.get('pages', [])
        if not pages:
            return

        sections = []

        titles = [p.get('title', '') for p in pages if p.get('title')]
        if titles:
            avg_len = sum(len(t) for t in titles) / len(titles)
            short = len([t for t in titles if len(t) < 30])
            long = len([t for t in titles if len(t) > 60])
            sections.append(
                f"[bold bright_yellow]TITLES[/bold bright_yellow]\n"
                f"  [bright_white]Average length:[/bright_white]  [bright_cyan]{avg_len:.0f} chars[/bright_cyan]\n"
                f"  [bright_white]Short (<30):[/bright_white]     [bright_green]{short}[/bright_green]\n"
                f"  [bright_white]Long (>60):[/bright_white]      [bright_red]{long}[/bright_red]"
            )

        meta_descs = [p.get('meta_description', '') for p in pages if p.get('meta_description')]
        if meta_descs:
            avg_desc = sum(len(d) for d in meta_descs) / len(meta_descs)
            missing = len(pages) - len(meta_descs)
            sections.append(
                f"[bold bright_yellow]META DESCRIPTIONS[/bold bright_yellow]\n"
                f"  [bright_white]Average length:[/bright_white]  [bright_cyan]{avg_desc:.0f} chars[/bright_cyan]\n"
                f"  [bright_white]Missing:[/bright_white]         [bright_red]{missing}[/bright_red]\n"
                f"  [bright_white]Found:[/bright_white]           [bright_green]{len(meta_descs)}[/bright_green]"
            )

        h1_all = []
        h2_all = []
        for page in pages:
            h1_all.extend(page.get('h1_tags', []))
            h2_all.extend(page.get('h2_tags', []))

        if h1_all:
            no_h1 = len([p for p in pages if not p.get('h1_tags')])
            multi_h1 = len([p for p in pages if len(p.get('h1_tags', [])) > 1])
            sections.append(
                f"[bold bright_yellow]HEADERS[/bold bright_yellow]\n"
                f"  [bright_white]H1 tags total:[/bright_white]   [bright_cyan]{len(h1_all)}[/bright_cyan]\n"
                f"  [bright_white]H2 tags total:[/bright_white]   [bright_cyan]{len(h2_all)}[/bright_cyan]\n"
                f"  [bright_white]Pages without H1:[/bright_white] [bright_red]{no_h1}[/bright_red]\n"
                f"  [bright_white]Multiple H1s:[/bright_white]     [bright_yellow]{multi_h1}[/bright_yellow]"
            )

        images = sitemap.get('images', [])
        if images:
            with_alt = len([i for i in images if i.get('alt')])
            pct = (with_alt / len(images)) * 100 if images else 0
            sections.append(
                f"[bold bright_yellow]IMAGES[/bold bright_yellow]\n"
                f"  [bright_white]Total:[/bright_white]            [bright_cyan]{len(images)}[/bright_cyan]\n"
                f"  [bright_white]With ALT:[/bright_white]         [bright_green]{pct:.0f}%[/bright_green] ({with_alt}/{len(images)})\n"
                f"  [bright_white]Without ALT:[/bright_white]      [bright_red]{len(images) - with_alt}[/bright_red]"
            )

        total_bytes = sum(p.get('content_length', 0) for p in pages)
        if total_bytes > 0:
            avg_bytes = total_bytes / len(pages)
            total_kb = total_bytes / 1024
            sections.append(
                f"[bold bright_yellow]CONTENT[/bold bright_yellow]\n"
                f"  [bright_white]Pages analyzed:[/bright_white]   [bright_cyan]{len(pages)}[/bright_cyan]\n"
                f"  [bright_white]Avg size:[/bright_white]         [bright_cyan]{avg_bytes/1024:.1f} KB[/bright_cyan]\n"
                f"  [bright_white]Total size:[/bright_white]       [bright_green]{total_kb:.1f} KB[/bright_green]"
            )

        internal = sitemap.get('internal_links', 0)
        external = sitemap.get('external_links', 0)
        if pages:
            sections.append(
                f"[bold bright_yellow]LINKS[/bold bright_yellow]\n"
                f"  [bright_white]Internal total:[/bright_white]   [bright_green]{internal}[/bright_green]\n"
                f"  [bright_white]External total:[/bright_white]   [bright_yellow]{external}[/bright_yellow]\n"
                f"  [bright_white]Avg per page:[/bright_white]     [bright_cyan]{(internal + external) / len(pages):.1f}[/bright_cyan]"
            )

        panel_content = "\n\n".join(sections)
        self.console.print()
        self.console.print(Panel(
            panel_content,
            title="[bold bright_white]SEO Analysis[/bold bright_white]",
            border_style="bright_yellow",
            box=box.ROUNDED,
            padding=(1, 2),
        ))

    def show_crawl_complete(self, sitemap, output_dir):
        elapsed = time.time() - self.start_time
        mins, secs = divmod(int(elapsed), 60)
        pages = len(sitemap.get('pages', []))

        self.console.print()
        self.console.print(Panel(
            f"[bold bright_green]Crawl Complete![/bold bright_green]\n\n"
            f"  [bright_white]Pages:[/bright_white]       [bright_cyan]{pages}[/bright_cyan]\n"
            f"  [bright_white]Images:[/bright_white]      [bright_cyan]{len(sitemap.get('images', []))}[/bright_cyan]\n"
            f"  [bright_white]Duration:[/bright_white]    [bright_yellow]{mins}m {secs}s[/bright_yellow]\n"
            f"  [bright_white]Output:[/bright_white]      [bright_green]{output_dir}/[/bright_green]\n"
            f"  [bright_white]Files:[/bright_white]       [bright_magenta]sitemap.xml, sitemap.json[/bright_magenta]",
            title="[bold bright_white]MAPIFY COMPLETE[/bold bright_white]",
            border_style="bright_green",
            box=box.DOUBLE_EDGE,
            padding=(1, 2),
        ))
        self.console.print()
        dev_text = Text()
        dev_text.append("  Made with ", style="dim white")
        dev_text.append("<3", style="bold red")
        dev_text.append(" by ", style="dim white")
        dev_text.append(DEVELOPER, style="bold magenta")
        dev_text.append("  |  ", style="dim white")
        dev_text.append(COMPANY, style="bold cyan")
        self.console.print(Align.center(dev_text))
        self.console.print()
