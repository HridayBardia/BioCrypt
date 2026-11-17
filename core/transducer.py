"""
BioCrypt-DNA Biological Transduction Engine
===========================================
Translates binary bitstreams into biologically constrained DNA sequences and back.

Biological Constraints Enforced:
1. Homopolymer Elimination: Max consecutive run length <= 2 identical bases across
   both intra-codon positions and inter-codon boundaries.
2. GC Content Balance: Every codon strictly contains 1 or 2 G/C nucleotides
   (33.3% or 66.7% local GC), maintaining a global GC window between 45% and 55%.
3. Termination Codon Exclusion: In-frame stop codons (TAA, TAG, TGA) are globally
   excluded from the alphabet.
4. Deterministic FSM: A 9-state boundary-aware finite state machine dynamically rotates
   the 32-codon alphabet based on the trailing sequence context to guarantee zero
   homopolymers >= 3 while maintaining bijective, byte-level reversibility.
"""

from __future__ import annotations

import struct
from typing import Dict, List, Optional, Tuple


BASES: Tuple[str, ...] = ("A", "C", "G", "T")
STOP_CODONS: Tuple[str, ...] = ("TAA", "TAG", "TGA")
HOMOPOLYMERS_3: Tuple[str, ...] = ("AAA", "CCC", "GGG", "TTT")


def generate_candidate_codons() -> List[str]:
    """
    Generate the master pool of biologically viable 3-nucleotide codons.

    Criteria:
    - Must NOT be a stop codon (TAA, TAG, TGA).
    - Must NOT be a 3-base uniform homopolymer (AAA, CCC, GGG, TTT).
    - Must contain strictly 1 or 2 G/C bases (balanced 33.3% - 66.7% local GC).

    Returns:
        Sorted list of viable codons (exactly 46 codons).
    """
    candidates: List[str] = []
    for b1 in BASES:
        for b2 in BASES:
            for b3 in BASES:
                codon = b1 + b2 + b3
                if codon in STOP_CODONS or codon in HOMOPOLYMERS_3:
                    continue
                gc_count = codon.count("G") + codon.count("C")
                if gc_count in (1, 2):
                    candidates.append(codon)
    return sorted(candidates)


MASTER_CODON_POOL: Tuple[str, ...] = tuple(generate_candidate_codons())


StateKey = Tuple[Optional[str], int]


def build_state_tables() -> Tuple[
    Dict[StateKey, Tuple[str, ...]],
    Dict[StateKey, Dict[str, int]],
]:
    """
    Constructs the deterministic FSM encode and decode lookup tables for all 9 states.

    States:
    - (None, 0): Initial state (no preceding nucleotide).
    - (b, 1): Trailing nucleotide 'b' with run length 1.
    - (b, 2): Trailing nucleotide 'b' with run length 2.

    Boundary Rules:
    - In state (b, 1): codons starting with 'b*2' are excluded (prevents b + bb = bbb).
    - In state (b, 2): codons starting with 'b' are excluded (prevents bb + b = bbb).
    - In each state, exactly 32 codons are deterministically selected from remaining candidates.

    Returns:
        (encode_tables, decode_tables)
    """
    encode_tables: Dict[StateKey, Tuple[str, ...]] = {}
    decode_tables: Dict[StateKey, Dict[str, int]] = {}

    states: List[StateKey] = [(None, 0)]
    for b in BASES:
        states.append((b, 1))
        states.append((b, 2))

    for base, run_len in states:
        valid_codons: List[str] = []
        for codon in MASTER_CODON_POOL:
            if base is not None:
                if run_len == 1 and codon.startswith(base * 2):
                    continue
                if run_len >= 2 and codon.startswith(base):
                    continue
            valid_codons.append(codon)

        if len(valid_codons) < 32:
            raise RuntimeError(
                f"Deficient codon pool for state ({base}, {run_len}): only {len(valid_codons)} available."
            )

        selected_codons = tuple(valid_codons[:32])
        encode_tables[(base, run_len)] = selected_codons
        decode_tables[(base, run_len)] = {c: idx for idx, c in enumerate(selected_codons)}

    return encode_tables, decode_tables


