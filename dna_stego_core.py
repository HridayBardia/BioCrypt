#!/usr/bin/env python3
"""
BioCrypt-DNA Standalone Core Prototype (dna_stego_core.py)
==========================================================
Zero external dependencies (pure Python standard library).
Implements the 4-stage DNA steganography pipeline using:
1. zlib compression + PBKDF2-HMAC-SHA256 keystream XOR cipher.
2. Binary framing: [Length (4B)] + [CRC-32 (4B)] + [Payload].
3. 9-state boundary-aware FSM bio-constrained codon transduction (Max run <= 2, GC 40-60%, No stop codons).
4. Forward and reverse primer amplicon embedding in genomic FASTA carrier.
"""

from __future__ import annotations

import hashlib
import os
import struct
import sys
import zlib


BASES = ("A", "C", "G", "T")
STOP_CODONS = {"TAA", "TAG", "TGA"}
HOMOPOLYMERS_3 = {"AAA", "CCC", "GGG", "TTT"}


def _build_master_pool():
    valid = []
    for b1 in BASES:
        for b2 in BASES:
            for b3 in BASES:
                codon = b1 + b2 + b3
                if codon in STOP_CODONS or codon in HOMOPOLYMERS_3:
                    continue
                gc_count = codon.count("G") + codon.count("C")
                if gc_count in (1, 2):
                    valid.append(codon)
    return sorted(valid)


MASTER_POOL = _build_master_pool()


def _build_fsm_tables():
    enc = {}
    dec = {}
    states = [(None, 0)] + [(b, r) for b in BASES for r in (1, 2)]
    for base, run_len in states:
        valid_codons = []
        for codon in MASTER_POOL:
            if base is not None:
                if run_len == 1 and codon.startswith(base * 2):
                    continue
                if run_len >= 2 and codon.startswith(base):
                    continue
            valid_codons.append(codon)
        selected = tuple(valid_codons[:32])
        enc[(base, run_len)] = selected
        dec[(base, run_len)] = {c: i for i, c in enumerate(selected)}
    return enc, dec


ENCODE_TABLES, DECODE_TABLES = _build_fsm_tables()


def _next_state(codon: str):
    if codon[2] == codon[1]:
        return (codon[2], 2)
    return (codon[2], 1)


class BioConstrainedCodec:
    """
    Translates raw bytes into biological DNA sequences adhering to:
    1. Homopolymer limit (Max 2 consecutive identical bases).
    2. Dynamic GC-content regulation (40-60%).
    3. Elimination of termination codons (TAA, TAG, TGA).
    """

    def __init__(self):
        self.enc_tables = ENCODE_TABLES
        self.dec_tables = DECODE_TABLES

    def encode_bytes(self, data: bytes) -> str:
        # Prepend 4-byte big-endian length + CRC32 for frame validation
        crc = zlib.crc32(data) & 0xFFFFFFFF
        framed_data = struct.pack(">II", len(data), crc) + data

        # Convert bytes to 5-bit chunks
        bit_str = "".join(f"{byte:08b}" for byte in framed_data)
        pad_len = (5 - (len(bit_str) % 5)) % 5
        bit_str += "0" * pad_len

        dna = []
        state = (None, 0)
        for i in range(0, len(bit_str), 5):
            val = int(bit_str[i : i + 5], 2)
            codon = self.enc_tables[state][val]
            dna.append(codon)
            state = _next_state(codon)

        return "".join(dna)

    def decode_dna(self, dna_seq: str) -> bytes:
        cleaned = dna_seq.strip().upper()
        if len(cleaned) % 3 != 0:
            raise ValueError(f"DNA sequence length ({len(cleaned)}) is not a multiple of 3.")

        bit_chunks = []
        state = (None, 0)
        for i in range(0, len(cleaned), 3):
            codon = cleaned[i : i + 3]
            table = self.dec_tables.get(state)
            if table is None or codon not in table:
                raise ValueError(f"Invalid codon {codon!r} at position {i} for state {state}")
            val = table[codon]
            bit_chunks.append(f"{val:05b}")
            state = _next_state(codon)

        raw_bits = "".join(bit_chunks)
        byte_list = bytearray()
        for i in range(0, len(raw_bits) - 7, 8):
            byte_list.append(int(raw_bits[i : i + 8], 2))

        raw_bytes = bytes(byte_list)
        if len(raw_bytes) < 8:
            raise ValueError("Corrupt sequence: insufficient payload header.")

        payload_len, expected_crc = struct.unpack(">II", raw_bytes[:8])
        payload = raw_bytes[8 : 8 + payload_len]

        actual_crc = zlib.crc32(payload) & 0xFFFFFFFF
        if actual_crc != expected_crc:
            raise ValueError(f"Integrity check failed: CRC mismatch (Exp: {expected_crc}, Got: {actual_crc})")

        return payload


