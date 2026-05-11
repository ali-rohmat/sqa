#!/usr/bin/env python3
"""
╔══════════════════════════════════════════╗
║   DevTools Suite — Selenium + ZIP App   ║
╚══════════════════════════════════════════╝
Features:
  1. Run Selenium web automation tests
  2. Compress files/folders to ZIP
  3. Inspect ZIP contents
"""

import os
import sys
import time
import shutil
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
    from rich.prompt import Prompt, Confirm
    from rich.text import Text
    from rich import box
    from rich.columns import Columns
    from rich.rule import Rule
    HAS_RICH = True
except ImportError:
    HAS_RICH = False

from src.compressor import compress_files, list_zip_contents
from src.selenium_tests import run_selenium_tests

console = Console() if HAS_RICH else None


def hr(char="─"):
    w = shutil.get_terminal_size((80, 24)).columns
    print(char * w)


def print_header():
    if HAS_RICH:
        console.print()
        console.print(Panel.fit(
            "[bold cyan]🛠  DevTools Suite[/bold cyan]\n"
            "[dim]Selenium Testing · ZIP Compressor · File Inspector[/dim]",
            border_style="cyan",
            padding=(1, 4),
        ))
        console.print()
    else:
        hr("═")
        print("  DevTools Suite — Selenium Testing + ZIP Compressor")
        hr("═")
        print()


def print_menu():
    if HAS_RICH:
        table = Table(show_header=False, box=box.SIMPLE, padding=(0, 2))
        table.add_column("Key", style="bold yellow", width=4)
        table.add_column("Action", style="white")
        table.add_row("1", "🧪  Run Selenium Web Tests")
        table.add_row("2", "📦  Compress Files to ZIP")
        table.add_row("3", "🔍  Inspect ZIP Contents")
        table.add_row("4", "📄  Generate Sample Files")
        table.add_row("q", "🚪  Quit")
        console.print(Panel(table, title="[bold]Main Menu[/bold]", border_style="blue"))
    else:
        print("  [1] Run Selenium Web Tests")
        print("  [2] Compress Files to ZIP")
        print("  [3] Inspect ZIP Contents")
        print("  [4] Generate Sample Files")
        print("  [q] Quit")
        print()


def format_size(bytes_val: int) -> str:
    for unit in ["B", "KB", "MB", "GB"]:
        if bytes_val < 1024:
            return f"{bytes_val:.1f} {unit}"
        bytes_val /= 1024
    return f"{bytes_val:.1f} TB"


# ─────────────────────────────────────────
# FEATURE 1: Selenium Tests
# ─────────────────────────────────────────
def menu_selenium():
    if HAS_RICH:
        console.print(Rule("[bold yellow]🧪 Selenium Web Tests[/bold yellow]"))
        url = Prompt.ask(
            "\n[cyan]Target URL[/cyan]",
            default="https://example.com"
        )
    else:
        hr()
        print("SELENIUM WEB TESTS")
        hr()
        url = input("Target URL [https://example.com]: ").strip() or "https://example.com"

    if not url.startswith("http"):
        url = "https://" + url

    if HAS_RICH:
        console.print(f"\n[dim]Running tests against:[/dim] [bold]{url}[/bold]\n")
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            transient=True,
        ) as progress:
            task = progress.add_task("[cyan]Initializing Selenium...", total=None)
            suite = run_selenium_tests(url)
            progress.update(task, description="[green]Tests complete!")
    else:
        print(f"\nRunning tests against: {url}")
        suite = run_selenium_tests(url)

    _display_test_results(suite)

    # Save report
    report_path = f"output/test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    os.makedirs("output", exist_ok=True)
    _save_test_report(suite, report_path, url)

    if HAS_RICH:
        console.print(f"\n[dim]📄 Report saved:[/dim] [green]{report_path}[/green]")
    else:
        print(f"\nReport saved: {report_path}")


def _display_test_results(suite):
    if HAS_RICH:
        table = Table(
            show_header=True,
            header_style="bold magenta",
            box=box.ROUNDED,
            padding=(0, 1),
        )
        table.add_column("Test Name", style="white", min_width=25)
        table.add_column("Status", justify="center", width=8)
        table.add_column("Duration", justify="right", width=10)
        table.add_column("Message", style="dim")

        status_styles = {
            "PASS": "[bold green]✓ PASS[/bold green]",
            "FAIL": "[bold red]✗ FAIL[/bold red]",
            "SKIP": "[bold yellow]⊘ SKIP[/bold yellow]",
            "ERROR": "[bold red]⚠ ERROR[/bold red]",
        }

        for r in suite.results:
            table.add_row(
                r.name,
                status_styles.get(r.status, r.status),
                f"{r.duration:.2f}s",
                r.message,
            )

        console.print(table)
        console.print()

        # Summary
        color = "green" if suite.failed == 0 else "red"
        console.print(Panel(
            f"[bold]Total:[/bold] {suite.total}  "
            f"[green]Passed: {suite.passed}[/green]  "
            f"[red]Failed: {suite.failed}[/red]  "
            f"[yellow]Skipped: {suite.skipped}[/yellow]  "
            f"[bold {color}]Success Rate: {suite.success_rate}%[/bold {color}]",
            title="[bold]Test Summary[/bold]",
            border_style=color,
        ))
    else:
        hr()
        print(f"{'Test Name':<30} {'Status':<8} {'Time':>8}  Message")
        hr("-")
        for r in suite.results:
            print(f"{r.name:<30} {r.status:<8} {r.duration:>6.2f}s  {r.message}")
        hr()
        print(f"Total: {suite.total} | Pass: {suite.passed} | Fail: {suite.failed} | Skip: {suite.skipped}")
        print(f"Success Rate: {suite.success_rate}%")