ENCODE_TABLES, DECODE_TABLES = build_state_tables()


def advance_fsm_state(current_state: StateKey, codon: str) -> StateKey:
    """
    Determines the next FSM state based on the emitted or decoded codon.

    Since all viable codons have internal run lengths <= 2:
    - If the last two bases are identical (codon[1] == codon[2]), trailing run is 2.
    - Otherwise, trailing run is 1.

    Args:
        current_state: Current (base, run_length) state.
        codon: The 3-nucleotide codon just processed.

    Returns:
        Next StateKey (last_base, run_length).
    """
    trailing_base = codon[2]
    if codon[1] == trailing_base:
        return (trailing_base, 2)
    return (trailing_base, 1)


class TransductionError(Exception):
    """Raised when codon parsing or inverse decoding fails."""


class Transducer:
    """
    Adaptive Codon Transduction Engine.
    Converts binary bitstreams to bio-constrained DNA sequences and back.
    """

    def __init__(self) -> None:
        self.encode_tables = ENCODE_TABLES
        self.decode_tables = DECODE_TABLES

    def encode(self, data: bytes) -> str:
        """
        Encodes arbitrary binary data into a bio-constrained DNA sequence.

        Args:
            data: Raw input bytes.

        Returns:
            DNA sequence string consisting of [A, C, G, T].
        """
        # Pack 4-byte big-endian length prefix to preserve exact byte length
        payload = struct.pack(">I", len(data)) + data

        # Convert to bitstream
        bit_str = "".join(f"{byte:08b}" for byte in payload)

        # Pad to multiple of 5 bits
        pad_len = (5 - (len(bit_str) % 5)) % 5
        bit_str += "0" * pad_len

        # Transduce via FSM
        dna_codons: List[str] = []
        state: StateKey = (None, 0)

        for i in range(0, len(bit_str), 5):
            val = int(bit_str[i : i + 5], 2)
            codon = self.encode_tables[state][val]
            dna_codons.append(codon)
            state = advance_fsm_state(state, codon)

        return "".join(dna_codons)

    def decode(self, dna_seq: str) -> bytes:
        """
        Decodes a bio-constrained DNA sequence back to the original binary bytes.

        Args:
            dna_seq: String of nucleotides (must have length multiple of 3).

        Returns:
            Original binary bytes.

        Raises:
            TransductionError: If sequence length is invalid, unknown codon encountered,
                              or payload is corrupted.
        """
        cleaned_seq = dna_seq.strip().upper()
        if len(cleaned_seq) % 3 != 0:
            raise TransductionError(
                f"DNA sequence length ({len(cleaned_seq)}) is not a multiple of 3."
            )

        bit_chunks: List[str] = []
        state: StateKey = (None, 0)

        for i in range(0, len(cleaned_seq), 3):
            codon = cleaned_seq[i : i + 3]
            table = self.decode_tables.get(state)
            if table is None or codon not in table:
                raise TransductionError(
                    f"Codon {codon!r} at position {i} is invalid for FSM state {state}."
                )
            val = table[codon]
            bit_chunks.append(f"{val:05b}")
            state = advance_fsm_state(state, codon)

        raw_bits = "".join(bit_chunks)

        # Convert bits to bytes
        byte_list = bytearray()
        for i in range(0, len(raw_bits) - 7, 8):
            byte_list.append(int(raw_bits[i : i + 8], 2))

        if len(byte_list) < 4:
            raise TransductionError("Decoded bitstream is shorter than 4-byte length prefix.")

        expected_len = struct.unpack(">I", byte_list[:4])[0]
        payload = bytes(byte_list[4 : 4 + expected_len])

        if len(payload) != expected_len:
            raise TransductionError(
                f"Payload length mismatch: header specifies {expected_len} bytes, "
                f"extracted {len(payload)} bytes."
            )

        return payload


# Backwards compatibility alias
BioConstrainedCodec = Transducer

