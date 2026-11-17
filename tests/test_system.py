"""
BioCrypt-DNA Comprehensive Test Suite
=====================================
Automated verification of lossless round-trip recovery, cryptographic integrity,
and biophysical viability constraint compliance (homopolymers, GC%, stop codons).
"""

from __future__ import annotations

import os
import sys
import tempfile
import pytest
from click.testing import CliRunner

# Ensure root directory is on PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core import (
    AuthenticationError,
    BiologicalMetrics,
    CarrierEngine,
    ChecksumMismatchError,
    CryptoEngine,
    DNASteganographyEngine,
    HeaderCorruptError,
    InvalidMagicError,
    PrimerNotFoundError,
    Transducer,
    TransductionError,
)
from cli import cli


@pytest.fixture
def secret_passphrase() -> str:
    return "UltraSecureBioComputingPassphrase2026!#"


@pytest.fixture
def carrier_fasta_record() -> str:
    # 3000 bp innocent carrier sequence
    unit = "GCTGATCGATCGTACGATCGATCGATCGATCGTAGCTAGCTAGCTAGCATCGATCGATCGATC"
    seq = (unit * 50)[:3000]
    return f">NC_000913.3 Escherichia coli str. K-12 substr. MG1655\n{seq}"


# ============================================================================
# 1. High-Level Lossless Round-Trip & Benchmark Tests (1 KB, 10 KB, 100 KB)
# ============================================================================

@pytest.mark.parametrize("payload_size_kb", [1, 10, 100])
def test_lossless_round_trip_binary_payloads(
    payload_size_kb: int,
    secret_passphrase: str,
    carrier_fasta_record: str,
) -> None:
    """
    Asserts bit-for-bit lossless extraction of 1 KB, 10 KB, and 100 KB arbitrary binary payloads
    and verifies strict biological viability compliance (Zero homopolymers >= 3, GC 40-60%, No stop codons).
    """
    raw_bytes = os.urandom(payload_size_kb * 1024)
    engine = DNASteganographyEngine(passphrase=secret_passphrase)

    # 1. Conceal into carrier
    stego_seq, report = engine.conceal(
        secret_data=raw_bytes,
        carrier_fasta=carrier_fasta_record,
        locus="center",
    )

    # 2. Extract and verify bit-for-bit identity
    extracted_bytes = engine.extract(stego_seq)
    assert extracted_bytes == raw_bytes, f"Fidelity mismatch for {payload_size_kb} KB payload!"

    # 3. Verify biological constraints
    assert report.is_viable is True, f"Viability failed: {report.diagnostic_messages}"
    assert report.max_homopolymer_run <= 2, f"Homopolymer violation: max run {report.max_homopolymer_run} > 2"
    assert len(report.homopolymer_violations) == 0, f"Found {len(report.homopolymer_violations)} homopolymer violations"
    assert 40.0 <= report.gc_percent <= 60.0, f"GC content {report.gc_percent}% out of bounds [40%, 60%]"
    assert sum(len(v) for v in report.in_frame_stop_codons.values()) == 0, "Accidental in-frame stop codons detected"
    assert report.shannon_entropy >= 1.85, f"Shannon entropy too low: {report.shannon_entropy:.4f}"


def test_lossless_text_and_unicode_payloads(secret_passphrase: str) -> None:
    """Tests various textual, empty, boundary, and Unicode payloads."""
    test_cases = [
        b"",
        b"X",
        b"BioCrypt-DNA: Next-generation in-silico genetic steganography.",
        "Synthetically engineered nucleotide data: \u03b1\u03b2\u03b3-\u03c0\u221e \u2705 \U0001F9EC".encode("utf-8"),
        b"\x00" * 256,
        b"\xff" * 256,
        bytes(range(256)) * 4,
    ]

    engine = DNASteganographyEngine(passphrase=secret_passphrase)
    for sample in test_cases:
        stego, report = engine.conceal(sample)
        recovered = engine.extract(stego)
        assert recovered == sample, f"Failed round-trip for sample: {sample!r}"
        assert report.max_homopolymer_run <= 2
        assert sum(len(v) for v in report.in_frame_stop_codons.values()) == 0