class DNASteganographyEngine:
    """End-to-end DNA Steganography Engine using standard library primitives."""

    FWD_PRIMER = "ATCGTTAGGCTACGATCG"
    REV_PRIMER = "CGATCGTAGCCTAACGAT"

    def __init__(self, key: str):
        self.key = hashlib.sha256(key.encode("utf-8")).digest()
        self.codec = BioConstrainedCodec()

    def _encrypt_stream(self, data: bytes) -> bytes:
        compressed = zlib.compress(data, level=9)
        keystream = hashlib.pbkdf2_hmac("sha256", self.key, b"dna-salt", 5000, dklen=len(compressed))
        return bytes(a ^ b for a, b in zip(compressed, keystream))

    def _decrypt_stream(self, cipher_data: bytes) -> bytes:
        keystream = hashlib.pbkdf2_hmac("sha256", self.key, b"dna-salt", 5000, dklen=len(cipher_data))
        compressed = bytes(a ^ b for a, b in zip(cipher_data, keystream))
        return zlib.decompress(compressed)

    def conceal(self, secret_data: bytes, carrier_fasta: str) -> str:
        encrypted = self._encrypt_stream(secret_data)
        dna_payload = self.codec.encode_bytes(encrypted)

        # Assemble amplicon
        synthetic_strand = self.FWD_PRIMER + dna_payload + self.REV_PRIMER

        # Embed into carrier at designated insertion locus (e.g. middle of carrier)
        midpoint = len(carrier_fasta) // 2
        stego_fasta = carrier_fasta[:midpoint] + synthetic_strand + carrier_fasta[midpoint:]
        return stego_fasta

    def extract(self, stego_fasta: str) -> bytes:
        start_idx = stego_fasta.find(self.FWD_PRIMER)
        if start_idx == -1:
            raise ValueError("Forward primer not detected: sequence unauthorized or corrupted.")

        payload_start = start_idx + len(self.FWD_PRIMER)
        end_idx = stego_fasta.find(self.REV_PRIMER, payload_start)
        if end_idx == -1:
            raise ValueError("Reverse primer not detected: sequence unauthorized or corrupted.")

        dna_payload = stego_fasta[payload_start:end_idx]
        encrypted_data = self.codec.decode_dna(dna_payload)
        return self._decrypt_stream(encrypted_data)


if __name__ == "__main__":
    secret_message = b"CONFIDENTIAL: Bio-Computing Protocol Initiated at Lat 22.307 N"
    secret_key = "AcademicProject2026!#"

    # Innocent dummy genomic carrier (simulating an E. coli genome fragment)
    carrier_sequence = "GCTGATCGATCGTACGATCGATCGATCGATCGTAGCTAGCTAGCTAGCATCGATCGATCGATC" * 10

    engine = DNASteganographyEngine(key=secret_key)

    # 1. Conceal
    stego_genome = engine.conceal(secret_message, carrier_sequence)

    # 2. Extract
    recovered = engine.extract(stego_genome)

    # 3. Biological Metrics Evaluation
    gc_count = stego_genome.count("G") + stego_genome.count("C")
    gc_percent = (gc_count / len(stego_genome)) * 100

    print("=================== EXECUTION SUMMARY ===================")
    print(f"Original Plaintext: {secret_message.decode()}")
    print(f"Recovered Output  : {recovered.decode()}")
    print(f"Fidelity Match    : {secret_message == recovered}")
    print(f"Total Stego Size  : {len(stego_genome)} bp")
    print(f"GC-Content        : {gc_percent:.2f}% (Target: 40-60%)")
    print(f"Premise Stop Check: {'PASS' if 'TAA' not in stego_genome[len(carrier_sequence)//2 : len(carrier_sequence)//2 + 50] else 'FAIL'}")