def _save_test_report(suite, path, url):
    with open(path, "w") as f:
        f.write(f"SELENIUM TEST REPORT\n")
        f.write(f"{'='*60}\n")
        f.write(f"URL:       {url}\n")
        f.write(f"Date:      {suite.start_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Total:     {suite.total}\n")
        f.write(f"Passed:    {suite.passed}\n")
        f.write(f"Failed:    {suite.failed}\n")
        f.write(f"Skipped:   {suite.skipped}\n")
        f.write(f"Rate:      {suite.success_rate}%\n")
        f.write(f"{'='*60}\n\n")
        for r in suite.results:
            f.write(f"[{r.status}] {r.name} ({r.duration:.2f}s)\n")
            f.write(f"       {r.message}\n\n")


# ─────────────────────────────────────────
# FEATURE 2: ZIP Compressor
# ─────────────────────────────────────────
def menu_compress():
    if HAS_RICH:
        console.print(Rule("[bold yellow]📦 ZIP Compressor[/bold yellow]"))
        console.print("\n[dim]Enter paths to compress (files or folders). Empty line to finish.[/dim]\n")
    else:
        hr()
        print("ZIP COMPRESSOR")
        hr()
        print("Enter paths (empty line when done):")

    paths = []
    idx = 1
    while True:
        if HAS_RICH:
            val = Prompt.ask(f"  Path {idx}", default="").strip()
        else:
            val = input(f"  Path {idx}: ").strip()

        if not val:
            break
        if os.path.exists(val):
            paths.append(val)
            if HAS_RICH:
                console.print(f"  [green]✓ Added:[/green] {val}")
            else:
                print(f"  Added: {val}")
        else:
            if HAS_RICH:
                console.print(f"  [red]✗ Not found:[/red] {val}")
            else:
                print(f"  Not found: {val}")
        idx += 1

    if not paths:
        if HAS_RICH:
            console.print("[red]No valid paths provided.[/red]")
        else:
            print("No valid paths provided.")
        return

    # Output path
    if HAS_RICH:
        out = Prompt.ask(
            "\n[cyan]Output ZIP path[/cyan]",
            default=f"output/archive_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
        )
        level = int(Prompt.ask("[cyan]Compression level[/cyan] (1=fast, 9=best)", default="6"))
    else:
        out = input(f"\nOutput ZIP path: ").strip() or f"output/archive_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
        level = int(input("Compression level [1-9]: ").strip() or "6")

    if HAS_RICH:
        console.print()
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            console=console,
            transient=True,
        ) as progress:
            task = progress.add_task("[cyan]Compressing...", total=None)
            result = compress_files(paths, out, compression_level=level)
    else:
        print("\nCompressing...")
        result = compress_files(paths, out, compression_level=level)

    _display_compress_results(result)


def _display_compress_results(result):
    if not result["success"]:
        if HAS_RICH:
            console.print(f"[red]Compression failed:[/red] {result['errors']}")
        else:
            print(f"ERROR: {result['errors']}")
        return

    if HAS_RICH:
        table = Table(show_header=True, header_style="bold cyan", box=box.SIMPLE_HEAVY)
        table.add_column("File", style="white")
        table.add_column("Original Size", justify="right")

        for f in result["files_added"]:
            table.add_row(f["name"], format_size(f["original_size"]))

        console.print(table)
        console.print()

        ratio_color = "green" if result["compression_ratio"] > 20 else "yellow"
        console.print(Panel(
            f"[bold]Output:[/bold] {result['output_path']}\n"
            f"[bold]Files:[/bold] {len(result['files_added'])}\n"
            f"[bold]Original:[/bold] {format_size(result['total_original_size'])}\n"
            f"[bold]Compressed:[/bold] {format_size(result['compressed_size'])}\n"
            f"[bold {ratio_color}]Saved: {result['compression_ratio']}%[/bold {ratio_color}]",
            title="[bold green]✓ Compression Complete[/bold green]",
            border_style="green",
        ))
    else:
        print(f"\nDone! Output: {result['output_path']}")
        print(f"Files:      {len(result['files_added'])}")
        print(f"Original:   {format_size(result['total_original_size'])}")
        print(f"Compressed: {format_size(result['compressed_size'])}")
        print(f"Saved:      {result['compression_ratio']}%")


