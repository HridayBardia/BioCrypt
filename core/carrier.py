"""
BioCrypt-DNA Carrier & In-Silico PCR Layer
==========================================
Handles NCBI-compliant FASTA I/O, synthetic primer flanking (amplicon generation),
genomic locus embedding, and in-silico PCR extraction.

Primers:
- Forward Primer (18 nt, 50% GC): 5'-ATCGTTAGGCTACGATCG-3'
- Reverse Primer (18 nt, 50% GC): 5'-CGATCGTAGCCTAACGAT-3'

NCBI Standard Formatting:
- Sequence line width wrapped to 80 characters.
- FASTA headers prefixed with '>'.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import List, Optional, Tuple, Union


DEFAULT_FWD_PRIMER: str = "ATCGTTAGGCTACGATCG"
DEFAULT_REV_PRIMER: str = "CGATCGTAGCCTAACGAT"
DEFAULT_LINE_WIDTH: int = 80


class CarrierError(Exception):
    """Base exception for carrier embedding and extraction errors."""


class PrimerNotFoundError(CarrierError):
    """Raised when in-silico PCR primers cannot be located in the carrier sequence."""


class FastaParseError(CarrierError):
    """Raised when parsing an invalid FASTA file."""


@dataclass
class FastaRecord:
    """Represents a single FASTA sequence record."""

    header: str
    sequence: str

    def format_fasta(self, line_width: int = DEFAULT_LINE_WIDTH) -> str:
        """Formats the record as standard NCBI FASTA text with wrapped lines."""
        lines = [f">{self.header.lstrip('>')}"]
        for i in range(0, len(self.sequence), line_width):
            lines.append(self.sequence[i : i + line_width])
        return "\n".join(lines) + "\n"


class CarrierEngine:
    """
    Manages genomic FASTA parsing, amplicon synthesis with flanking primers,
    locus-targeted insertion, and in-silico PCR payload extraction.
    """

    def __init__(
        self,
        fwd_primer: str = DEFAULT_FWD_PRIMER,
        rev_primer: str = DEFAULT_REV_PRIMER,
    ):
        self.fwd_primer = fwd_primer.upper()
        self.rev_primer = rev_primer.upper()

    # ------------------ FASTA I/O ------------------

    @staticmethod
    def read_fasta(source: Union[str, os.PathLike]) -> List[FastaRecord]:
        """
        Reads one or more records from a FASTA file path or FASTA-formatted string.

        Args:
            source: File path or raw FASTA text string.

        Returns:
            List of FastaRecord objects.
        """
        if isinstance(source, (str, os.PathLike)) and os.path.exists(str(source)):
            with open(source, "r", encoding="utf-8") as f:
                content = f.read()
        else:
            content = str(source)

        records: List[FastaRecord] = []
        current_header: Optional[str] = None
        current_seq_parts: List[str] = []

        for line in content.splitlines():
            line = line.strip()
            if not line:
                continue
            if line.startswith(">"):
                if current_header is not None:
                    records.append(
                        FastaRecord(
                            header=current_header,
                            sequence="".join(current_seq_parts).upper(),
                        )
                    )
                    current_seq_parts = []
                current_header = line[1:].strip()
            else:
                if current_header is None:
                    raise FastaParseError("FASTA sequence data encountered before header line.")
                # Filter to standard nucleotide characters, ignoring spaces
                clean_line = "".join(ch for ch in line if ch.isalpha()).upper()
                current_seq_parts.append(clean_line)

        if current_header is not None:
            records.append(
                FastaRecord(
                    header=current_header,
                    sequence="".join(current_seq_parts).upper(),
                )
            )

        if not records:
            raise FastaParseError("No valid FASTA records found in source.")

        return records

    @staticmethod
    def write_fasta(
        header: str,
        sequence: str,
        output_path: Optional[Union[str, os.PathLike]] = None,
        line_width: int = DEFAULT_LINE_WIDTH,
    ) -> str:
        """
        Generates NCBI standard FASTA string and optionally writes it to a file.

        Args:
            header: Header text (with or without '>').
            sequence: Nucleotide sequence string.
            output_path: Optional destination file path.
            line_width: Line wrap width (default 80).

        Returns:
            Formatted FASTA string.
        """
        record = FastaRecord(header=header, sequence=sequence)
        fasta_text = record.format_fasta(line_width=line_width)

        if output_path is not None:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(fasta_text)

        return fasta_text

    @staticmethod
    def generate_dummy_carrier(length: int = 2000, header: str = "synthetic_host_carrier") -> FastaRecord:
        """
        Generates a balanced synthetic carrier sequence when an external FASTA is not provided.
        """
        # Deterministic balanced 50% GC repeating sequence
        unit = "GCTGATCGATCGTACGATCGATCGATCGATCGTAGCTAGCTAGCTAGCATCGATCGATCGATC"
        repeats = (length // len(unit)) + 1
        seq = (unit * repeats)[:length]
        return FastaRecord(header=header, sequence=seq)

    # ------------------ In-Silico Amplicon & Insertion ------------------

    def assemble_amplicon(self, encoded_dna: str) -> str:
        """
        Synthesizes an amplicon by flanking the encoded DNA strand with
        forward and reverse primers.

        Structure:
        5'- [FWD_PRIMER (18 nt)] + [ENCODED_DNA] + [REV_PRIMER (18 nt)] -3'
        """
        return self.fwd_primer + encoded_dna.upper() + self.rev_primer

    def embed_into_carrier(
        self,
        carrier_sequence: str,
        encoded_dna: str,
        locus: Optional[Union[int, str]] = None,
    ) -> Tuple[str, int]:
        """
        Embeds the synthetic amplicon into a genomic carrier sequence.

        Embedding modes:
        - None / 'center': Injected into the genomic center of the carrier sequence.
        - 'append': Appended to the 3' terminus of the carrier sequence.
        - int: Inserted at the specified 0-based index locus.

        Args:
            carrier_sequence: Innocent host genomic sequence.
            encoded_dna: Bio-constrained payload strand.
            locus: Target insertion coordinate or mode.

        Returns:
            (stego_sequence, insertion_locus_index)
        """
        amplicon = self.assemble_amplicon(encoded_dna)
        seq_len = len(carrier_sequence)

        if locus is None or locus == "center":
            insert_idx = seq_len // 2
        elif locus == "append":
            insert_idx = seq_len
        elif isinstance(locus, int):
            if locus < 0 or locus > seq_len:
                raise ValueError(
                    f"Insertion locus index {locus} out of bounds for sequence length {seq_len}."
                )
            insert_idx = locus
        else:
            raise ValueError(f"Invalid locus mode: {locus!r}. Choose 'center', 'append', or an integer index.")

        stego_seq = (
            carrier_sequence[:insert_idx]
            + amplicon
            + carrier_sequence[insert_idx:]
        )
        return stego_seq, insert_idx

    def extract_from_carrier(self, stego_sequence: str) -> str:
        """
        Performs in-silico PCR extraction by annealing forward and reverse primers
        and extracting the inner bio-constrained payload strand.

        Args:
            stego_sequence: Full carrier sequence containing the hidden amplicon.

        Returns:
            Extracted encoded DNA payload strand.

        Raises:
            PrimerNotFoundError: If forward or reverse primer cannot be located in order.
        """
        clean_seq = "".join(ch for ch in stego_sequence if ch.isalpha()).upper()

        fwd_idx = clean_seq.find(self.fwd_primer)
        if fwd_idx == -1:
            raise PrimerNotFoundError(
                f"Forward primer motif ({self.fwd_primer}) not found in target sequence."
            )

        payload_start = fwd_idx + len(self.fwd_primer)
        rev_idx = clean_seq.find(self.rev_primer, payload_start)
        if rev_idx == -1:
            raise PrimerNotFoundError(
                f"Reverse primer motif ({self.rev_primer}) not found downstream of forward primer."
            )

        return clean_seq[payload_start:rev_idx]

