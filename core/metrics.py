"""
BioCrypt-DNA Biological Metrics & Viability Auditor
===================================================
Provides comprehensive biophysical and computational diagnostics for DNA sequences:
1. GC-Content Analysis: Overall and sliding-window GC percentages.
2. Homopolymer Detection: Flags any consecutive identical nucleotide run >= 3.
3. Shannon Entropy: Quantifies information density and randomness ($H = -\\sum p \\log_2 p$).
4. Termination Codon Audit: Scans for premature translation arrest codons (TAA, TAG, TGA)
   both in-frame (reading frame 0) and across sliding 3-mer windows.
5. Melting Temperature (Tm): Wallace rule estimation for primer & sequence stability.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Dict, List, Tuple


STOP_CODONS: Tuple[str, ...] = ("TAA", "TAG", "TGA")
STANDARD_BASES: Tuple[str, ...] = ("A", "C", "G", "T")


@dataclass
class HomopolymerViolation:
    """Represents a homopolymer violation where run length exceeds threshold."""

    base: str
    run_length: int
    start_index: int


@dataclass
class ViabilityReport:
    """Comprehensive biological audit scorecard for a DNA sequence."""

    sequence_length: int
    gc_percent: float
    sliding_gc_min: float
    sliding_gc_max: float
    sliding_gc_mean: float
    shannon_entropy: float
    max_homopolymer_run: int
    homopolymer_violations: List[HomopolymerViolation]
    in_frame_stop_codons: Dict[str, List[int]]
    sliding_stop_codons: Dict[str, List[int]]
    melting_temperature_tm: float
    is_viable: bool
    diagnostic_messages: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, object]:
        """Convert report to dictionary representation."""
        return {
            "sequence_length": self.sequence_length,
            "gc_percent": round(self.gc_percent, 2),
            "sliding_gc_min": round(self.sliding_gc_min, 2),
            "sliding_gc_max": round(self.sliding_gc_max, 2),
            "sliding_gc_mean": round(self.sliding_gc_mean, 2),
            "shannon_entropy": round(self.shannon_entropy, 4),
            "max_homopolymer_run": self.max_homopolymer_run,
            "homopolymer_violations_count": len(self.homopolymer_violations),
            "in_frame_stops_count": sum(len(v) for v in self.in_frame_stop_codons.values()),
            "sliding_stops_count": sum(len(v) for v in self.sliding_stop_codons.values()),
            "melting_temperature_tm": round(self.melting_temperature_tm, 2),
            "is_viable": self.is_viable,
            "diagnostic_messages": self.diagnostic_messages,
        }


class BiologicalMetrics:
    """Biophysical metrics calculator and auditing engine."""

    @staticmethod
    def calc_gc_content(sequence: str) -> float:
        """
        Calculates GC content percentage: (G + C) / Length * 100.
        """
        seq = sequence.upper()
        if not seq:
            return 0.0
        gc_count = seq.count("G") + seq.count("C")
        return (gc_count / len(seq)) * 100.0

    @staticmethod
    def calc_sliding_window_gc(
        sequence: str,
        window_size: int = 50,
        step: int = 10,
    ) -> List[float]:
        """
        Calculates GC percentage across sliding windows.
        If sequence is shorter than window_size, returns single GC value.
        """
        seq = sequence.upper()
        if len(seq) <= window_size:
            return [BiologicalMetrics.calc_gc_content(seq)]

        values: List[float] = []
        for i in range(0, len(seq) - window_size + 1, step):
            win = seq[i : i + window_size]
            values.append(BiologicalMetrics.calc_gc_content(win))

        return values if values else [BiologicalMetrics.calc_gc_content(seq)]

    @staticmethod
    def calc_shannon_entropy(sequence: str) -> float:
        """
        Calculates Shannon Entropy (bits per nucleotide):
        H = - sum(p * log2(p)) over nucleotide frequencies.
        Maximum theoretical entropy for 4 equiprobable bases is 2.0 bits.
        """
        seq = sequence.upper()
        if not seq:
            return 0.0

        length = len(seq)
        counts = {b: seq.count(b) for b in STANDARD_BASES}
        entropy = 0.0
        for b, count in counts.items():
            if count > 0:
                p = count / length
                entropy -= p * math.log2(p)

        return entropy

    @staticmethod
    def detect_homopolymers(sequence: str, max_run: int = 2) -> List[HomopolymerViolation]:
        """
        Detects consecutive identical nucleotide runs exceeding max_run (default > 2, i.e. >= 3).
        """
        seq = sequence.upper()
        violations: List[HomopolymerViolation] = []
        if not seq:
            return violations

        cur_base = seq[0]
        cur_len = 1
        start_idx = 0

        for i in range(1, len(seq)):
            if seq[i] == cur_base:
                cur_len += 1
            else:
                if cur_len > max_run:
                    violations.append(
                        HomopolymerViolation(
                            base=cur_base,
                            run_length=cur_len,
                            start_index=start_idx,
                        )
                    )
                cur_base = seq[i]
                cur_len = 1
                start_idx = i

        if cur_len > max_run:
            violations.append(
                HomopolymerViolation(
                    base=cur_base,
                    run_length=cur_len,
                    start_index=start_idx,
                )
            )

        return violations

    @staticmethod
    def get_max_run_length(sequence: str) -> int:
        """Finds the maximum run length of any consecutive identical base in the sequence."""
        seq = sequence.upper()
        if not seq:
            return 0
        max_run = 1
        cur_run = 1
        for i in range(1, len(seq)):
            if seq[i] == seq[i - 1]:
                cur_run += 1
                if cur_run > max_run:
                    max_run = cur_run
            else:
                cur_run = 1
        return max_run

    @staticmethod
    def scan_stop_codons(sequence: str) -> Tuple[Dict[str, List[int]], Dict[str, List[int]]]:
        """
        Scans sequence for termination codons (TAA, TAG, TGA).

        Returns:
            (in_frame_stops, sliding_window_stops)
            where each is a dict: {'TAA': [pos, ...], 'TAG': [...], 'TGA': [...]}
        """
        seq = sequence.upper()
        in_frame: Dict[str, List[int]] = {s: [] for s in STOP_CODONS}
        sliding: Dict[str, List[int]] = {s: [] for s in STOP_CODONS}

        # 1. In-frame stops (steps of 3 from index 0)
        for i in range(0, len(seq) - 2, 3):
            triplet = seq[i : i + 3]
            if triplet in in_frame:
                in_frame[triplet].append(i)

        # 2. Sliding window stops (every single 3-mer)
        for i in range(len(seq) - 2):
            triplet = seq[i : i + 3]
            if triplet in sliding:
                sliding[triplet].append(i)

        return in_frame, sliding

    @staticmethod
    def estimate_melting_temp(sequence: str) -> float:
        """
        Estimates melting temperature (Tm in deg C) using the Wallace / Marmur formula:
        Tm = 64.9 + 41 * (G + C - 16.4) / (A + T + G + C).
        For short oligonucleotides (< 14 nt): Wallace rule 2*(A+T) + 4*(G+C).
        """
        seq = sequence.upper()
        total_bases = sum(seq.count(b) for b in STANDARD_BASES)
        if total_bases == 0:
            return 0.0

        gc = seq.count("G") + seq.count("C")
        at = seq.count("A") + seq.count("T")

        if total_bases < 14:
            return float(2 * at + 4 * gc)

        tm = 64.9 + 41.0 * (gc - 16.4) / total_bases
        return tm

    @classmethod
    def audit_sequence(
        cls,
        sequence: str,
        gc_min: float = 40.0,
        gc_max: float = 60.0,
        max_homopolymer_allowed: int = 2,
    ) -> ViabilityReport:
        """
        Executes a complete biological audit scorecard on a candidate sequence.

        Args:
            sequence: Nucleotide sequence to audit.
            gc_min: Minimum acceptable GC% (default 40.0%).
            gc_max: Maximum acceptable GC% (default 60.0%).
            max_homopolymer_allowed: Maximum acceptable repeat run (default 2).

        Returns:
            ViabilityReport containing metrics, viability status, and diagnostics.
        """
        clean_seq = "".join(ch for ch in sequence if ch.isalpha()).upper()
        length = len(clean_seq)

        gc = cls.calc_gc_content(clean_seq)
        sliding_gc = cls.calc_sliding_window_gc(clean_seq, window_size=50, step=10)
        s_min = min(sliding_gc) if sliding_gc else gc
        s_max = max(sliding_gc) if sliding_gc else gc
        s_mean = sum(sliding_gc) / len(sliding_gc) if sliding_gc else gc

        entropy = cls.calc_shannon_entropy(clean_seq)
        max_run = cls.get_max_run_length(clean_seq)
        violations = cls.detect_homopolymers(clean_seq, max_run=max_homopolymer_allowed)
        in_frame_stops, sliding_stops = cls.scan_stop_codons(clean_seq)
        tm = cls.estimate_melting_temp(clean_seq)

        diagnostics: List[str] = []
        is_viable = True

        # Check GC
        if not (gc_min <= gc <= gc_max):
            diagnostics.append(f"GC content ({gc:.1f}%) outside viable window [{gc_min}%, {gc_max}%].")
            is_viable = False

        # Check homopolymers
        if violations:
            diagnostics.append(f"{len(violations)} homopolymer violation(s) found (max run: {max_run}).")
            is_viable = False

        # Check in-frame stop codons
        total_in_frame_stops = sum(len(v) for v in in_frame_stops.values())
        if total_in_frame_stops > 0:
            diagnostics.append(f"{total_in_frame_stops} in-frame stop codon(s) detected.")
            is_viable = False

        if not diagnostics:
            diagnostics.append("Sequence fully complies with all biological viability constraints.")

        return ViabilityReport(
            sequence_length=length,
            gc_percent=gc,
            sliding_gc_min=s_min,
            sliding_gc_max=s_max,
            sliding_gc_mean=s_mean,
            shannon_entropy=entropy,
            max_homopolymer_run=max_run,
            homopolymer_violations=violations,
            in_frame_stop_codons=in_frame_stops,
            sliding_stop_codons=sliding_stops,
            melting_temperature_tm=tm,
            is_viable=is_viable,
            diagnostic_messages=diagnostics,
        )

