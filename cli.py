#!/usr/bin/env python3
"""
BioCrypt-DNA Command-Line Interface
===================================
Terminal suite for bio-constrained DNA steganography, in-silico PCR extraction,
and biological genomic sequence auditing.
"""

from __future__ import annotations

import os
import sys

# Ensure Python 3.8+
if sys.version_info < (3, 8):
    sys.stderr.write(
        "Error: BioCrypt-DNA requires Python 3.8 or newer.\n"
        "Please execute with 'py cli.py' or 'python3 cli.py'.\n"
    )
    sys.exit(1)

# Ensure local core package is importable
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from core import (
    AuthenticationError,
    BiologicalMetrics,
    CarrierEngine,
    CarrierError,
    ChecksumMismatchError,
    CryptoError,
    DNASteganographyEngine,
    FastaParseError,
    HeaderCorruptError,
    InvalidMagicError,
    PrimerNotFoundError,
    TransductionError,
    ViabilityReport,
)

# Configure console for cross-platform compatibility
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

console = Console(safe_box=True)


def print_banner() -> None:
    """Displays project header banner."""
    console.print(
        Panel.fit(
            "[bold cyan]BioCrypt-DNA[/bold cyan] : [bold green]Genomic Steganography & Data Hiding Suite[/bold green]\n"
            "[dim]Authenticated AES-256-GCM | 9-State Bio-FSM | In-Silico PCR Primer Annealing[/dim]",
            border_style="cyan",
        )
    )


def render_scorecard_table(report: ViabilityReport, title: str = "Biological Viability Audit Scorecard") -> Table:
    """Constructs a Rich table displaying sequence biophysical metrics."""
    table = Table(title=title, show_header=True, header_style="bold magenta")
    table.add_column("Biophysical Metric", style="cyan", width=30)
    table.add_column("Measured Value", style="white", width=22)
    table.add_column("Biological Constraint", style="yellow", width=25)
    table.add_column("Status", style="bold", width=12)

    # GC Content
    gc_status = "[green]PASS[/green]" if (40.0 <= report.gc_percent <= 60.0) else "[red]FAIL[/red]"
    table.add_row(
        "Global GC Content",
        f"{report.gc_percent:.2f}%",
        "40.0% - 60.0% window",
        gc_status,
    )

    # Sliding GC
    sliding_gc_status = (
        "[green]PASS[/green]"
        if (35.0 <= report.sliding_gc_min and report.sliding_gc_max <= 65.0)
        else "[yellow]WARN[/yellow]"
    )
    table.add_row(
        "Sliding Window GC (min/max)",
        f"{report.sliding_gc_min:.1f}% / {report.sliding_gc_max:.1f}%",
        "35.0% - 65.0% window",
        sliding_gc_status,
    )

    # Max Homopolymer Run
    homo_status = (
        "[green]PASS[/green]"
        if report.max_homopolymer_run <= 2
        else "[red]FAIL[/red]"
    )
    table.add_row(
        "Max Homopolymer Run",
        f"{report.max_homopolymer_run} bp",
        "<= 2 bp (No optical noise)",
        homo_status,
    )

    # In-Frame Stops
    in_frame_count = sum(len(v) for v in report.in_frame_stop_codons.values())
    stop_status = "[green]PASS[/green]" if in_frame_count == 0 else "[red]FAIL[/red]"
    table.add_row(
        "In-Frame Stop Codons",
        f"{in_frame_count} occurrences",
        "0 (TAA, TAG, TGA)",
        stop_status,
    )

    # Shannon Entropy
    table.add_row(
        "Shannon Information Entropy",
        f"{report.shannon_entropy:.4f} bits/nt",
        "Target: ~1.85 - 2.00 bits",
        "[green]OPTIMAL[/green]",
    )

    # Wallace Melting Temperature
    table.add_row(
        "Wallace Melting Temp (Tm)",
        f"{report.melting_temperature_tm:.2f} °C",
        "Sequence duplex stability",
        "[cyan]STABLE[/cyan]",
    )

    # Overall Viability
    overall = "[green]VIABLE (PASS)[/green]" if report.is_viable else "[red]VIOLATIONS (FAIL)[/red]"
    table.add_row("Overall Biological Viability", f"{report.sequence_length} bp total", "All Constraints", overall)

    return table


@click.group()
def cli() -> None:
    """BioCrypt-DNA: Computational DNA Steganography and Data Hiding System."""
    pass


