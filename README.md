# BioCrypt-DNA: Computational DNA Steganography & Data Hiding System

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Cryptography AES-256-GCM](https://img.shields.io/badge/crypto-AES--256--GCM-green.svg)](https://cryptography.io/)
[![Biological Constraints](https://img.shields.io/badge/bio--constraints-Homopolymer%20%E2%89%A4%202%20%7C%20GC%2040--60%25-orange.svg)]()
[![Tests Passing](https://img.shields.io/badge/tests-13%20passed-brightgreen.svg)]()

**BioCrypt-DNA** is a production-grade computational DNA steganography suite that conceals arbitrary files and binary streams inside biological genomic sequences (FASTA format). It bridges authenticated symmetric cryptography with strict biological viability constraints without requiring physical wet-lab synthesis.

---

## 1. System Architecture & 4-Stage Pipeline

The system uses a defense-in-depth, 4-stage pipeline: **Cryptographic Layering $\to$ Error-Correcting Framing $\to$ Bio-Constrained Transduction $\to$ Genomic Carrier Embedding**.

```
ENCODING PIPELINE:
[Plaintext / Binary / File]
        │
        ▼  [Stage 1: Authenticated Cryptographic Layer]
  zlib Compression (Level 9) + PBKDF2-HMAC-SHA256 (100k iter) + AES-256-GCM + IV (12B) + Salt (16B) + Tag (16B)
        │
        ▼  [Stage 2: Deterministic Binary Header Framing]
  [MAGIC (4B: b"BCOP")] + [Payload Len (4B)] + [Salt (16B)] + [IV (12B)] + [Tag (16B)] + [CRC-32 (4B)] + [Ciphertext]
        │
        ▼  [Stage 3: Bio-Constrained Transduction Engine]
  9-State Boundary-Aware Finite State Machine (5 bits -> 3-nucleotide codons)
  (Enforces: Max run <= 2, GC 40-60%, Zero in-frame termination codons)
        │
        ▼  [Stage 4: Steganographic Carrier Embedder]
  5'- [Universal Forward Primer (18 nt)] + [Bio-Constrained Stego Strand] + [Reverse Primer (18 nt)] -3'
        │  (Injected into center, append, or target coordinate locus)
        ▼
[NCBI FASTA Stego Genome (80-char line wrap)]

DECODING PIPELINE:
[NCBI FASTA Stego Genome]
        │
        ▼  [Stage 1: In-Silico PCR Primer Annealing]
  Scan Forward (5'-ATCGTTAGGCTACGATCG-3') & Reverse (5'-CGATCGTAGCCTAACGAT-3') Primers -> Extract Payload Strand
        │
        ▼  [Stage 2: Inverse FSM Transduction]
  Reverse 9-State Codon Machine -> Reconstruct Framed Bitstream
        │
        ▼  [Stage 3: Frame Validation & Integrity Verification]
  Verify b"BCOP" Magic Bytes + Validate CRC-32 Checksum
        │
        ▼  [Stage 4: Authenticated Decryption & Decompression]
  PBKDF2 Key Derivation + AES-256-GCM Tag Verification + zlib Decompression -> 100% Lossless Recovery
```

---

## 2. Biological Constraints & Mathematical Mapping

### 2.1 Why Direct Mapping Fails
A naive mapping like `00 -> A`, `01 -> C`, `10 -> G`, `11 -> T` fails in real-world genomics:
1. **Homopolymers**: Uniform sequences like `AAAAA` or `GGGGG` cause fluorescent signal saturation and phase errors on Next-Generation Sequencing (NGS) optical flow cells (Illumina, Oxford Nanopore).
2. **Melting Temperature ($T_m$) Spikes**: High GC stretches (`CGCGCCGC`) dramatically raise melting temperatures, causing primer annealing failure and secondary hairpin loop formation.
3. **Premature Stop Codons**: Arbitrary in-frame codons `TAA`, `TAG`, `TGA` trigger ribosomal release factors and cellular degradation in synthetic hosts.

### 2.2 The 9-State Rotating Transduction Engine
To guarantee zero homopolymers $> 2$, GC content between 40% and 60%, and zero in-frame stop codons:
- 3 nucleotides offer $4^3 = 64$ combinations.
- We filter out:
  - 3 stop codons (`TAA`, `TAG`, `TGA`).
  - 4 uniform 3-homopolymers (`AAA`, `CCC`, `GGG`, `TTT`).
  - Extreme GC codons (0% GC and 100% GC).
- This leaves a pool of **46 balanced codons** ($33.3\%$ or $66.7\%$ GC).
- We implement a **9-State Boundary-Aware Finite State Machine (FSM)** tracking `(last_base, run_length)`:
  - State `(None, 0)`: Initial state $\to$ 32 sorted viable codons.
  - State `(b, 1)`: Trailing single nucleotide $b \to$ codons starting with $bb$ are excluded ($46 - 2 = 44 \ge 32$).
  - State `(b, 2)`: Trailing double nucleotide $bb \to$ all codons starting with $b$ are excluded ($46 - 12 = 34 \ge 32$).
- **Result**: Every state has $\ge 32$ viable codons, ensuring bijective 5-bit to 3-nt transduction with a strict maximum homopolymer run length $\le 2$ across all inter-codon boundaries.

---

## 3. Directory Layout

```
bio_crypt/
├── core/
│   ├── __init__.py         # Package facade (DNASteganographyEngine)
│   ├── crypto.py           # AES-256-GCM, PBKDF2 (100k), CRC-32, framing, zlib
│   ├── transducer.py       # 9-state boundary-aware FSM codon engine
│   ├── carrier.py          # NCBI FASTA reader/writer, primers, locus embedder
│   └── metrics.py          # Viability audit (GC%, homopolymers, entropy, Tm)
├── cli.py                  # Rich terminal CLI interface (Click + Rich)
├── main.py                 # CLI entry point alias
├── dna_stego_core.py       # Standalone zero-dependency standard library prototype
├── tests/
│   ├── test_system.py      # 13 automated tests & 1KB/10KB/100KB benchmarks
│   └── test_pipeline.py    # Pipeline alias test module
├── requirements.txt        # cryptography, rich, click, pytest
└── README.md               # Scientific explanation & complete guide
```

---

## 4. Installation & Requirements

Ensure **Python 3.8+** is installed.

```bash
# Install dependencies
pip install -r requirements.txt
```

---

## 5. Command-Line Interface (CLI) Usage

### 5.1 Conceal Secret Data (`embed`)
Embeds a secret file inside an innocent host carrier genome (or auto-generates a balanced synthetic carrier):

```bash
# Embed into an existing carrier genome (e.g. E. coli)
python cli.py embed -i secret.txt -c carrier.fasta -o stego_genome.fasta -p "SecretPassphrase2026"

# Embed with auto-generated synthetic host carrier:
python cli.py embed -i confidential.pdf -o stego_genome.fasta -p "SecretPassphrase2026" --locus center
```

### 5.2 Extract and Recover Plaintext (`extract`)
Recovers the secret payload with 100% bit-for-bit lossless fidelity:

```bash
python cli.py extract -c stego_genome.fasta -o recovered.txt -p "SecretPassphrase2026"
```

### 5.3 Biological Viability Audit (`audit`)
Generates a biophysical scorecard assessing GC content, homopolymers, Shannon entropy, and melting temperature:

```bash
python cli.py audit -c stego_genome.fasta
```

### 5.4 In-Silico PCR Amplification (`simulate-pcr`)
Simulates PCR primer annealing and computes amplicon size and melting temperatures:

```bash
python cli.py simulate-pcr -c stego_genome.fasta
```

---

## 6. Programmatic Python API

```python
from core import DNASteganographyEngine, BiologicalMetrics

# 1. Initialize engine with a secure passphrase
engine = DNASteganographyEngine(passphrase="BioResearchKey2026!")

# 2. Conceal secret bytes
secret_data = b"CONFIDENTIAL: In-silico synthetic biology experiment protocol."
stego_fasta, report = engine.conceal(secret_data)

print(f"Stego length: {len(stego_fasta)} bp")
print(f"Viability Status: {report.is_viable}")
print(f"Max homopolymer: {report.max_homopolymer_run} bp")
print(f"Global GC: {report.gc_percent:.2f}%")

# 3. Extract and verify lossless recovery
recovered = engine.extract(stego_fasta)
assert recovered == secret_data
print("Decryption successful: 100% fidelity match!")
```

---

## 7. Running the Automated Test Suite

Run pytest to execute the comprehensive test suite (including 1 KB, 10 KB, and 100 KB binary payloads, tamper detection, wrong passwords, and biological constraint assertions):

```bash
pytest tests/test_system.py -v
```

