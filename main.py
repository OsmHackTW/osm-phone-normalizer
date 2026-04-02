"""
OSMTW Phone Normalizer — main pipeline
Fetch phone-tagged entities for an area, then normalize all phone numbers.

Usage
-----
  python main.py --target TTT                  # fetch + normalize 臺東縣
  python main.py --target Hsinchu              # English name
  python main.py --preset greater_taipei       # Greater Taipei area set
  python main.py --target TPE --no-cache       # re-fetch even if cached
  python main.py --target TPE --dry-run        # show changes without writing
  
"""

import json
import logging
from pathlib import Path

from rich.console import Console
from rich.logging import RichHandler
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
)
from rich.table import Table
from rich.text import Text

from overpass import (
    OUTPUT_DIR,
    REQUEST_DELAY,
    Area,
    batch_fetch,
    resolve_area,
)
from overpass.presets import ALL_PRESETS, REGION_ALIASES, REGION_AREAS, REGION_DEFAULT_PRESET, REGION_PRESETS, REGIONS
from phonenumbers import PhoneNumberFormat
from phone_normalizer import apply_changes, process_node

_REGION_CITY_LOOKUP: dict[str, dict[str, Area]] = {
    region: {a.name: a for a in areas} for region, areas in REGION_AREAS.items()
}

console = Console()
log = logging.getLogger(__name__)

_CAT_KEYS = (
    "amenity",
    "office",
    "tourism",
    "shop",
    "leisure",
    "historic",
    "landuse",
    "building",
    "public_transport",
)


# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------