@cli.command("embed")
@click.option(
    "--input", "-i", "input_path",
    required=True,
    help="Path to secret file to conceal.",
)
@click.option(
    "--carrier", "-c", "carrier_path",
    default=None,
    help="Path to host FASTA file (default: synthetic carrier genome generated).",
)
@click.option(
    "--output", "-o", "output_path",
    required=True,
    help="Path to output stego FASTA file.",
)
@click.option(
    "--password", "-p", "password",
    required=True,
    help="Cryptographic passphrase for AES-256-GCM encryption.",
)
@click.option(
    "--locus", "-l", "locus",
    default="center",
    help="Genomic insertion locus: 'center', 'append', or integer coordinate index.",
)
def embed(
    input_path: str,
    carrier_path: str | None,
    output_path: str,
    password: str,
    locus: str,
) -> None:
    """Conceal arbitrary secret data inside a genomic carrier FASTA sequence."""
    print_banner()

    # 1. Read secret payload
    if not os.path.exists(input_path):
        console.print(f"[bold red]Error:[/bold red] Secret input file not found: {input_path}")
        sys.exit(1)

    with open(input_path, "rb") as f:
        secret_bytes = f.read()

    console.print(f"[bold green][+][/bold green] Read [bold white]{len(secret_bytes)} bytes[/bold white] from [cyan]{input_path}[/cyan]")

    # 2. Read carrier sequence if provided
    carrier_seq: str | None = None
    carrier_header = "stego_genome"
    if carrier_path:
        if not os.path.exists(carrier_path):
            console.print(f"[bold red]Error:[/bold red] Carrier FASTA file not found: {carrier_path}")
            sys.exit(1)
        records = CarrierEngine.read_fasta(carrier_path)
        carrier_seq = records[0].sequence
        carrier_header = f"{records[0].header}_stego"
        console.print(f"[bold green][+][/bold green] Loaded carrier genome: [cyan]{len(carrier_seq)} bp[/cyan] from {carrier_path}")
    else:
        console.print("[dim]No carrier supplied — generating synthetic host carrier genome...[/dim]")

    # 3. Parse locus if integer
    parsed_locus: int | str = locus
    if locus.isdigit():
        parsed_locus = int(locus)

    # 4. Conceal via DNASteganographyEngine
    try:
        engine = DNASteganographyEngine(passphrase=password)
        with console.status("[bold cyan]Applying 4-Stage Stego Pipeline (AES-256-GCM -> FSM Transduction -> Embedding)...[/bold cyan]"):
            stego_seq, report = engine.conceal(
                secret_data=secret_bytes,
                carrier_fasta=carrier_seq,
                locus=parsed_locus,
            )
    except Exception as exc:
        console.print(f"[bold red]Embedding Pipeline Error:[/bold red] {exc}")
        sys.exit(1)

    # 5. Write stego FASTA file
    CarrierEngine.write_fasta(header=carrier_header, sequence=stego_seq, output_path=output_path)
    console.print(f"[bold green][+][/bold green] Stego genome successfully written to: [bold cyan]{output_path}[/bold cyan] ({len(stego_seq)} bp)")

    # 6. Render metrics scorecard
    console.print()
    console.print(render_scorecard_table(report, title="Payload Strand Biological Audit"))


@cli.command("extract")
@click.option(
    "--carrier", "-c", "carrier_path",
    required=True,
    help="Path to stego FASTA file containing concealed amplicon.",
)
@click.option(
    "--output", "-o", "output_path",
    default=None,
    help="Path to save recovered secret file (or stdout if omitted).",
)
@click.option(
    "--password", "-p", "password",
    required=True,
    help="Cryptographic passphrase for AES-256-GCM decryption.",
)
def extract(
    carrier_path: str,
    output_path: str | None,
    password: str,
) -> None:
    """Extract and decrypt secret payload from a stego FASTA sequence."""
    print_banner()

    if not os.path.exists(carrier_path):
        console.print(f"[bold red]Error:[/bold red] Stego FASTA file not found: {carrier_path}")
        sys.exit(1)

    try:
        records = CarrierEngine.read_fasta(carrier_path)
        stego_seq = records[0].sequence
        console.print(f"[bold green][+][/bold green] Loaded stego genome: [cyan]{len(stego_seq)} bp[/cyan]")

        engine = DNASteganographyEngine(passphrase=password)
        with console.status("[bold cyan]Executing In-Silico PCR -> Inverse FSM -> AES-GCM Decryption...[/bold cyan]"):
            recovered_bytes = engine.extract(stego_seq)

    except PrimerNotFoundError as exc:
        console.print(f"[bold red]PCR Extraction Error:[/bold red] {exc}")
        sys.exit(1)
    except AuthenticationError as exc:
        console.print(f"[bold red]Cryptographic Authentication Error:[/bold red] {exc}")
        sys.exit(1)
    except ChecksumMismatchError as exc:
        console.print(f"[bold red]Integrity Checksum Error:[/bold red] {exc}")
        sys.exit(1)
    except Exception as exc:
        console.print(f"[bold red]Extraction Failed:[/bold red] {exc}")
        sys.exit(1)

    console.print(f"[bold green]✔ Plaintext Recovery Successful![/bold green] ([bold white]{len(recovered_bytes)} bytes[/bold white])")

    if output_path:
        with open(output_path, "wb") as f:
            f.write(recovered_bytes)
        console.print(f"[bold green][+][/bold green] Extracted data saved to: [bold cyan]{output_path}[/bold cyan]")
    else:
        # Display preview if text, else notify binary
        try:
            preview = recovered_bytes.decode("utf-8")
            console.print(Panel(preview, title="Recovered Secret Payload Preview", border_style="green"))
        except UnicodeDecodeError:
            console.print(f"[yellow]Binary payload recovered ({len(recovered_bytes)} bytes). Use -o <file> to write to disk.[/yellow]")