# ============================================================================
# 2. Cryptographic Security & Integrity Tests
# ============================================================================

def test_crypto_wrong_password_fails(secret_passphrase: str) -> None:
    """Verifies that an incorrect passphrase raises AuthenticationError."""
    engine_correct = DNASteganographyEngine(passphrase=secret_passphrase)
    engine_wrong = DNASteganographyEngine(passphrase="IncorrectPassword999!")

    secret = b"Confidential clinical research records."
    stego, _ = engine_correct.conceal(secret)

    with pytest.raises(AuthenticationError):
        engine_wrong.extract(stego)


def test_crypto_tampered_ciphertext_fails(secret_passphrase: str) -> None:
    """Verifies that tampering with ciphertext triggers ChecksumMismatchError or AuthenticationError."""
    crypto = CryptoEngine(secret_passphrase)
    payload = b"Immutable cryptographic payload."
    framed = crypto.encrypt_and_pack(payload)

    # Tamper with a byte in the ciphertext region (after 56-byte header)
    tampered = bytearray(framed)
    tampered[58] ^= 0x42

    with pytest.raises((ChecksumMismatchError, AuthenticationError)):
        crypto.unpack_and_decrypt(bytes(tampered))


def test_crypto_corrupted_header_fails(secret_passphrase: str) -> None:
    """Verifies that corrupting the magic bytes raises InvalidMagicError."""
    crypto = CryptoEngine(secret_passphrase)
    payload = b"Important payload"
    framed = bytearray(crypto.encrypt_and_pack(payload))

    # Overwrite magic bytes
    framed[:4] = b"XXXX"
    with pytest.raises(InvalidMagicError):
        crypto.unpack_and_decrypt(bytes(framed))

    # Truncated header
    with pytest.raises(HeaderCorruptError):
        crypto.unpack_and_decrypt(bytes(framed[:30]))


# ============================================================================
# 3. Transducer & FSM Biological Constraint Tests
# ============================================================================

def test_transducer_fsm_zero_homopolymers() -> None:
    """
    Verifies that the 9-state boundary-aware FSM strictly prevents runs > 2
    for challenging repeated bit patterns (e.g. 0x00, 0xFF, 0x55, 0xAA).
    """
    transducer = Transducer()
    for byte_val in [0x00, 0x11, 0x55, 0xAA, 0xFF]:
        raw = bytes([byte_val] * 1000)
        dna = transducer.encode(raw)

        # Check maximum run length
        max_run = BiologicalMetrics.get_max_run_length(dna)
        assert max_run <= 2, f"Homopolymer violation on 0x{byte_val:02x}: max run = {max_run}"

        # Check in-frame stop codons
        in_frame_stops, _ = BiologicalMetrics.scan_stop_codons(dna)
        assert sum(len(v) for v in in_frame_stops.values()) == 0

        # Lossless decode
        recovered = transducer.decode(dna)
        assert recovered == raw


def test_transducer_invalid_codon_raises() -> None:
    """Verifies that an unknown or out-of-alphabet codon raises TransductionError."""
    transducer = Transducer()
    # AAA is a 3-homopolymer and strictly excluded from all FSM states
    invalid_dna = "AAACGACTACGACTA"
    with pytest.raises(TransductionError):
        transducer.decode(invalid_dna)


# ============================================================================
# 4. Carrier & In-Silico PCR Tests
# ============================================================================

