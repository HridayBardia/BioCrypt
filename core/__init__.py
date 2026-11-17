"""
BioCrypt-DNA Core Package
=========================
A production-grade DNA Steganography and Data Hiding System.

Four-stage pipeline:
1. Crypto Layer (AES-256-GCM + PBKDF2 + zlib level 9 + CRC-32)
2. Framing & Header Layer (Deterministic binary packaging)
3. Bio-Constrained Transduction Engine (9-state boundary-aware FSM)
4. Steganographic Carrier Embedder (Synthetic primer flanking & genomic insertion)
"""

from __future__ import annotations

from typing import Optional, Tuple, Union

from .carrier import (
    CarrierEngine,
    CarrierError,
    FastaParseError,
    FastaRecord,
    PrimerNotFoundError,
)
from .crypto import (
    AuthenticationError,
    ChecksumMismatchError,
    CryptoEngine,
    CryptoError,
    HeaderCorruptError,
    InvalidMagicError,
)
from .metrics import (
    BiologicalMetrics,
    HomopolymerViolation,
    ViabilityReport,
)
from .transducer import (
    BioConstrainedCodec,
    Transducer,
    TransductionError,
)


class DNASteganographyEngine:
    """
    High-level facade orchestrating the 4-stage DNA steganography pipeline:
    Cryptographic Layering -> Binary Framing -> Bio-Constrained Transduction -> Carrier Embedding.
    """

    def __init__(
        self,
        passphrase: str,
        fwd_primer: Optional[str] = None,
        rev_primer: Optional[str] = None,
    ):
        self.crypto = CryptoEngine(passphrase)
        self.transducer = Transducer()
        if fwd_primer and rev_primer:
            self.carrier = CarrierEngine(fwd_primer=fwd_primer, rev_primer=rev_primer)
        else:
            self.carrier = CarrierEngine()

    def conceal(
        self,
        secret_data: Union[bytes, str],
        carrier_fasta: Optional[str] = None,
        locus: Optional[Union[int, str]] = "center",
    ) -> Tuple[str, ViabilityReport]:
        """
        Conceals arbitrary secret bytes or text inside a genomic carrier FASTA sequence.

        Args:
            secret_data: Raw bytes or string to conceal.
            carrier_fasta: Innocent host carrier sequence (or FASTA text). If None,
                           a balanced synthetic carrier is generated automatically.
            locus: Insertion position ('center', 'append', or integer index).

        Returns:
            (stego_fasta_sequence, payload_viability_report)
        """
        if isinstance(secret_data, str):
            payload_bytes = secret_data.encode("utf-8")
        else:
            payload_bytes = bytes(secret_data)

        # 1. Cryptographic packaging: zlib + AES-256-GCM + CRC32 + Framing
        framed_data = self.crypto.encrypt_and_pack(payload_bytes)

        # 2. Bio-constrained transduction: 5-bit to 3-nucleotide FSM
        dna_payload = self.transducer.encode(framed_data)

        # 3. Viability audit on the generated payload strand
        report = BiologicalMetrics.audit_sequence(dna_payload)

        # 4. Resolve carrier sequence
        if carrier_fasta is None or not carrier_fasta.strip():
            carrier_seq = self.carrier.generate_dummy_carrier(
                length=max(2000, len(dna_payload) * 2)
            ).sequence
        else:
            # Parse if FASTA format, else use raw sequence
            if ">" in carrier_fasta:
                records = self.carrier.read_fasta(carrier_fasta)
                carrier_seq = records[0].sequence
            else:
                carrier_seq = "".join(ch for ch in carrier_fasta if ch.isalpha()).upper()

        # 5. Embed amplicon (FWD_PRIMER + dna_payload + REV_PRIMER) into carrier
        stego_seq, _ = self.carrier.embed_into_carrier(carrier_seq, dna_payload, locus=locus)

        return stego_seq, report

    def extract(self, stego_fasta: str) -> bytes:
        """
        Extracts and decrypts secret data from a stego FASTA sequence or file.

        Args:
            stego_fasta: Carrier sequence containing the hidden amplicon.

        Returns:
            Original secret bytes with 100% lossless fidelity.
        """
        # 1. Parse sequence from FASTA if necessary
        if ">" in stego_fasta:
            records = self.carrier.read_fasta(stego_fasta)
            seq = records[0].sequence
        else:
            seq = "".join(ch for ch in stego_fasta if ch.isalpha()).upper()

        # 2. In-silico PCR primer annealing & extraction
        extracted_dna = self.carrier.extract_from_carrier(seq)

        # 3. Inverse transduction: Codon FSM -> framed binary stream
        framed_data = self.transducer.decode(extracted_dna)

        # 4. Unpack, verify CRC-32, authenticate AES-GCM tag, decompress zlib
        secret_bytes = self.crypto.unpack_and_decrypt(framed_data)

        return secret_bytes


__all__ = [
    "DNASteganographyEngine",
    "CryptoEngine",
    "CryptoError",
    "InvalidMagicError",
    "HeaderCorruptError",
    "ChecksumMismatchError",
    "AuthenticationError",
    "Transducer",
    "BioConstrainedCodec",
    "TransductionError",
    "CarrierEngine",
    "CarrierError",
    "PrimerNotFoundError",
    "FastaParseError",
    "FastaRecord",
    "BiologicalMetrics",
    "ViabilityReport",
    "HomopolymerViolation",
]