# ─────────────────────────────────────────
# FEATURE 3: Inspect ZIP
# ─────────────────────────────────────────
def menu_inspect():
    if HAS_RICH:
        console.print(Rule("[bold yellow]🔍 ZIP Inspector[/bold yellow]"))
        zip_path = Prompt.ask("\n[cyan]ZIP file path[/cyan]")
    else:
        hr()
        print("ZIP INSPECTOR")
        hr()
        zip_path = input("ZIP file path: ").strip()

    if not os.path.exists(zip_path):
        if HAS_RICH:
            console.print(f"[red]File not found:[/red] {zip_path}")
        else:
            print(f"File not found: {zip_path}")
        return

    try:
        contents = list_zip_contents(zip_path)
        if HAS_RICH:
            table = Table(
                show_header=True,
                header_style="bold magenta",
                box=box.ROUNDED,
            )
            table.add_column("Filename", style="white")
            table.add_column("Original", justify="right")
            table.add_column("Compressed", justify="right")
            table.add_column("Ratio", justify="right")
            table.add_column("Modified")

            for item in contents:
                if item["original_size"] > 0:
                    ratio = round((1 - item["compressed_size"] / item["original_size"]) * 100, 1)
                    ratio_str = f"[green]{ratio}%[/green]"
                else:
                    ratio_str = "—"

                table.add_row(
                    item["filename"],
                    format_size(item["original_size"]),
                    format_size(item["compressed_size"]),
                    ratio_str,
                    item["date_modified"],
                )

            console.print(table)
            console.print(f"\n[dim]{len(contents)} items in archive[/dim]")
        else:
            print(f"\n{'Filename':<40} {'Original':>10} {'Compressed':>12}")
            hr("-")
            for item in contents:
                print(f"{item['filename']:<40} {format_size(item['original_size']):>10} {format_size(item['compressed_size']):>12}")
            print(f"\n{len(contents)} items in archive")

    except Exception as e:
        if HAS_RICH:
            console.print(f"[red]Error reading ZIP:[/red] {e}")
        else:
            print(f"Error: {e}")


# ─────────────────────────────────────────
# FEATURE 4: Generate Sample Files
# ─────────────────────────────────────────
def menu_generate_samples():
    sample_dir = "sample_files"
    os.makedirs(sample_dir, exist_ok=True)

    samples = {
        "report.txt": "Quarterly Sales Report\n" + "="*30 + "\nQ1: $1,200,000\nQ2: $1,450,000\nQ3: $1,380,000\nQ4: $1,750,000\nTotal: $5,780,000\n",
        "config.json": '{\n  "app": "DevTools Suite",\n  "version": "1.0.0",\n  "debug": false,\n  "database": {\n    "host": "localhost",\n    "port": 5432\n  }\n}\n',
        "readme.md": "# DevTools Suite\n\nA Python application with Selenium testing and ZIP compression.\n\n## Features\n- Web automation testing\n- File compression\n- ZIP inspection\n",
        "data.csv": "id,name,score,grade\n1,Alice,95,A\n2,Bob,82,B\n3,Carol,78,C\n4,David,91,A\n5,Eve,88,B\n",
        "notes.txt": "Meeting Notes\n" + "-"*20 + "\n- Review test coverage\n- Deploy to staging\n- Update documentation\n- Code review PR #42\n",
    }

    created = []
    for filename, content in samples.items():
        path = os.path.join(sample_dir, filename)
        with open(path, "w") as f:
            f.write(content)
        created.append(path)

    if HAS_RICH:
        console.print(f"\n[green]✓ Generated {len(created)} sample files in [bold]{sample_dir}/[/bold][/green]")
        for p in created:
            console.print(f"  [dim]{p}[/dim]")
        console.print(f"\n[dim]You can now compress [bold]{sample_dir}/[/bold] using option 2[/dim]")
    else:
        print(f"\nGenerated {len(created)} files in {sample_dir}/")
        for p in created:
            print(f"  {p}")


# ─────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────
def main():
    os.makedirs("output", exist_ok=True)
    print_header()

    while True:
        print_menu()

        if HAS_RICH:
            choice = Prompt.ask("[bold]Choice[/bold]", choices=["1", "2", "3", "4", "q"], default="1")
        else:
            choice = input("Choice: ").strip().lower()

        if choice == "q":
            if HAS_RICH:
                console.print("\n[dim]Goodbye! 👋[/dim]\n")
            else:
                print("\nGoodbye!")
            break
        elif choice == "1":
            menu_selenium()
        elif choice == "2":
            menu_compress()
        elif choice == "3":
            menu_inspect()
        elif choice == "4":
            menu_generate_samples()
        else:
            if HAS_RICH:
                console.print("[red]Invalid choice[/red]")
            else:
                print("Invalid choice")

        if HAS_RICH:
            console.print()
            input("  Press Enter to continue...")
            console.clear()
            print_header()
        else:
            input("\nPress Enter to continue...")
            print()


if __name__ == "__main__":
    main()