def test_carrier_insertion_loci(secret_passphrase: str) -> None:
    """Verifies center, append, and custom index locus embeddings."""
    carrier = CarrierEngine()
    dummy = carrier.generate_dummy_carrier(length=1000).sequence
    payload = "ACGACTACGACTACGACT"

    # Center insertion
    center_stego, c_idx = carrier.embed_into_carrier(dummy, payload, locus="center")
    assert c_idx == 500
    assert carrier.extract_from_carrier(center_stego) == payload

    # Append insertion
    append_stego, a_idx = carrier.embed_into_carrier(dummy, payload, locus="append")
    assert a_idx == 1000
    assert carrier.extract_from_carrier(append_stego) == payload

    # Coordinate index insertion
    idx_stego, i_idx = carrier.embed_into_carrier(dummy, payload, locus=250)
    assert i_idx == 250
    assert carrier.extract_from_carrier(idx_stego) == payload


def test_carrier_missing_primer_raises() -> None:
    """Verifies that missing forward or reverse primer raises PrimerNotFoundError."""
    carrier = CarrierEngine()
    dummy_seq = "GCTGATCGATCGTACGATCGATCGATCGATCGTAGCTAGCTAGCTA"

    with pytest.raises(PrimerNotFoundError):
        carrier.extract_from_carrier(dummy_seq)


def test_ncbi_fasta_wrapping() -> None:
    """Verifies NCBI standard 80-character line wrapping."""
    seq = "A" * 200
    fasta = CarrierEngine.write_fasta("test_header", seq, line_width=80)
    lines = fasta.strip().split("\n")
    assert lines[0] == ">test_header"
    assert len(lines[1]) == 80
    assert len(lines[2]) == 80
    assert len(lines[3]) == 40


# ============================================================================
# 5. CLI End-to-End Execution Tests
# ============================================================================

def test_cli_full_workflow() -> None:
    """Simulates the full CLI workflow: embed -> audit -> simulate-pcr -> extract."""
    runner = CliRunner()
    password = "MasterCLISecret2026!#"

    with tempfile.TemporaryDirectory() as tmpdir:
        input_file = os.path.join(tmpdir, "secret.txt")
        carrier_file = os.path.join(tmpdir, "carrier.fasta")
        stego_file = os.path.join(tmpdir, "stego.fasta")
        recovered_file = os.path.join(tmpdir, "recovered.txt")

        secret_text = "CONFIDENTIAL: Bio-Computing Protocol Initiated at Lat 22.307 N."
        with open(input_file, "w", encoding="utf-8") as f:
            f.write(secret_text)

        # Create carrier FASTA
        carrier_seq = "GCTGATCGATCGTACGATCGATCGATCGATCGTAGCTAGCTAGCTAGCATCGATCGATCGATC" * 20
        CarrierEngine.write_fasta("host_genome", carrier_seq, output_path=carrier_file)

        # 1. CLI Embed
        res_embed = runner.invoke(
            cli,
            ["embed", "-i", input_file, "-c", carrier_file, "-o", stego_file, "-p", password],
        )
        assert res_embed.exit_code == 0, f"Embed failed: {res_embed.output}"
        assert os.path.exists(stego_file)

        # 2. CLI Audit
        res_audit = runner.invoke(cli, ["audit", "-c", stego_file])
        assert res_audit.exit_code == 0, f"Audit failed: {res_audit.output}"
        assert "Global GC Content" in res_audit.output

        # 3. CLI Simulate-PCR
        res_pcr = runner.invoke(cli, ["simulate-pcr", "-c", stego_file])
        assert res_pcr.exit_code == 0, f"Simulate PCR failed: {res_pcr.output}"
        assert "In-Silico Amplification Succeeded" in res_pcr.output

        # 4. CLI Extract
        res_extract = runner.invoke(
            cli,
            ["extract", "-c", stego_file, "-o", recovered_file, "-p", password],
        )
        assert res_extract.exit_code == 0, f"Extract failed: {res_extract.output}"
        assert os.path.exists(recovered_file)

        with open(recovered_file, "r", encoding="utf-8") as f:
            recovered_text = f.read()

        assert recovered_text == secret_text

