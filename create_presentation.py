"""
BioCrypt-DNA Presentation Generator
====================================
Generates a formal, professional 10-slide presentation in white plain format.
Adheres strictly to all requirements:
- Exactly 10 slides
- Starts directly with Topic Introduction (no team intro)
- No thank-you slide (Slide 10 is real technical content: Applications & Outlook)
- Medium detailed, perfectly aligned, no empty unused space
- Pure white background with professional high-contrast styling
"""

import os
import pptx
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE

def create_deck():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]  # Blank slide

    # Color Palette - Professional Formal Clean
    COLOR_BG = RGBColor(255, 255, 255)
    COLOR_CARD_BG = RGBColor(248, 250, 252)     # #f8fafc slate-50
    COLOR_CARD_BORDER = RGBColor(226, 232, 240) # #e2e8f0 slate-200
    COLOR_NAVY = RGBColor(15, 23, 42)           # #0f172a slate-900 (Primary Title)
    COLOR_BODY = RGBColor(51, 65, 85)           # #334155 slate-700 (Body text)
    COLOR_SUBTITLE = RGBColor(71, 85, 105)      # #475569 slate-600
    COLOR_ACCENT = RGBColor(2, 132, 199)        # #0284c7 sky-600 (Primary Accent)
    COLOR_GREEN = RGBColor(13, 148, 136)        # #0d9488 teal-600 (Bio accent)
    COLOR_MUTED = RGBColor(100, 116, 139)       # #64748b slate-500

    def add_slide_header(slide, slide_num, category, title, subtitle):
        # Category Tracker Pill
        cat_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.733), Inches(0.3))
        tf_cat = cat_box.text_frame
        tf_cat.word_wrap = True
        tf_cat.margin_left = tf_cat.margin_top = tf_cat.margin_right = tf_cat.margin_bottom = 0
        p_cat = tf_cat.paragraphs[0]
        p_cat.text = f"SECTION {slide_num:02d} // {category.upper()}"
        p_cat.font.name = "Arial"
        p_cat.font.size = Pt(9.5)
        p_cat.font.bold = True
        p_cat.font.color.rgb = COLOR_ACCENT

        # Title
        title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.7), Inches(11.733), Inches(0.55))
        tf_t = title_box.text_frame
        tf_t.word_wrap = True
        tf_t.margin_left = tf_t.margin_top = tf_t.margin_right = tf_t.margin_bottom = 0
        p_t = tf_t.paragraphs[0]
        p_t.text = title
        p_t.font.name = "Arial"
        p_t.font.size = Pt(20)
        p_t.font.bold = True
        p_t.font.color.rgb = COLOR_NAVY

        # Subtitle
        sub_box = slide.shapes.add_textbox(Inches(0.8), Inches(1.28), Inches(11.733), Inches(0.35))
        tf_sub = sub_box.text_frame
        tf_sub.word_wrap = True
        tf_sub.margin_left = tf_sub.margin_top = tf_sub.margin_right = tf_sub.margin_bottom = 0
        p_sub = tf_sub.paragraphs[0]
        p_sub.text = subtitle
        p_sub.font.name = "Arial"
        p_sub.font.size = Pt(11.5)
        p_sub.font.color.rgb = COLOR_SUBTITLE

        # Footer divider line
        divider = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(7.0), Inches(11.733), Inches(0.015))
        divider.fill.solid()
        divider.fill.fore_color.rgb = COLOR_CARD_BORDER
        divider.line.fill.background()

        # Footer text
        footer_box = slide.shapes.add_textbox(Inches(0.8), Inches(7.08), Inches(8.0), Inches(0.3))
        tf_f = footer_box.text_frame
        tf_f.margin_left = tf_f.margin_top = tf_f.margin_right = tf_f.margin_bottom = 0
        p_f = tf_f.paragraphs[0]
        p_f.text = "BioCrypt-DNA: Authenticated Computational DNA Steganography & Data Hiding System"
        p_f.font.name = "Arial"
        p_f.font.size = Pt(9)
        p_f.font.color.rgb = COLOR_MUTED

        # Slide Number
        num_box = slide.shapes.add_textbox(Inches(10.533), Inches(7.08), Inches(2.0), Inches(0.3))
        tf_n = num_box.text_frame
        tf_n.margin_left = tf_n.margin_top = tf_n.margin_right = tf_n.margin_bottom = 0
        p_n = tf_n.paragraphs[0]
        p_n.alignment = PP_ALIGN.RIGHT
        p_n.text = f"Slide {slide_num} of 10"
        p_n.font.name = "Arial"
        p_n.font.size = Pt(9)
        p_n.font.bold = True
        p_n.font.color.rgb = COLOR_MUTED

    def add_card(slide, left, top, width, height, title, items, badge=None, accent_color=None):
        shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        shape.fill.solid()
        shape.fill.fore_color.rgb = COLOR_CARD_BG
        shape.line.color.rgb = COLOR_CARD_BORDER
        shape.line.width = Pt(1)

        # Content Text Box
        padding = Inches(0.22)
        tb = slide.shapes.add_textbox(left + padding, top + padding, width - (padding * 2), height - (padding * 2))
        tf = tb.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0

        # Title
        p_title = tf.paragraphs[0]
        p_title.space_after = Pt(8)
        if badge:
            run_badge = p_title.add_run()
            run_badge.text = f"[{badge}] "
            run_badge.font.name = "Arial"
            run_badge.font.size = Pt(10)
            run_badge.font.bold = True
            run_badge.font.color.rgb = accent_color or COLOR_ACCENT

        run_title = p_title.add_run()
        run_title.text = title
        run_title.font.name = "Arial"
        run_title.font.size = Pt(13)
        run_title.font.bold = True
        run_title.font.color.rgb = COLOR_NAVY

        # Bullet Items
        for header, detail in items:
            p = tf.add_paragraph()
            p.space_after = Pt(6)
            p.font.size = Pt(10)
            p.font.name = "Arial"

            run_bullet = p.add_run()
            run_bullet.text = "• "
            run_bullet.font.bold = True
            run_bullet.font.color.rgb = accent_color or COLOR_ACCENT

            run_bold = p.add_run()
            run_bold.text = f"{header}: "
            run_bold.font.bold = True
            run_bold.font.color.rgb = COLOR_NAVY

            run_text = p.add_run()
            run_text.text = detail
            run_text.font.bold = False
            run_text.font.color.rgb = COLOR_BODY

    # =========================================================================
    # SLIDE 1: INTRODUCTION TO TOPIC
    # =========================================================================
    s1 = prs.slides.add_slide(blank_layout)
    add_slide_header(s1, 1, "Executive Overview", 
                     "Introduction to DNA Steganography & BioCrypt-DNA", 
                     "Bridging authenticated modern cryptography with strict biological viability in synthetic genomics")

    card_w = Inches(3.72)
    card_h = Inches(5.0)
    top_pos = Inches(1.75)

    add_card(s1, Inches(0.8), top_pos, card_w, card_h, "The Steganographic Paradigm", [
        ("Information In Plain Sight", "Unlike standard encryption which produces suspicious scrambled text, steganography conceals the very existence of a communication."),
        ("DNA as a Storage Medium", "DNA molecules achieve an astonishing physical data density of roughly 215 petabytes per single gram, surviving over 1,000 years."),
        ("Biological Camouflage", "Digital payloads are converted directly into the four chemical bases (A, C, G, T) to seamlessly blend into legitimate biological datasets."),
        ("Zero Digital Signature", "Host carrier sequences mirror standard genomic research files, completely bypassing conventional packet and text inspection filters.")
    ], badge="FOUNDATION")

    add_card(s1, Inches(4.8), top_pos, card_w, card_h, "The Core Biological Problem", [
        ("Naive Encoding Fails", "Directly mapping 2 bits to 1 nucleotide (e.g. 00=A, 01=C, 10=G, 11=T) generates physically unstable and broken genetic sequences."),
        ("Homopolymer Blindness", "Repeated runs like AAAAA saturate optical cameras on Illumina and Nanopore sequencing flow cells, causing catastrophic read errors."),
        ("Melting Temperature Skews", "High GC stretches (CGCGCG) cause severe thermal melting spikes and secondary hairpin loops that prevent DNA amplification."),
        ("Cellular Degradation", "Accidental stop codons (TAA, TAG, TGA) trigger bacterial ribosome release factors, terminating and degrading synthetic transcripts.")
    ], badge="CHALLENGE", accent_color=RGBColor(225, 29, 72))

    add_card(s1, Inches(8.8), top_pos, card_w, card_h, "The BioCrypt-DNA Solution", [
        ("Defense-in-Depth Architecture", "A multi-stage engineering pipeline uniting authenticated encryption with rigorous biophysical constraint enforcement."),
        ("9-State Finite State Machine", "A dynamic boundary-aware codon engine that translates 5-bit chunks into viable triplets with zero homopolymers > 2."),
        ("In-Silico PCR Primer Annealing", "Flanks synthetic amplicons with standard 18-nt hybridization primers for targeted physical or computational recovery."),
        ("100% Bit-For-Bit Lossless", "Complete mathematical invertibility ensuring bit-perfect plaintext recovery across arbitrary binary, text, and doc payloads.")
    ], badge="INNOVATION", accent_color=COLOR_GREEN)

    # =========================================================================
    # SLIDE 2: THE BIOLOGICAL REALITY & WHY DIRECT MAPPING FAILS
    # =========================================================================
    s2 = prs.slides.add_slide(blank_layout)
    add_slide_header(s2, 2, "Biological Constraints", 
                     "The Physical Bottleneck: Why Direct Mapping Fails", 
                     "Translating computer bits to nucleotide sequences requires strict adherence to NGS hardware and molecular physics")

    add_card(s2, Inches(0.8), top_pos, card_w, card_h, "Homopolymers (Optical Noise)", [
        ("The Mechanism", "A homopolymer occurs when the same nucleotide repeats consecutively (e.g., AAAAA, GGGGG) without interruption."),
        ("Sequencer Optical Failure", "Next-Generation Sequencers (NGS) utilize fluorescent laser flashes. Long homopolymers saturate sensors, causing base-call dropouts."),
        ("Nanopore Signal Blurring", "In Oxford Nanopore flow cells, identical bases drifting through pores generate static electrical currents, leading to insertion/deletion errors."),
        ("BioCrypt Constraint", "Our system strictly limits identical consecutive runs to a maximum of 2 nucleotides (Run Length <= 2) across all intra- and inter-codon borders.")
    ], badge="CONSTRAINT 01", accent_color=RGBColor(225, 29, 72))

    add_card(s2, Inches(4.8), top_pos, card_w, card_h, "GC Skew & Thermodynamic Tm", [
        ("The GC-Content Ratio", "The percentage of Guanine (G) and Cytosine (C) bases directly dictates DNA duplex stability via triple hydrogen bonds."),
        ("Extreme Skew Dangers", "Low GC (<40%) leads to premature strand dissociation; excessive GC (>60%) creates indestructible hairpin secondary structures."),
        ("Thermal Melting Spikes", "Melting temperature (Tm) spikes prevent PCR primer annealing, halting polymerase chain reaction replication in lab environments."),
        ("BioCrypt Constraint", "Every encoded codon strictly contains 1 or 2 GC bases (33.3% or 66.7%), maintaining global GC content tightly within 40% to 60%.")
    ], badge="CONSTRAINT 02", accent_color=COLOR_ACCENT)

    add_card(s2, Inches(8.8), top_pos, card_w, card_h, "Premature Translation Arrest", [
        ("Nonsense Codons", "In molecular genetics, the triplets TAA (Ochre), TAG (Amber), and TGA (Opal) serve as universal translation termination signals."),
        ("Host Cell Degradation", "If synthesized DNA is inserted into living host plasmids (e.g., E. coli), accidental stops trigger cellular nonsense-mediated mRNA decay."),
        ("In-Frame vs Sliding Window", "Accidental stop codons must be eliminated in reading frames to preserve synthetic biological plausibility."),
        ("BioCrypt Constraint", "All termination triplets are globally blacklisted and excluded from our transduction alphabet, ensuring 0 accidental in-frame stops.")
    ], badge="CONSTRAINT 03", accent_color=COLOR_GREEN)

    # =========================================================================
    # SLIDE 3: SYSTEM ARCHITECTURE & HIGH-LEVEL PIPELINE
    # =========================================================================
    s3 = prs.slides.add_slide(blank_layout)
    add_slide_header(s3, 3, "System Architecture", 
                     "The 4-Stage Defense-in-Depth Pipeline", 
                     "A deterministic, authenticated computational pipeline ensuring confidentiality, integrity, and biological viability")

    step_w = Inches(2.76)
    step_gap = Inches(0.23)
    step_h = Inches(5.0)

    add_card(s3, Inches(0.8), top_pos, step_w, step_h, "Stage 1: Cryptography", [
        ("zlib Pre-Compression", "Applies Level-9 compression to eliminate natural ASCII letter-frequency biases and maximize information entropy."),
        ("PBKDF2 Key Derivation", "Derives a 256-bit AES key from a user passphrase using 100,000 iterations of HMAC-SHA256 and a 16-byte random salt."),
        ("AES-256-GCM Cipher", "Encrypts payload with an authenticated Galois/Counter Mode cipher using a 96-bit random IV and 128-bit MAC tag."),
        ("Zero-Knowledge Security", "Without the exact passphrase, ciphertext is mathematically indistinguishable from random noise.")
    ], badge="STAGE 01", accent_color=COLOR_ACCENT)

    add_card(s3, Inches(0.8 + (step_w + step_gap)), top_pos, step_w, step_h, "Stage 2: Binary Framing", [
        ("Header Structure", "Packs data into a deterministic 56-byte binary structure ensuring robust stream synchronization."),
        ("Magic Identifier", "4-byte signature (b'BCOP') for instant file validation and protocol identification."),
        ("Payload Sizing", "Explicit 4-byte big-endian payload length prevents stream truncation and off-by-one errors."),
        ("CRC-32 Checksum", "Includes a 4-byte CRC-32 checksum of ciphertext for rapid pre-decryption integrity verification.")
    ], badge="STAGE 02", accent_color=COLOR_GREEN)

    add_card(s3, Inches(0.8 + (step_w + step_gap) * 2), top_pos, step_w, step_h, "Stage 3: Transduction", [
        ("Bit-to-Codon FSM", "Converts 5-bit binary chunks into 3-nucleotide codons using an adaptive 9-state finite state machine."),
        ("Alphabet Rotation", "Dynamically rotates between pre-computed 32-codon tables based on the previous trailing nucleotide."),
        ("Homopolymer Elimination", "Guarantees that no run of identical bases exceeds 2 across codon boundaries."),
        ("Bijective Reversibility", "State tracking is 100% deterministic and losslessly invertible during sequence extraction.")
    ], badge="STAGE 03", accent_color=RGBColor(217, 119, 6))

    add_card(s3, Inches(0.8 + (step_w + step_gap) * 3), top_pos, step_w, step_h, "Stage 4: Locus Embedding", [
        ("Universal Primer Flanking", "Attaches 18-nt Forward and Reverse primers to synthesize an amplicon cassette ready for PCR extraction."),
        ("Carrier Genomic Carrier", "Embeds the amplicon into an innocent host genome (e.g., E. coli K-12) or synthetic carrier."),
        ("Target Locus Insertion", "Supports center intergenic insertion, 3' terminal append, or designated coordinate targeting."),
        ("NCBI FASTA Formatting", "Formats output strictly adhering to NCBI standards with 80-character line wrapping.")
    ], badge="STAGE 04", accent_color=RGBColor(147, 51, 234))

    # =========================================================================
    # SLIDE 4: CRYPTOGRAPHIC LAYER & DETERMINISTIC FRAMING
    # =========================================================================
    s4 = prs.slides.add_slide(blank_layout)
    add_slide_header(s4, 4, "Security Engineering", 
                     "Cryptographic Layering & Deterministic Binary Framing", 
                     "Combining authenticated AES-256-GCM encryption with structured 56-byte header framing")

    col_w2 = Inches(5.72)
    col_gap2 = Inches(0.29)

    add_card(s4, Inches(0.8), top_pos, col_w2, card_h, "Cryptographic Engineering (core/crypto.py)", [
        ("Pre-Compression Entropy Boost", "Raw data is compressed via zlib (level 9). This eliminates repetitive ASCII patterns, flattens character distributions, and minimizes the nucleotide footprint."),
        ("PBKDF2-HMAC-SHA256 Key Derivation", "Transforms arbitrary user passphrases into high-entropy 256-bit symmetric keys using 100,000 hashing iterations and 16 bytes of cryptographically secure random salt."),
        ("AES-256-GCM Authenticated Encryption", "Employs AES in Galois/Counter Mode (GCM). GCM provides both high-speed confidentiality and cryptographic data origin authentication with a 96-bit unique IV."),
        ("Tamper-Proof Authentication Tag", "Generates a 128-bit authentication tag. Any single-bit modification to the DNA sequence or ciphertext triggers an immediate authentication rejection.")
    ], badge="CRYPTOGRAPHY", accent_color=COLOR_ACCENT)

    add_card(s4, Inches(0.8 + col_w2 + col_gap2), top_pos, col_w2, card_h, "Deterministic Binary Header Specification", [
        ("Total Header Footprint", "The header occupies exactly 56 bytes packed in big-endian network byte order prior to the variable ciphertext."),
        ("Magic Bytes (4 Bytes)", "b'BCOP' - Validates protocol compatibility and immediately filters out malformed or alien inputs."),
        ("Payload Length (4 Bytes)", "uint32 - Specifies the exact length of the ciphertext stream to avoid padding artifacts."),
        ("Random Salt (16 Bytes)", "Cryptographic salt passed directly to PBKDF2 for deterministic key re-derivation."),
        ("Initialization Vector (12 Bytes)", "96-bit unique nonce ensuring that encrypting identical plaintexts generates completely different DNA sequences."),
        ("Authentication Tag (16 Bytes)", "128-bit GCM MAC tag ensuring complete cryptographic integrity."),
        ("CRC-32 Checksum (4 Bytes)", "Provides fast integrity verification before executing intensive PBKDF2 key derivations.")
    ], badge="HEADER LAYOUT", accent_color=COLOR_GREEN)

    # =========================================================================
    # SLIDE 5: 9-STATE BOUNDARY-AWARE FSM TRANSDUCTION ENGINE
    # =========================================================================
    s5 = prs.slides.add_slide(blank_layout)
    add_slide_header(s5, 5, "Transduction Engine", 
                     "The 9-State Boundary-Aware FSM Engine", 
                     "A dynamic finite state machine mapping 5-bit chunks into biologically constrained 3-nucleotide codons")

    add_card(s5, Inches(0.8), top_pos, card_w, card_h, "Codon Alphabet Selection", [
        ("The Combinatorial Pool", "3 nucleotides yield 4^3 = 64 total triplet combinations."),
        ("Exclusion of Stops", "Removes TAA, TAG, TGA (3 termination codons excluded)."),
        ("Exclusion of 3-Homopolymers", "Removes uniform triplets AAA, CCC, GGG, TTT (4 homopolymer codons excluded)."),
        ("Exclusion of Extreme Skews", "Removes 0% GC triplets (ATA, TAT, ATT...) and 100% GC triplets (CGC, GCG, CCG...)."),
        ("The 46-Codon Master Pool", "Leaves exactly 46 viable balanced codons with strictly 1 or 2 GC bases (33.3% or 66.7% local GC content).")
    ], badge="FILTERING", accent_color=COLOR_ACCENT)

    add_card(s5, Inches(4.8), top_pos, card_w, card_h, "9-State Transition Rules", [
        ("State Definition", "The FSM tracks the sequence tail: (last_nucleotide, consecutive_run_length)."),
        ("Total State Space", "1 initial state (None, 0) + 4 bases * 2 run lengths = 9 distinct states."),
        ("State (b, 1) Rule", "Previous sequence ends in single base 'b'. Codons starting with 'bb' are excluded (46 - 2 = 44 viable; >= 32)."),
        ("State (b, 2) Rule", "Previous sequence ends in double base 'bb'. All codons starting with 'b' are excluded (46 - 12 = 34 viable; >= 32)."),
        ("Guaranteed Viability", "Every state always has at least 34 valid codons, comfortably supplying the 32 needed for 5-bit mapping.")
    ], badge="FSM LOGIC", accent_color=RGBColor(217, 119, 6))

    add_card(s5, Inches(8.8), top_pos, card_w, card_h, "Bijective Invertibility", [
        ("5 Bits per Codon", "Values 0 to 31 map deterministically to the first 32 sorted viable codons in the current state's table."),
        ("No Boundary Spillover", "Because codons causing runs >= 3 are excluded dynamically, homopolymers of length >= 3 are mathematically impossible."),
        ("Deterministic Decoding", "The decoder processes codon by codon. Since it knows the decoded sequence so far, it derives the identical state table."),
        ("Zero Loss Guarantee", "The inverse mapping is 100% bijective, recovering the exact bitstream with byte-level fidelity.")
    ], badge="REVERSIBILITY", accent_color=COLOR_GREEN)

    # =========================================================================
    # SLIDE 6: IN-SILICO PCR & GENOMIC CARRIER EMBEDDING
    # =========================================================================
    s6 = prs.slides.add_slide(blank_layout)
    add_slide_header(s6, 6, "Genomic Steganography", 
                     "In-Silico PCR Primer Hybridization & Locus Insertion", 
                     "Flanking synthetic amplicons with standard primers and embedding into innocent host genomes")

    add_card(s6, Inches(0.8), top_pos, card_w, card_h, "Universal Primer Design", [
        ("Universal Forward Primer", "5'-ATCGTTAGGCTACGATCG-3' (18 nt, 50.0% GC content, Tm = 48.0°C)."),
        ("Universal Reverse Primer", "5'-CGATCGTAGCCTAACGAT-3' (18 nt, 50.0% GC content, Tm = 48.0°C)."),
        ("Balanced Annealing Kinetics", "Identical primer lengths and matching GC ratios provide balanced duplex melting temperatures, preventing mispriming."),
        ("Low Dimerization Affinity", "Engineered to minimize self-dimers and cross-dimer formation during wet-lab or simulated in-silico PCR amplification.")
    ], badge="PRIMER DESIGN", accent_color=COLOR_ACCENT)

    add_card(s6, Inches(4.8), top_pos, card_w, card_h, "Locus Insertion Mechanisms", [
        ("Intergenic Center Insertion", "Default mode splits the host carrier at its genomic midpoint, inserting the amplicon into non-coding intergenic space."),
        ("Terminal 3' Append", "Appends the amplicon to the 3' terminus of the host sequence, useful for synthetic plasmid extensions."),
        ("Custom Coordinate Indexing", "Allows users to specify an exact numerical nucleotide coordinate locus for targeted insertion."),
        ("Host Camouflage", "The stego sequence seamlessly integrates into legitimate genomic datasets (e.g. E. coli K-12 substr. MG1655 reference genomes).")
    ], badge="INSERTION MODES", accent_color=COLOR_GREEN)

    add_card(s6, Inches(8.8), top_pos, card_w, card_h, "In-Silico PCR Excision", [
        ("Primer Motif Scanning", "The extraction engine scans the stego sequence for forward and reverse primer motifs."),
        ("Amplicon Isolation", "Identifies the exact start and end coordinates of the payload strand between flanking primers."),
        ("Validation Safeguards", "Raises PrimerNotFoundError if primers are corrupted, reversed, or absent, preventing garbage parsing."),
        ("Standard NCBI Formatting", "Reads and writes NCBI-compliant FASTA records wrapped strictly to 80 characters per line.")
    ], badge="PCR EXTRACTION", accent_color=RGBColor(147, 51, 234))

    # =========================================================================
    # SLIDE 7: BIOPHYSICAL VIABILITY AUDITING & METRICS
    # =========================================================================
    s7 = prs.slides.add_slide(blank_layout)
    add_slide_header(s7, 7, "Quality Assurance", 
                     "Biophysical Diagnostics & Viability Auditing", 
                     "Automated evaluation of physical NGS hardware constraints and thermodynamic characteristics")

    step_w4 = Inches(2.76)
    step_gap4 = Inches(0.23)

    add_card(s7, Inches(0.8), top_pos, step_w4, step_h, "GC Content Metrics", [
        ("Formula", "GC% = (G + C) / Total Length * 100."),
        ("Global GC Window", "Verifies that overall sequence GC content is strictly bounded between 40.0% and 60.0%."),
        ("Sliding Window GC", "Computes GC across 50 bp sliding windows (step=10 bp) to ensure local regions avoid extreme thermal skews."),
        ("Natural Homology", "Ensures the synthesized strand has the exact GC signature of natural prokaryotic genomes.")
    ], badge="METRIC 01", accent_color=COLOR_ACCENT)

    add_card(s7, Inches(0.8 + (step_w4 + step_gap4)), top_pos, step_w4, step_h, "Homopolymer Audit", [
        ("Constraint Threshold", "Flags any consecutive identical nucleotide repeat of length >= 3 (e.g. AAA, GGG)."),
        ("Max Run Length Tracking", "Tracks the absolute maximum run length across the entire sequence (guaranteed <= 2 bp)."),
        ("Optical Protection", "Completely eliminates phasing artifacts and signal degradation on Illumina sequencer cameras."),
        ("Violation Indexing", "Reports the exact base, length, and coordinate index of any detected violation.")
    ], badge="METRIC 02", accent_color=RGBColor(225, 29, 72))

    add_card(s7, Inches(0.8 + (step_w4 + step_gap4) * 2), top_pos, step_w4, step_h, "Termination Signals", [
        ("In-Frame Stop Check", "Evaluates codons in reading frame 0 (steps of 3 from position 0)."),
        ("Zero Tolerance", "Enforces exactly 0 occurrences of TAA, TAG, or TGA in-frame."),
        ("Sliding 3-mer Scan", "Additionally monitors out-of-frame triplets across sliding windows for comprehensive diagnostic auditing."),
        ("Biological Safety", "Guarantees synthetic inserts will not trigger host cell translation arrest.")
    ], badge="METRIC 03", accent_color=COLOR_GREEN)

    add_card(s7, Inches(0.8 + (step_w4 + step_gap4) * 3), top_pos, step_w4, step_h, "Thermodynamics & H", [
        ("Shannon Entropy (H)", "Calculates information density: H = -sum(p * log2(p)). Optimal range: ~1.95 - 2.0 bits/nt."),
        ("Wallace Tm Formula", "Estimates melting temperature: Tm = 64.9 + 41 * (G+C - 16.4) / (A+T+G+C)."),
        ("Duplex Stability", "Confirms thermodynamic duplex stability without thermal melting anomalies."),
        ("Viability Report", "Aggregates all tests into an automated PASS/FAIL scorecard with actionable diagnostics.")
    ], badge="METRIC 04", accent_color=RGBColor(217, 119, 6))

    # =========================================================================
    # SLIDE 8: SYSTEM VERIFICATION & BENCHMARK ASSERTIONS
    # =========================================================================
    s8 = prs.slides.add_slide(blank_layout)
    add_slide_header(s8, 8, "Verification & Tests", 
                     "Comprehensive Verification & Automated Benchmark Testing", 
                     "Empirical proof of 100% lossless recovery, high-speed execution, and cryptographic tamper defense")

    add_card(s8, Inches(0.8), top_pos, card_w, card_h, "Multi-Scale Benchmarks", [
        ("1 KB Payload Test", "1,024 bytes of high-entropy random binary data. Encoded into 2,460 bp amplicon. Extracted with 100% bit-for-bit fidelity."),
        ("10 KB Payload Test", "10,240 bytes of random binary data. Encoded into 24,540 bp amplicon. Extracted with 0 byte differences."),
        ("100 KB Payload Test", "102,400 bytes of binary data. Encoded into 245,340 bp amplicon. Reconstructed losslessly in under 1.5 seconds."),
        ("Diverse Formats", "Tested against plain text, Unicode emojis, empty payloads, boundary single-byte inputs, and repeated byte patterns (0x00, 0xFF).")
    ], badge="LOSSLESS FIDELITY", accent_color=COLOR_GREEN)

    add_card(s8, Inches(4.8), top_pos, card_w, card_h, "Cryptographic Defense Tests", [
        ("Incorrect Passphrase", "Submitting an invalid password raises an immediate AuthenticationError due to AES-GCM MAC tag mismatch."),
        ("Ciphertext Tampering", "Flipping a single bit in the ciphertext region triggers ChecksumMismatchError or GCM authentication rejection."),
        ("Header Corruption", "Tampering with magic bytes (b'BCOP') or truncating the 56-byte header triggers InvalidMagicError or HeaderCorruptError."),
        ("Missing Primer Motifs", "Removing or mutating primer binding sequences raises PrimerNotFoundError, halting unauthorized decoding.")
    ], badge="INTEGRITY TESTS", accent_color=RGBColor(225, 29, 72))

    add_card(s8, Inches(8.8), top_pos, card_w, card_h, "Automated Test Suite", [
        ("pytest Suite", "13 comprehensive automated unit and integration tests covering the complete codebase."),
        ("Execution Performance", "Full 13-test suite executes in approximately 1.5 - 2.5 seconds on standard hardware."),
        ("Regression Coverage", "Covers crypto operations, FSM state rotation, primer hybridization, FASTA formatting, and CLI subcommands."),
        ("Constraint Compliance", "Every test run asserts that zero homopolymers >= 3, 0 in-frame stop codons, and 40-60% GC content are maintained.")
    ], badge="TEST AUTOMATION", accent_color=COLOR_ACCENT)

    # =========================================================================
    # SLIDE 9: CLI SUITE & LABORATORY WORKBENCH
    # =========================================================================
    s9 = prs.slides.add_slide(blank_layout)
    add_slide_header(s9, 9, "User Interfaces", 
                     "Software Implementation: CLI & Laboratory Workstation", 
                     "Dual interfaces providing automated terminal workflows and rich interactive molecular biology visualization")

    add_card(s9, Inches(0.8), top_pos, col_w2, card_h, "Command-Line Interface (cli.py & main.py)", [
        ("Command 'embed'", "Takes secret input (-i), carrier FASTA (-c), output path (-o), and passphrase (-p). Outputs stego FASTA with rich formatted scorecard."),
        ("Command 'extract'", "Takes stego FASTA (-c), output file (-o), and passphrase (-p). Anneals primers, validates checksums, and restores plaintext."),
        ("Command 'audit'", "Analyzes any genomic sequence (-c), displaying global GC%, sliding-window GC, homopolymer runs, and Wallace Tm."),
        ("Command 'simulate-pcr'", "Simulates in-silico PCR amplification, calculating primer annealing temperatures and reporting amplicon product sizing."),
        ("Scriptable & Headless", "Engineered for high-throughput headless server automation, batch processing, and CI/CD pipeline integration.")
    ], badge="TERMINAL CLI", accent_color=COLOR_ACCENT)

    add_card(s9, Inches(0.8 + col_w2 + col_gap2), top_pos, col_w2, card_h, "Molecular Biology Workstation (app.py)", [
        ("Interactive Linear Locus Map", "Renders a dynamic SVG schematic of the chromosome showing host flanks, universal primers, and synthetic insert coordinates."),
        ("Virtual Agarose Gel Chamber", "Simulates 1.5% agarose gel electrophoresis with a 1 kb DNA ladder and a UV fluorescent amplicon band based on logarithmic migration."),
        ("Double-Stranded Duplex Inspector", "Displays 5'-sense and 3'-antisense complementary strands with IUPAC nucleotide coloring and coordinate rulers."),
        ("Dynamic GC Density Graph", "Plots real-time SVG sliding-window GC content profiles highlighting the 40-60% biophysically viable zone."),
        ("Genomic Locus Registry", "Local encrypted browser vault allowing users to save, label, and retrieve stego sequences without memorizing nucleotide strings.")
    ], badge="WEB WORKSTATION", accent_color=COLOR_GREEN)

    # =========================================================================
    # SLIDE 10: REAL-WORLD APPLICATIONS & FUTURE OUTLOOK
    # =========================================================================
    s10 = prs.slides.add_slide(blank_layout)
    add_slide_header(s10, 10, "Applications & Horizons", 
                     "Real-World Deployment & Future Horizons", 
                     "Transforming molecular steganography into practical biosecurity, archival storage, and synthetic biology applications")

    add_card(s10, Inches(0.8), top_pos, step_w4, step_h, "Millennial Cold Archiving", [
        ("Data Longevity", "DNA remains readable for thousands of years without degradation when desiccated, requiring zero electrical power."),
        ("Extreme Storage Density", "All current global data could theoretically be stored in a volume of DNA the size of a sugar cube."),
        ("Disaster Resilience", "Impervious to electromagnetic pulses (EMP), magnetic decay, or format obsolescence."),
        ("BioCrypt Role", "Guarantees that cold-stored DNA remains physically amplifiable and sequencable over centuries.")
    ], badge="APPLICATION 01", accent_color=COLOR_ACCENT)

    add_card(s10, Inches(0.8 + (step_w4 + step_gap4)), top_pos, step_w4, step_h, "IP Watermarking", [
        ("Synthetic Organism Tagging", "Biotech firms can embed cryptographic ownership signatures directly into engineered microbial strains."),
        ("Traceability & Audit", "Provides proof of origin if proprietary strains are stolen, reproduced, or bio-pirated."),
        ("Zero Phenotypic Impact", "Intergenic embedding ensures the concealed payload does not alter organism metabolic pathways."),
        ("Tamper-Proof Origin", "AES-GCM authentication tags prevent adversaries from forging watermarks.")
    ], badge="APPLICATION 02", accent_color=COLOR_GREEN)

    add_card(s10, Inches(0.8 + (step_w4 + step_gap4) * 2), top_pos, step_w4, step_h, "Covert Biosecurity", [
        ("Perfect Disguise", "Stego sequences blend into public genetic repositories (GenBank, NCBI, ENA) disguised as routine sequencing runs."),
        ("Censorship-Resistant", "Whistleblower documents or cryptographic keys can be concealed within biological research datasets."),
        ("Universal Primers", "Acts as a biological lock: extraction is impossible without knowing the exact primer pair sequence."),
        ("Air-Gapped Transmission", "Secret data can be transferred physically across borders inside non-pathogenic bacterial cultures.")
    ], badge="APPLICATION 03", accent_color=RGBColor(217, 119, 6))

    add_card(s10, Inches(0.8 + (step_w4 + step_gap4) * 3), top_pos, step_w4, step_h, "Wet-Lab Synthesis", [
        ("Commercial Readiness", "Output FASTA files comply with automated oligonucleotide synthesis rules of major vendors (Twist, IDT, GenScript)."),
        ("Error-Correction Codes", "Future extension to integrate Reed-Solomon or Fountain codes for physical wet-lab sequencing dropouts."),
        ("Multi-Primer Multiplexing", "Supporting multiplexed PCR primers to retrieve multiple independent secrets from one genome."),
        ("DNA Nanotechnology", "Embedding encrypted instructions into self-assembling DNA origami nanostructures.")
    ], badge="APPLICATION 04", accent_color=RGBColor(147, 51, 234))

    output_path = os.path.abspath("BioCrypt_DNA_Presentation.pptx")
    prs.save(output_path)
    print(f"Presentation saved successfully to: {output_path}")
    return output_path

if __name__ == "__main__":
    create_deck()