def normalize_results(
    results: dict[str, list[dict]],
    output_dir: Path,
    dry_run: bool = False,
    verbose: bool = False,
    fmt: int = PhoneNumberFormat.INTERNATIONAL,
    region: str = "TW",
) -> tuple[dict[str, int], list[tuple[dict, dict]]]:
    """
    Normalize phone tags on every element in results.
    Writes updated elements back to <area>.json (unless dry_run).
    Returns ({area_name: n_changed}, [(original_element, changes_dict)]).
    """
    summary: dict[str, int] = {}
    totals: dict[str, int] = {}
    diffs: list[tuple[dict, dict]] = []

    for area_name, elements in results.items():
        changed = 0
        updated_elements = []
        totals[area_name] = len(elements)

        for elem in elements:
            tags = elem.get("tags", {})
            changes = process_node(tags, fmt, region)
            if changes:
                diffs.append((elem, changes))
                updated_elem = {**elem, "tags": apply_changes(tags, changes)}
                changed += 1
                if verbose:
                    eid = f"{elem.get('type', '?')}/{elem.get('id', '?')}"
                    name = tags.get("name", "(unnamed)")
                    category = next(
                        (
                            tags[k] if tags[k] != "yes" else k
                            for k in _CAT_KEYS
                            if k in tags
                        ),
                        "(others)",
                    )
                    for tag, new_val in changes.items():
                        old_val = tags.get(tag, "(missing)")
                        if new_val is None:
                            console.print(
                                f"  [dim]{eid}[/dim]  [bold]{name}[/bold]  "
                                f"[blue]{category}[/blue]  "
                                f"[[yellow]{tag}[/yellow]] [red]deleted[/red] [dim](duplicate)[/dim]"
                            )
                        else:
                            console.print(
                                f"  [dim]{eid}[/dim]  [bold]{name}[/bold]  "
                                f"[blue]{category}[/blue]  "
                                f"[[yellow]{tag}[/yellow]]  "
                                f"[red]{old_val}[/red] [dim]→[/dim] [green]{new_val}[/green]"
                            )
                updated_elements.append(updated_elem)
            else:
                updated_elements.append(elem)

        summary[area_name] = changed

        if not dry_run and changed:
            out_file = output_dir / f"{area_name}.json"
            out_file.write_text(
                json.dumps(updated_elements, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )

    # Summary table
    table = Table(show_footer=True, title="Normalization Summary", title_style="bold")
    table.add_column("Region", style="cyan", footer=Text("Total", style="bold"))
    table.add_column("Fetched", justify="right", footer=str(sum(totals.values())))
    table.add_column(
        "Normalized",
        justify="right",
        footer=Text(str(sum(summary.values())), style="bold green"),
    )
    for area_name in summary:
        n_changed = summary[area_name]
        n_total = totals[area_name]
        normalized_cell = (
            Text(str(n_changed), style="bold green")
            if n_changed
            else Text("0", style="dim")
        )
        table.add_row(area_name, str(n_total), normalized_cell)
    console.print(table)

    return summary, diffs


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse

    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(console=console, rich_tracebacks=True, show_path=False)],
    )
    # Progress bar replaces per-area fetch logs
    logging.getLogger("overpass.batch").setLevel(logging.INFO)

    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=(
            "[OSMTW] OSM Phone Normalizer\n"
            "Fetch phone-tagged entities from Overpass API and normalize to E.123 format.\n\n"
            "[OSMTW] 電話格式正規化工具\n"
            "從 Overpass API 擷取帶有電話標籤的資料，檢查並將其轉換為 E.123 格式。\n\n"
        ),
        epilog=(
            "area --target 接受以下格式 accepts:\n"
            "  ISO 3166-2 代碼 code    TPE  NWT  TAO  TXG  TNN  KHH  TTT  PEN  KMN  LIE ...\n"
            "  英文名稱 English         Taipei  Taitung  Kaohsiung  'Hsinchu County' ...\n"
            "  中文簡稱 Chinese short   竹市  竹縣  台北  高市 ...\n"
            "  中文全名 Chinese full    臺北市  臺東縣  澎湖縣 ...\n"
            "\n"
            "examples:\n"
            "  python main.py --preset cities\n"
            "  python main.py --target TXG\n"
            "  python main.py --target Taitung --dry-run --verbose\n"
            "  python main.py --target 竹市\n"
            "  python main.py --target TPE --no-cache\n"
        ),
    )
    parser.add_argument(
        "-r",
        "--region",
        choices=REGIONS,
        default="TW",
        help="Country region for phone normalization (default: TW)",
    )
    parser.add_argument(
        "-p",
        "--preset",
        choices=list(ALL_PRESETS),
        help="Predefined area set",
    )
    parser.add_argument(
        "-t",
        "--target",
        metavar="TARGET",
        help="Single area by code, English, or Chinese name",
    )
    parser.add_argument(
        "-l",
        "--list",
        nargs="?",
        const="preset",
        choices=["preset", "alias"],
        metavar="LISTING",
        help="List available presets/aliases and exit. LISTING: preset (default), alias",
    )
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR, metavar="DIR")
    parser.add_argument(
        "--delay",
        type=float,
        default=0,
        metavar="SEC",
        help=f"Seconds between Overpass requests (default: 0 for --target, {REQUEST_DELAY} for --preset)",
    )
    parser.add_argument(
        "--no-cache", action="store_true", help="Re-fetch even if cached"
    )
    parser.add_argument(
        "--print-query",
        "-q",
        action="store_true",
        help="Print Overpass queries and exit without fetching",
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Show changes without writing files"
    )
    parser.add_argument(
        "--upload",
        "--up",
        "-u",
        choices=["josm", "api", "level0"],
        metavar="MODE",
        help="Export changeset: 'josm' writes .osc for JOSM; 'api' uploads directly to OSM API; 'level0' writes text for level0.osmz.ru",
    )
    parser.add_argument(
        "--changeset-comment",
        default="Normalize phone numbers to E.123 format",
        metavar="TEXT",
        help="Changeset comment for --upload api",
    )
    parser.add_argument(
        "--format",
        choices=["e123", "rfc3966"],
        default="e123",
        metavar="FMT",
        help="Output phone format: e123 (default, E.123 international) or rfc3966 (tel: URI)",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Print each changed tag"
    )
    args = parser.parse_args()
    args.output_dir = args.output_dir / args.region

    # --list: print presets / aliases and exit
    if args.list:
        _aliases = REGION_ALIASES.get(args.region, {})
        if args.list in ("preset", None):
            region_filter = REGION_PRESETS.get(args.region, REGION_PRESETS)
            region_map = {args.region: region_filter} if args.region in REGION_PRESETS else REGION_PRESETS
            for region, presets in region_map.items():
                t = Table(title=f"Presets for {region}  (--preset)", title_style="bold")
                t.add_column("Name", style="cyan")
                t.add_column("Areas", justify="right")
                t.add_column("Area names", style="dim")
                for name, area_list in presets.items():
                    t.add_row(name, str(len(area_list)), "  ".join(a.name for a in area_list))
                console.print(t)
        if args.list == "alias":
            # Group aliases by canonical name
            by_canonical: dict[str, list[str]] = {}
            for alias, canonical in _aliases.items():
                by_canonical.setdefault(canonical, []).append(alias)

            def _alias_sort_key(item: tuple[str, list[str]]) -> tuple:
                _, aliases = item
                # Numeric-only aliases are JIS/ISO codes — sort those first
                codes = [a for a in aliases if a.isdigit()]
                return (0, int(min(codes))) if codes else (1, item[0])

            def _alias_inner_key(alias: str) -> tuple:
                # Tier 2: contains any non-ASCII letter (CJK / kana / etc.)
                if any(c > "\x7f" for c in alias):
                    return (2, alias)
                # Tier 0: digit-only (JIS codes) or ISO pattern (JP-01)
                core = alias.replace("-", "")
                if core.isdigit():
                    return (0, alias.zfill(10))
                # Tier 0: short uppercase letter codes ≤ 4 chars (TPE, NWT, NTPC…)
                if alias.isupper() and len(alias) <= 4 and alias.isalpha():
                    return (0, alias)
                # Tier 1: everything else (English full names, longer codes)
                return (1, alias)

            t = Table(title=f"Aliases for {args.region}  (--target)", title_style="bold")
            t.add_column("Area", style="cyan")
            t.add_column("Accepted aliases", style="dim")
            for canonical, aliases in sorted(by_canonical.items(), key=_alias_sort_key):
                t.add_row(canonical, "  ".join(sorted(aliases, key=_alias_inner_key)))
            console.print(t)
        raise SystemExit(0)

    if not args.target and not args.preset:
        parser.print_help()
        raise SystemExit(0)

    # Resolve area(s)
    _aliases = REGION_ALIASES.get(args.region, {})
    _city_lookup = _REGION_CITY_LOOKUP.get(args.region, {})
    if args.target:
        areas: list[Area] = [resolve_area(args.target, _aliases, _city_lookup)]
    else:
        default_preset = REGION_DEFAULT_PRESET.get(args.region, next(iter(ALL_PRESETS)))
        areas = ALL_PRESETS[args.preset or default_preset]
        if args.delay == 0:
            args.delay = REQUEST_DELAY

    if args.print_query:
        from overpass import build_query

        for area in areas:
            print(f"/* {area.name} */")
            print(build_query(area))
            print()
        raise SystemExit(0)

    # Header panel
    fmt_label = "RFC3966" if args.format == "rfc3966" else "E.123"
    area_label = areas[0].name if args.target else (args.preset or "(UNKNOWN)")
    badges: list[str] = []
    if args.dry_run:
        badges.append("[on dark_orange] dry-run [/on dark_orange]")
    if args.verbose:
        badges.append("[on grey23] verbose [/on grey23]")
    badge_str = "  " + "  ".join(badges) if badges else ""

    console.print(
        Panel(
            f"[bold white]OSM Phone Normalizer[/bold white]  "
            f"[dim]·[/dim]  Region: [bold cyan]{args.region}[/bold cyan]  "
            f"[dim]·[/dim]  Area: [bold]{area_label}[/bold]  "
            f"[dim]·[/dim]  Format: [cyan]{fmt_label}[/cyan]" + badge_str,
            expand=False,
        )
    )

    # Fetch with progress bar
    with Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]{task.description}"),
        BarColumn(),
        MofNCompleteColumn(),
        TextColumn("[dim]·[/dim]"),
        TextColumn("[cyan]{task.fields[current_area]}[/cyan]"),
        TimeElapsedColumn(),
        console=console,
    ) as progress:
        fetch_task = progress.add_task("Fetching", total=len(areas), current_area="")

        def on_progress(i: int, total: int, area_name: str, from_cache: bool) -> None:
            suffix = " [dim](cached)[/dim]" if from_cache else ""
            progress.update(
                fetch_task, completed=i, current_area=f"{area_name}{suffix}"
            )

        try:
            results = batch_fetch(
                areas,
                output_dir=args.output_dir,
                delay=args.delay,
                skip_existing=not args.no_cache,
                progress_callback=on_progress,
            )
        except ValueError as exc:
            console.print(
                Panel(
                    f"[bold red]Error:[/bold red] {exc}",
                    expand=False,
                    border_style="red",
                )
            )
            raise SystemExit(1)

    # Normalize
    phone_fmt: int = (
        PhoneNumberFormat.RFC3966
        if args.format == "rfc3966"
        else PhoneNumberFormat.INTERNATIONAL
    )  
    summary, diffs = normalize_results(
        results,
        output_dir=args.output_dir,
        dry_run=args.dry_run,
        verbose=args.verbose,
        fmt=phone_fmt,
        region=args.region,
    )

    total_fetched = sum(len(v) for v in results.values())
    total_changed = sum(summary.values())

    if args.upload == "josm":
        from upload.osm_api import build_osc
        from upload.josm import open_in_josm

        missing_version = [e for e, _ in diffs if "version" not in e]
        if missing_version:
            log.warning(
                "%d element(s) missing version — re-run with --no-cache to get metadata",
                len(missing_version),
            )
        osc_xml = build_osc(diffs)
        osc_path = args.output_dir / "changes.osc"
        osc_path.write_text(osc_xml, encoding="utf-8")
        log.info("Wrote %d change(s) to %s", len(diffs), osc_path)
        if not open_in_josm(osc_xml):
            log.info("Open %s in JOSM manually to review and upload", osc_path)

    elif args.upload == "level0":
        from overpass import build_query
        from upload.level0 import level0_url

        for area in areas:
            url = level0_url(build_query(area))
            console.print(f"[bold cyan]{area.name}[/bold cyan]  {url}")

    elif args.upload == "api":
        import os
        from upload.osm_api import upload_osm

        token = os.environ.get("OSM_ACCESS_TOKEN", "")
        if not token:
            log.error("OSM_ACCESS_TOKEN env var not set — cannot upload")
            raise SystemExit(1)
        changeset_id = upload_osm(
            diffs,
            access_token=token,
            comment=args.changeset_comment,
            dry_run=args.dry_run,
        )
        if changeset_id:
            console.print(
                f"[bold green]Uploaded[/bold green] — "
                f"https://www.openstreetmap.org/changeset/{changeset_id}"
            )

    # Done panel
    console.print(
        Panel(
            f"[bold green]Done.[/bold green]  "
            f"[cyan]{total_fetched}[/cyan] entities fetched, "
            f"[bold green]{total_changed}[/bold green] phone tags normalized.\n"
            f"[dim]已處理完畢。此次獲取 {total_fetched} 筆資料，"
            f"其中正規化 {total_changed} 筆資料。[/dim]",
            expand=False,
        )
    )