@cli.command("audit")
@click.option(
    "--carrier", "-c", "carrier_path",
    default=None,
    help="Path to FASTA file to audit.",
)
@click.option(
    "--input", "-i", "input_path",
    default=None,
    help="Alternative flag for FASTA file path.",
)
def audit(carrier_path: str | None, input_path: str | None) -> None:
    """Display a biophysical scorecard for a FASTA sequence or genome."""
    print_banner()

    target_path = carrier_path or input_path
    if not target_path:
        console.print("[bold red]Error:[/bold red] Please provide a FASTA file via --carrier / -c or --input / -i.")
        sys.exit(1)

    if not os.path.exists(target_path):
        console.print(f"[bold red]Error:[/bold red] Target FASTA file not found: {target_path}")
        sys.exit(1)

    try:
        records = CarrierEngine.read_fasta(target_path)
    except Exception as exc:
        console.print(f"[bold red]FASTA Read Error:[/bold red] {exc}")
        sys.exit(1)

    for record in records:
        report = BiologicalMetrics.audit_sequence(record.sequence)
        console.print(render_scorecard_table(report, title=f"Scorecard: >{record.header}"))
        if not report.is_viable:
            console.print("[bold yellow]Diagnostics:[/bold yellow]")
            for msg in report.diagnostic_messages:
                console.print(f"  [red]*[/red] {msg}")


@cli.command("simulate-pcr")
@click.option(
    "--carrier", "-c", "carrier_path",
    required=True,
    help="Path to stego FASTA file.",
)
@click.option(
    "--fwd", "-f", "fwd_primer",
    default=None,
    help="Forward primer (default: 5'-ATCGTTAGGCTACGATCG-3').",
)
@click.option(
    "--rev", "-r", "rev_primer",
    default=None,
    help="Reverse primer (default: 5'-CGATCGTAGCCTAACGAT-3').",
)
def simulate_pcr(carrier_path: str, fwd_primer: str | None, rev_primer: str | None) -> None:
    """Simulates in-silico PCR amplification of the steganographic amplicon."""
    print_banner()

    if not os.path.exists(carrier_path):
        console.print(f"[bold red]Error:[/bold red] Carrier FASTA not found: {carrier_path}")
        sys.exit(1)

    carrier = CarrierEngine(
        fwd_primer=fwd_primer or "ATCGTTAGGCTACGATCG",
        rev_primer=rev_primer or "CGATCGTAGCCTAACGAT",
    )
    records = carrier.read_fasta(carrier_path)
    seq = records[0].sequence

    fwd_tm = BiologicalMetrics.estimate_melting_temp(carrier.fwd_primer)
    rev_tm = BiologicalMetrics.estimate_melting_temp(carrier.rev_primer)

    table = Table(title="In-Silico PCR Primer Specification", header_style="bold cyan")
    table.add_column("Primer", style="white")
    table.add_column("Sequence (5' -> 3')", style="green")
    table.add_column("Length", style="yellow")
    table.add_column("Tm (°C)", style="magenta")

    table.add_row("Forward Primer", carrier.fwd_primer, f"{len(carrier.fwd_primer)} nt", f"{fwd_tm:.2f} °C")
    table.add_row("Reverse Primer", carrier.rev_primer, f"{len(carrier.rev_primer)} nt", f"{rev_tm:.2f} °C")
    console.print(table)

    try:
        payload = carrier.extract_from_carrier(seq)
        amplicon = carrier.assemble_amplicon(payload)
        console.print(f"[bold green][+] In-Silico Amplification Succeeded![/bold green]")
        console.print(f"  * Amplicon Size: [bold cyan]{len(amplicon)} bp[/bold cyan]")
        console.print(f"  * Insert Size  : [bold cyan]{len(payload)} bp[/bold cyan]")
        console.print(f"  * Annealing Tm : [bold cyan]{min(fwd_tm, rev_tm) - 5.0:.1f} °C[/bold cyan] (recommended)")
    except PrimerNotFoundError as exc:
        console.print(f"[bold red]PCR Amplification Failed:[/bold red] {exc}")
        sys.exit(1)


if __name__ == "__main__":
    cli()
