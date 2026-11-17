"""
BioCrypt Genomics Laboratory Workstation
========================================
High-precision computational biology platform with:
- Linear Genomic Cassette Map (Interactive SVG locus view)
- In-Silico Virtual Agarose Gel Electrophoresis (UV transilluminator simulation)
- Double-Stranded 5'->3' / 3'->5' Nucleotide Inspector
- Sliding-Window GC% Density Profile Graph (SVG dynamic area plot)
- Authenticated AES-256-GCM + 9-State Transduction FSM
"""

from __future__ import annotations

import base64
import os
import sys
from typing import Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from core import (
    AuthenticationError,
    BiologicalMetrics,
    CarrierEngine,
    ChecksumMismatchError,
    DNASteganographyEngine,
    PrimerNotFoundError,
)

app = FastAPI(
    title="BioCrypt Genomics Laboratory Workstation",
    description="Computational DNA Steganography & Biophysical Viability Suite",
    version="4.0.0",
    redirect_slashes=False,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def vercel_path_normalizer(request: Request, call_next):
    orig_path = (
        request.headers.get("x-matched-path")
        or request.headers.get("x-forwarded-uri")
        or request.headers.get("x-invoke-path")
        or request.headers.get("x-original-url")
        or request.headers.get("x-rewrite-url")
    )
    if orig_path:
        clean_path = orig_path.split("?")[0]
        if clean_path in ["/api/index.py", "/api/index", "/api", "/api/"]:
            clean_path = "/"
        elif clean_path.startswith("/api/index.py/"):
            clean_path = clean_path[len("/api/index.py"):]
        elif clean_path.startswith("/api/index/"):
            clean_path = clean_path[len("/api/index"):]
        request.scope["path"] = clean_path
    else:
        path = request.scope.get("path", "")
        if path in ["/api/index.py", "/api/index", "/api", "/api/"]:
            request.scope["path"] = "/"
        elif path.startswith("/api/index.py/"):
            request.scope["path"] = path[len("/api/index.py"):]
        elif path.startswith("/api/index/"):
            request.scope["path"] = path[len("/api/index"):]
    return await call_next(request)


class ConcealRequest(BaseModel):
    secret_text: str
    password: str
    carrier_fasta: Optional[str] = None
    locus: Optional[str] = "center"


class ExtractRequest(BaseModel):
    stego_fasta: str
    password: str


class AuditRequest(BaseModel):
    sequence: str


class PcrRequest(BaseModel):
    sequence: str
    fwd_primer: Optional[str] = "ATCGTTAGGCTACGATCG"
    rev_primer: Optional[str] = "CGATCGTAGCCTAACGAT"


@app.post("/api/conceal")
@app.post("/conceal")
async def api_conceal(payload: ConcealRequest):
    if not payload.secret_text.strip():
        raise HTTPException(status_code=400, detail="Secret payload is required.")
    if not payload.password.strip():
        raise HTTPException(status_code=400, detail="Cryptographic passphrase is required.")

    try:
        engine = DNASteganographyEngine(passphrase=payload.password)
        locus: int | str = payload.locus or "center"
        if isinstance(locus, str) and locus.isdigit():
            locus = int(locus)

        stego_seq, report = engine.conceal(
            secret_data=payload.secret_text.encode("utf-8"),
            carrier_fasta=payload.carrier_fasta,
            locus=locus,
        )

        formatted_fasta = CarrierEngine.write_fasta(
            header="BioCrypt_Synthetic_Cassette",
            sequence=stego_seq,
        )

        fwd_idx = stego_seq.find(engine.carrier.fwd_primer)
        payload_start = fwd_idx + len(engine.carrier.fwd_primer)
        rev_idx = stego_seq.find(engine.carrier.rev_primer, payload_start)
        rev_end = rev_idx + len(engine.carrier.rev_primer) if rev_idx != -1 else -1

        sliding_gc = BiologicalMetrics.calc_sliding_window_gc(stego_seq, window_size=50, step=15)

        return {
            "success": True,
            "stego_fasta": formatted_fasta,
            "stego_sequence": stego_seq,
            "stego_length": len(stego_seq),
            "coordinates": {
                "fwd_start": fwd_idx,
                "fwd_end": payload_start,
                "payload_start": payload_start,
                "payload_end": rev_idx,
                "rev_start": rev_idx,
                "rev_end": rev_end,
                "payload_length": report.sequence_length,
                "carrier_length": len(stego_seq) - (rev_end - fwd_idx) if rev_end != -1 else len(stego_seq),
            },
            "sliding_gc_points": sliding_gc[:80],
            "metrics": report.to_dict(),
        }
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.post("/api/extract")
@app.post("/extract")
async def api_extract(payload: ExtractRequest):
    if not payload.stego_fasta.strip():
        raise HTTPException(status_code=400, detail="FASTA carrier sequence is required.")
    if not payload.password.strip():
        raise HTTPException(status_code=400, detail="Authentication passphrase is required.")

    try:
        engine = DNASteganographyEngine(passphrase=payload.password)
        recovered_bytes = engine.extract(payload.stego_fasta)

        is_text = True
        try:
            recovered_text = recovered_bytes.decode("utf-8")
        except UnicodeDecodeError:
            is_text = False
            recovered_text = base64.b64encode(recovered_bytes).decode("ascii")

        return {
            "success": True,
            "is_text": is_text,
            "recovered_text": recovered_text,
            "byte_length": len(recovered_bytes),
        }
    except PrimerNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="PCR annealing failed: primer binding motifs (5'-ATCGTTAGGCTACGATCG and 5'-CGATCGTAGCCTAACGAT) not detected.",
        )
    except AuthenticationError:
        raise HTTPException(
            status_code=401,
            detail="Cryptographic authentication failed: AES-256-GCM MAC tag mismatch. Passphrase invalid.",
        )
    except ChecksumMismatchError:
        raise HTTPException(
            status_code=422,
            detail="Integrity check failed: CRC-32 checksum did not match payload stream.",
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Extraction failure: {exc}")


@app.post("/api/audit")
@app.post("/audit")
async def api_audit(payload: AuditRequest):
    if not payload.sequence.strip():
        raise HTTPException(status_code=400, detail="Target nucleotide sequence required.")

    seq = payload.sequence
    if ">" in seq:
        try:
            records = CarrierEngine.read_fasta(seq)
            seq = records[0].sequence
        except Exception:
            pass

    clean_seq = "".join(ch for ch in seq if ch.isalpha()).upper()
    if not clean_seq:
        raise HTTPException(status_code=400, detail="No nucleotide letters (A, C, G, T) identified.")

    report = BiologicalMetrics.audit_sequence(clean_seq)
    sliding_gc = BiologicalMetrics.calc_sliding_window_gc(clean_seq, window_size=50, step=15)

    return {
        "success": True,
        "metrics": report.to_dict(),
        "sliding_gc_points": sliding_gc[:80],
    }


@app.post("/api/simulate-pcr")
@app.post("/simulate-pcr")
async def api_simulate_pcr(payload: PcrRequest):
    if not payload.sequence.strip():
        raise HTTPException(status_code=400, detail="Genomic sequence required.")

    fwd = payload.fwd_primer or "ATCGTTAGGCTACGATCG"
    rev = payload.rev_primer or "CGATCGTAGCCTAACGAT"

    carrier = CarrierEngine(fwd_primer=fwd, rev_primer=rev)

    seq = payload.sequence
    if ">" in seq:
        try:
            records = carrier.read_fasta(seq)
            seq = records[0].sequence
        except Exception:
            pass

    clean_seq = "".join(ch for ch in seq if ch.isalpha()).upper()

    fwd_tm = BiologicalMetrics.estimate_melting_temp(fwd)
    rev_tm = BiologicalMetrics.estimate_melting_temp(rev)

    try:
        extracted = carrier.extract_from_carrier(clean_seq)
        amplicon = carrier.assemble_amplicon(extracted)
        fwd_idx = clean_seq.find(carrier.fwd_primer)
        rev_idx = clean_seq.find(carrier.rev_primer, fwd_idx + len(carrier.fwd_primer))

        return {
            "success": True,
            "amplicon_length": len(amplicon),
            "payload_length": len(extracted),
            "fwd_primer": fwd,
            "fwd_tm": round(fwd_tm, 1),
            "rev_primer": rev,
            "rev_tm": round(rev_tm, 1),
            "annealing_tm_recommended": round(min(fwd_tm, rev_tm) - 5.0, 1),
            "amplicon_sequence": amplicon,
            "coordinates": {"fwd_start": fwd_idx, "rev_end": rev_idx + len(rev)},
        }
    except PrimerNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="PCR amplification yielded zero product. Primer hybridization failed.",
        )


@app.get("/api/test-headers")
@app.post("/api/test-headers")
async def test_headers(request: Request):
    return {
        "headers": dict(request.headers),
        "url_path": request.url.path,
        "scope_path": request.scope.get("path")
    }


@app.get("/", response_class=HTMLResponse)
@app.get("/api", response_class=HTMLResponse)
@app.get("/api/", response_class=HTMLResponse)
@app.get("/api/index", response_class=HTMLResponse)
@app.get("/api/index.py", response_class=HTMLResponse)
@app.get("/index", response_class=HTMLResponse)
@app.get("/index.py", response_class=HTMLResponse)
async def serve_index():
    return HTMLResponse(content=INDEX_HTML)


INDEX_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BioCrypt Workbench &bull; DNA Data Storage &amp; Secret Hider</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@300;400;500;600;700&family=IBM+Plex+Mono:ital,wght@0,400;0,500;0,600;1,400&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-lab: #0d121c;
            --surface-panel: #131926;
            --surface-inner: #090d15;
            --border-lab: #1f293d;
            --border-highlight: #2f3e5c;
            --color-a: #22c55e;
            --color-c: #3b82f6;
            --color-g: #eab308;
            --color-t: #ef4444;
        }
        body {
            font-family: 'IBM Plex Sans', -apple-system, sans-serif;
            background-color: var(--bg-lab);
            color: #d1d5db;
        }
        .mono {
            font-family: 'IBM Plex Mono', monospace;
        }
        .lab-scroll::-webkit-scrollbar {
            width: 5px;
            height: 5px;
        }
        .lab-scroll::-webkit-scrollbar-thumb {
            background: #26334d;
            border-radius: 2px;
        }
        .lab-scroll::-webkit-scrollbar-track {
            background: #090d15;
        }
        .nt-A { color: var(--color-a); }
        .nt-C { color: var(--color-c); }
        .nt-G { color: var(--color-g); }
        .nt-T { color: var(--color-t); }
        .gel-lane {
            background: linear-gradient(180deg, #070a10 0%, #0d121c 100%);
            box-shadow: inset 0 0 12px rgba(0,0,0,0.8);
        }
        .gel-band {
            background: linear-gradient(90deg, transparent 5%, #38bdf8 30%, #a5f3fc 50%, #38bdf8 70%, transparent 95%);
            filter: drop-shadow(0 0 4px #06b6d4) drop-shadow(0 0 8px #38bdf8);
            border-radius: 1px;
        }
        .gel-band-ladder {
            background: linear-gradient(90deg, transparent 10%, #64748b 40%, #94a3b8 50%, #64748b 60%, transparent 90%);
            opacity: 0.7;
        }
    </style>
</head>
<body class="min-h-screen flex flex-col antialiased">

    <!-- Toast Notifications -->
    <div id="toast-shelf" class="fixed top-5 right-5 z-50 flex flex-col space-y-2 pointer-events-none"></div>

    <!-- Top Instrument Navigation Bar -->
    <header class="border-b border-[#1f293d] bg-[#111723] sticky top-0 z-40">
        <div class="max-w-[1440px] mx-auto px-5 h-14 flex items-center justify-between">
            <div class="flex items-center space-x-3">
                <div class="w-7 h-7 rounded bg-[#1e293b] border border-[#334155] flex items-center justify-center text-xs font-mono font-bold text-sky-400">
                    &psi;
                </div>
                <div class="flex items-center space-x-2">
                    <span class="text-sm font-semibold tracking-tight text-white font-mono uppercase">BIOCRYPT-DNA</span>
                    <span class="text-[11px] text-slate-400 font-mono">/ Hide Digital Files Inside Real DNA</span>
                </div>
            </div>

            <!-- Hardware & Pipeline Protocol Status -->
            <div class="flex items-center space-x-4 text-xs font-mono">
                <div class="hidden md:flex items-center space-x-3 px-3 py-1 bg-[#090d15] rounded border border-[#1f293d] text-[11px] text-slate-400">
                    <span class="flex items-center gap-1.5 text-emerald-400">
                        <span class="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
                        SYSTEM READY
                    </span>
                    <span class="text-slate-600">|</span>
                    <span>AES-256 ENCRYPTED</span>
                    <span class="text-slate-600">|</span>
                    <span class="text-sky-400">SAFE DNA RULES: ON</span>
                </div>

                <button onclick="toggleVaultDrawer()" class="px-3 py-1 rounded bg-[#1b2233] hover:bg-[#232c42] border border-[#2d374d] text-slate-200 text-xs font-medium flex items-center gap-1.5 transition">
                    <svg class="w-3.5 h-3.5 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 7v10c0 2 1.5 3 3.5 3h9c2 0 3.5-1 3.5-3V7M4 7c0-2 1.5-3 3.5-3h9c2 0 3.5 1 3.5 3M4 7h16m-5 5h3"></path></svg>
                    <span>Saved DNA Library</span>
                    <span id="vault-pill-count" class="px-1.5 py-0.2 rounded bg-[#090d15] text-[10px] text-sky-400">0</span>
                </button>
            </div>
        </div>
    </header>

    <!-- Lab Protocol Navigation Tabs -->
    <div class="border-b border-[#1f293d] bg-[#0c111a]">
        <div class="max-w-[1440px] mx-auto px-5 flex space-x-1 py-1 font-mono text-xs">
            <button onclick="switchTab('protocol-embed')" id="btn-tab-embed" class="px-4 py-2 rounded font-medium text-white bg-[#192233] border border-[#2a3752] transition flex items-center gap-2">
                <span class="text-sky-400">01</span> Hide Secret (Encode)
            </button>
            <button onclick="switchTab('protocol-extract')" id="btn-tab-extract" class="px-4 py-2 rounded font-medium text-slate-400 hover:text-slate-200 transition flex items-center gap-2">
                <span class="text-slate-500">02</span> Recover Secret (Decode)
            </button>
            <button onclick="switchTab('protocol-gel')" id="btn-tab-gel" class="px-4 py-2 rounded font-medium text-slate-400 hover:text-slate-200 transition flex items-center gap-2">
                <span class="text-slate-500">03</span> Virtual Gel Test
            </button>
            <button onclick="switchTab('protocol-audit')" id="btn-tab-audit" class="px-4 py-2 rounded font-medium text-slate-400 hover:text-slate-200 transition flex items-center gap-2">
                <span class="text-slate-500">04</span> DNA Health Check
            </button>
        </div>
    </div>

    <!-- Main Laboratory Workspace -->
    <main class="max-w-[1440px] mx-auto px-5 py-5 flex-1 w-full space-y-5">

        <!-- ======================= PROTOCOL 01: LIGATION & ENCODING ======================= -->
        <section id="panel-protocol-embed" class="space-y-5">

            <!-- Simple Explanation Banner -->
            <div class="bg-[#101726] border border-[#23334d] rounded-lg p-3.5 flex items-start space-x-3 text-xs">
                <div class="text-sky-400 font-bold text-sm mt-0.5">&#9432;</div>
                <div>
                    <span class="font-semibold text-slate-200">How Step 1 Works in Plain Words:</span>
                    <p class="text-slate-400 mt-0.5 leading-relaxed">
                        1. Type your secret message and choose a password. &bull; 
                        2. The system encrypts it with military-grade AES-256. &bull; 
                        3. It converts the encrypted data into safe DNA letters (<strong class="nt-A">A</strong>, <strong class="nt-C">C</strong>, <strong class="nt-G">G</strong>, <strong class="nt-T">T</strong>) with zero errors. &bull; 
                        4. It places your secret inside real host DNA like a hidden digital vault.
                    </p>
                </div>
            </div>

            <div class="grid grid-cols-1 lg:grid-cols-12 gap-5">

                <!-- Left Column: Experiment Controls -->
                <div class="lg:col-span-5 bg-[#131926] border border-[#1f293d] rounded p-4 space-y-4">
                    <div class="flex items-center justify-between pb-2 border-b border-[#1f293d]">
                        <span class="text-xs font-mono uppercase tracking-wider text-slate-300 font-semibold">1. HIDE YOUR SECRET</span>
                        <button onclick="loadExperimentBenchSample()" class="text-[11px] font-mono text-sky-400 hover:underline">
                            Try Example Secret
                        </button>
                    </div>

                    <!-- Secret Input -->
                    <div class="space-y-1">
                        <div class="flex items-center justify-between text-xs">
                            <label class="font-medium text-slate-300">Your Secret Message or Data</label>
                            <span id="byte-counter-span" class="font-mono text-[10px] text-slate-500">0 bytes</span>
                        </div>
                        <textarea id="input-secret" rows="4" oninput="updateByteCount()" class="w-full bg-[#090d15] border border-[#1f293d] rounded p-2.5 text-xs text-slate-200 placeholder-slate-600 focus:outline-none focus:border-sky-500/80 mono lab-scroll" placeholder="Type or paste any secret message, password, coordinates, or notes here..."></textarea>
                    </div>

                    <!-- Passphrase -->
                    <div class="space-y-1">
                        <label class="block text-xs font-medium text-slate-300">Secret Password (To Lock/Unlock)</label>
                        <input id="input-password" type="password" class="w-full bg-[#090d15] border border-[#1f293d] rounded p-2 text-xs text-slate-200 placeholder-slate-600 focus:outline-none focus:border-sky-500/80 font-mono" placeholder="Enter a password to protect your secret">
                        <p class="text-[10px] font-mono text-slate-500">Protected with AES-256-GCM encryption &bull; Nobody can read it without this password</p>
                    </div>

                    <!-- Host Carrier Selection -->
                    <div class="pt-2 border-t border-[#1f293d] space-y-1.5">
                        <div class="flex items-center justify-between text-xs">
                            <label class="font-medium text-slate-300">Host DNA Sequence (Background)</label>
                            <button onclick="loadEcoliCarrier()" class="text-[11px] font-mono text-emerald-400 hover:underline">
                                Load E. coli Sample DNA
                            </button>
                        </div>
                        <textarea id="input-carrier" rows="3" class="w-full bg-[#090d15] border border-[#1f293d] rounded p-2 text-xs text-slate-400 placeholder-slate-600 focus:outline-none focus:border-sky-500/80 mono lab-scroll" placeholder="Optional: Paste existing DNA (A,C,G,T) to hide inside. Leave empty to auto-generate standard DNA."></textarea>
                    </div>

                    <!-- Insertion & Execute Action -->
                    <div class="grid grid-cols-2 gap-3 pt-2">
                        <div>
                            <label class="block text-[10px] font-mono uppercase text-slate-400 mb-1">Where to Hide in DNA</label>
                            <select id="select-locus" class="w-full bg-[#090d15] border border-[#1f293d] rounded p-2 text-xs text-slate-300 focus:outline-none">
                                <option value="center">Middle of DNA (Safest)</option>
                                <option value="append">End of DNA</option>
                            </select>
                        </div>
                        <div class="flex items-end">
                            <button onclick="runConcealmentExperiment()" id="btn-run-synthesis" class="w-full bg-[#2563eb] hover:bg-[#1d4ed8] text-white font-mono text-xs font-semibold py-2 px-3 rounded transition flex items-center justify-center gap-1.5 shadow-md">
                                <span>LOCK &amp; HIDE IN DNA</span>
                                <span>&rarr;</span>
                            </button>
                        </div>
                    </div>
                </div>

                <!-- Right Column: Interactive Genomic Map & Output -->
                <div class="lg:col-span-7 space-y-4">

                    <!-- Linear Genomic Cassette Map (Interactive SVG Locus View) -->
                    <div class="bg-[#131926] border border-[#1f293d] rounded p-4 space-y-3">
                        <div class="flex items-center justify-between pb-2 border-b border-[#1f293d]">
                            <span class="text-xs font-mono uppercase tracking-wider text-slate-300 font-semibold">DNA MAP (WHERE YOUR SECRET IS HIDDEN)</span>
                            <span id="locus-coordinates-badge" class="text-[10px] font-mono text-slate-500">READY &bull; WAITING FOR INPUT</span>
                        </div>

                        <!-- Interactive SVG Linear Map -->
                        <div class="w-full bg-[#090d15] border border-[#1f293d] rounded p-3 overflow-x-auto">
                            <svg id="svg-genomic-map" class="w-full h-20" viewBox="0 0 700 80">
                                <line x1="20" y1="40" x2="680" y2="40" stroke="#1f293d" stroke-width="4" stroke-linecap="round"></line>
                                <text x="20" y="24" fill="#475569" font-size="9" font-family="monospace">5' (Start)</text>
                                <text x="640" y="24" fill="#475569" font-size="9" font-family="monospace">3' (End)</text>

                                <rect id="svg-host-left" x="20" y="36" width="280" height="8" fill="#334155" rx="1"></rect>
                                <text id="svg-host-left-txt" x="140" y="58" fill="#64748b" font-size="9" font-family="monospace" text-anchor="middle">Normal DNA (Left)</text>

                                <g id="svg-cassette-group" opacity="0.3">
                                    <rect id="svg-fwd-primer" x="300" y="30" width="18" height="20" fill="#0284c7" rx="1"></rect>
                                    <text x="309" y="24" fill="#38bdf8" font-size="8" font-family="monospace" text-anchor="middle">Start Tag</text>

                                    <rect id="svg-insert-body" x="318" y="32" width="64" height="16" fill="#059669" rx="1"></rect>
                                    <text id="svg-insert-txt" x="350" y="60" fill="#34d399" font-size="8" font-family="monospace" text-anchor="middle">Hidden Secret DNA</text>

                                    <rect id="svg-rev-primer" x="382" y="30" width="18" height="20" fill="#7c3aed" rx="1"></rect>
                                    <text x="391" y="24" fill="#c084fc" font-size="8" font-family="monospace" text-anchor="middle">End Tag</text>
                                </g>

                                <rect id="svg-host-right" x="400" y="36" width="280" height="8" fill="#334155" rx="1"></rect>
                                <text id="svg-host-right-txt" x="540" y="58" fill="#64748b" font-size="9" font-family="monospace" text-anchor="middle">Normal DNA (Right)</text>
                            </svg>
                        </div>
                    </div>

                    <!-- Scientific Metrics Matrix -->
                    <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs font-mono">
                        <div class="bg-[#131926] border border-[#1f293d] rounded p-3">
                            <span class="text-slate-500 text-[10px]">GC BALANCE</span>
                            <div id="stat-gc" class="text-base font-semibold text-slate-100 mt-0.5">--%</div>
                            <span class="text-[10px] text-emerald-400">Target: 40-60% (Stable)</span>
                        </div>
                        <div class="bg-[#131926] border border-[#1f293d] rounded p-3">
                            <span class="text-slate-500 text-[10px]">REPEATED LETTERS</span>
                            <div id="stat-homo" class="text-base font-semibold text-slate-100 mt-0.5">&le; 2 letters</div>
                            <span class="text-[10px] text-emerald-400">Zero repeats &ge; 3</span>
                        </div>
                        <div class="bg-[#131926] border border-[#1f293d] rounded p-3">
                            <span class="text-slate-500 text-[10px]">STOP SIGNALS</span>
                            <div id="stat-stops" class="text-base font-semibold text-slate-100 mt-0.5">0</div>
                            <span class="text-[10px] text-emerald-400">Zero accidental stops</span>
                        </div>
                        <div class="bg-[#131926] border border-[#1f293d] rounded p-3">
                            <span class="text-slate-500 text-[10px]">MELTING TEMP</span>
                            <div id="stat-tm" class="text-base font-semibold text-slate-100 mt-0.5">-- &deg;C</div>
                            <span class="text-[10px] text-slate-400">Physical Stability</span>
                        </div>
                    </div>

                    <!-- Double-Stranded DNA Sequence Inspector (5'->3' and 3'->5') -->
                    <div class="bg-[#131926] border border-[#1f293d] rounded p-4 space-y-3">
                        <div class="flex items-center justify-between pb-2 border-b border-[#1f293d]">
                            <div class="flex items-center space-x-2">
                                <span class="text-xs font-mono uppercase tracking-wider text-slate-300 font-semibold">DNA DOUBLE HELIX VIEWER (TOP &amp; BOTTOM STRANDS)</span>
                                <span id="ds-strand-len-badge" class="font-mono text-[10px] text-slate-500"></span>
                            </div>
                            <div class="flex items-center space-x-2 text-xs">
                                <button onclick="saveCurrentCassetteToVault()" class="px-2.5 py-1 rounded bg-[#1b2233] hover:bg-[#232c42] border border-[#2d374d] text-slate-200 font-mono text-[11px]">
                                    Save to Library
                                </button>
                                <button onclick="copyRawFastaSequence()" class="px-2.5 py-1 rounded bg-[#1b2233] hover:bg-[#232c42] border border-[#2d374d] text-slate-200 font-mono text-[11px]">
                                    Copy DNA Letters
                                </button>
                                <button onclick="downloadFastaExport()" class="px-2.5 py-1 rounded bg-[#2563eb] hover:bg-[#1d4ed8] text-white font-mono text-[11px] font-semibold">
                                    Download .fasta File
                                </button>
                            </div>
                        </div>

                        <!-- Nucleotide Color Legend -->
                        <div class="flex items-center space-x-4 text-[11px] font-mono text-slate-400 pb-1">
                            <span><strong class="nt-A">A</strong> (Green)</span>
                            <span><strong class="nt-C">C</strong> (Blue)</span>
                            <span><strong class="nt-G">G</strong> (Yellow)</span>
                            <span><strong class="nt-T">T</strong> (Red)</span>
                        </div>

                        <!-- Formatted Color-Coded Duplex Display -->
                        <div id="duplex-viewer-box" class="w-full bg-[#090d15] border border-[#1f293d] rounded p-3 text-xs font-mono lab-scroll max-h-48 overflow-y-auto whitespace-pre leading-relaxed select-all">
<span class="text-slate-600">// Your DNA sequence will appear here once you click "LOCK &amp; HIDE IN DNA".
// It displays both the top sense strand and the matching bottom antisense strand.</span>
                        </div>

                        <!-- Raw FASTA Sequence Text (Collapsible) -->
                        <details class="text-xs font-mono text-slate-400">
                            <summary class="cursor-pointer hover:text-slate-200">View Raw Standard FASTA File Format</summary>
                            <textarea id="raw-fasta-area" readonly rows="5" class="w-full mt-2 bg-[#090d15] border border-[#1f293d] rounded p-2 text-[11px] text-slate-300 mono lab-scroll select-all"></textarea>
                        </details>
                    </div>

                </div>
            </div>
        </section>

        <!-- ======================= PROTOCOL 02: IN-SILICO PCR & EXTRACTION ======================= -->
        <section id="panel-protocol-extract" class="hidden space-y-5">

            <!-- Simple Explanation Banner -->
            <div class="bg-[#101726] border border-[#23334d] rounded-lg p-3.5 flex items-start space-x-3 text-xs">
                <div class="text-sky-400 font-bold text-sm mt-0.5">&#9432;</div>
                <div>
                    <span class="font-semibold text-slate-200">How Step 2 Works in Plain Words:</span>
                    <p class="text-slate-400 mt-0.5 leading-relaxed">
                        1. Paste the DNA sequence or drag and drop your DNA file. &bull; 
                        2. The system scans the DNA to find your hidden section using the start and end tags. &bull; 
                        3. Enter the secret password you used during Step 1. &bull; 
                        4. It decrypts the letters and restores your exact original text or file with 100% accuracy.
                    </p>
                </div>
            </div>

            <div class="grid grid-cols-1 lg:grid-cols-12 gap-5">

                <!-- Left Column -->
                <div class="lg:col-span-5 bg-[#131926] border border-[#1f293d] rounded p-4 space-y-4">
                    <div class="pb-2 border-b border-[#1f293d]">
                        <span class="text-xs font-mono uppercase tracking-wider text-slate-300 font-semibold">2. RECOVER YOUR HIDDEN SECRET</span>
                        <p class="text-[11px] text-slate-500 font-mono mt-0.5">Locate hidden DNA section &rarr; Translate DNA letters &rarr; Unlock secret</p>
                    </div>

                    <!-- Drag & Drop Zone -->
                    <div class="space-y-1.5">
                        <div class="flex items-center justify-between text-xs font-mono">
                            <label class="text-slate-300">DNA Sequence with Hidden Secret</label>
                            <button onclick="toggleVaultDrawer()" class="text-sky-400 hover:underline">Select from Saved Library</button>
                        </div>

                        <div id="pcr-drop-target" ondragover="handleDragOver(event)" ondragleave="handleDragLeave(event)" ondrop="handleDrop(event)" onclick="document.getElementById('hidden-pcr-file').click()" class="border border-dashed border-[#2f3e5c] hover:border-sky-500 bg-[#090d15] rounded p-3 text-center cursor-pointer transition">
                            <input type="file" id="hidden-pcr-file" onchange="handleFileSelect(event)" class="hidden" accept=".fasta,.fa,.txt">
                            <span class="text-xs font-mono text-slate-300 block">Click or Drop your .fasta / .txt DNA file here</span>
                            <span class="text-[10px] font-mono text-slate-500">Automatically cleans and prepares the DNA for reading</span>
                        </div>

                        <textarea id="extract-input-seq" rows="6" class="w-full bg-[#090d15] border border-[#1f293d] rounded p-2.5 text-xs text-slate-200 placeholder-slate-600 focus:outline-none focus:border-sky-500/80 mono lab-scroll" placeholder="Or paste the full DNA sequence (A, C, G, T) here..."></textarea>
                    </div>

                    <!-- Password -->
                    <div class="space-y-1">
                        <label class="block text-xs font-medium text-slate-300">Secret Password</label>
                        <input id="extract-input-pass" type="password" class="w-full bg-[#090d15] border border-[#1f293d] rounded p-2 text-xs text-slate-200 placeholder-slate-600 focus:outline-none focus:border-sky-500/80 font-mono" placeholder="Enter the password used when hiding this secret">
                    </div>

                    <button onclick="runExtractionExperiment()" id="btn-run-extraction" class="w-full bg-[#2563eb] hover:bg-[#1d4ed8] text-white font-mono text-xs font-semibold py-2 px-3 rounded transition flex items-center justify-center gap-1.5 shadow-md">
                        <span>FIND &amp; UNLOCK SECRET</span>
                        <span>&rarr;</span>
                    </button>
                </div>

                <!-- Right Column: Extracted Payload -->
                <div class="lg:col-span-7 space-y-4">
                    <div id="extract-idle-view" class="h-full min-h-[360px] flex flex-col items-center justify-center border border-dashed border-[#1f293d] rounded p-8 text-center text-slate-500 bg-[#131926]">
                        <svg class="w-8 h-8 text-slate-600 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"></path></svg>
                        <span class="text-xs font-mono uppercase tracking-wider text-slate-400">AWAITING DNA INPUT</span>
                        <p class="text-xs text-slate-600 max-w-sm mt-1">Provide the DNA sequence and secret password on the left to extract and unlock your hidden message.</p>
                    </div>

                    <div id="extract-active-view" class="hidden bg-[#131926] border border-[#1f293d] rounded p-4 space-y-4">
                        <div class="flex items-center justify-between pb-2 border-b border-[#1f293d]">
                            <div class="flex items-center space-x-2">
                                <span class="w-2 h-2 rounded-full bg-emerald-400"></span>
                                <span class="text-xs font-mono font-bold text-emerald-400 uppercase tracking-wider">SECRET RECOVERED &bull; 100% PERFECT MATCH</span>
                            </div>
                            <span id="extract-byte-badge" class="font-mono text-[11px] text-slate-400"></span>
                        </div>

                        <div>
                            <span class="text-xs font-mono text-slate-400 block mb-1">YOUR ORIGINAL SECRET MESSAGE:</span>
                            <div class="p-3 bg-[#090d15] border border-[#1f293d] rounded">
                                <pre id="extract-text-display" class="text-xs text-slate-100 whitespace-pre-wrap font-mono lab-scroll"></pre>
                            </div>
                        </div>

                        <div class="flex items-center justify-between pt-1 text-xs font-mono text-slate-500">
                            <span>Integrity Check: PASS (Zero data lost or altered)</span>
                            <button onclick="copyExtractedPayload()" class="px-3 py-1 bg-[#1e293b] hover:bg-[#2d3a52] text-slate-200 rounded">
                                Copy Secret Message
                            </button>
                        </div>
                    </div>
                </div>

            </div>
        </section>
        <!-- ======================= PROTOCOL 03: VIRTUAL AGAROSE GEL ELECTROPHORESIS ======================= -->
        <section id="panel-protocol-gel" class="hidden space-y-5">

            <!-- Simple Explanation Banner -->
            <div class="bg-[#101726] border border-[#23334d] rounded-lg p-3.5 flex items-start space-x-3 text-xs">
                <div class="text-sky-400 font-bold text-sm mt-0.5">&#9432;</div>
                <div>
                    <span class="font-semibold text-slate-200">How Step 3 Works in Plain Words:</span>
                    <p class="text-slate-400 mt-0.5 leading-relaxed">
                        In biology labs, scientists use "Gel Electrophoresis" under UV light to measure DNA size. Smaller pieces run faster and travel lower down the gel. 
                        This virtual tank compares your hidden DNA piece against a standard 1,000-base-pair ruler so you can physically verify its size.
                    </p>
                </div>
            </div>

            <div class="bg-[#131926] border border-[#1f293d] rounded p-4 space-y-4">
                <div class="flex items-center justify-between pb-2 border-b border-[#1f293d]">
                    <div>
                        <span class="text-xs font-mono uppercase tracking-wider text-slate-300 font-semibold">3. VIRTUAL GEL SIZE TEST</span>
                        <p class="text-[11px] text-slate-500 font-mono mt-0.5">Simulated Agarose Gel with 1 kb DNA Reference Ladder under UV light</p>
                    </div>
                    <span class="text-[11px] font-mono text-sky-400">UV LIGHT: ON</span>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-12 gap-5">
                    <div class="md:col-span-5 bg-[#070a10] border border-[#1f293d] rounded p-4 flex flex-col items-center">
                        <div class="w-full flex justify-between text-[10px] font-mono text-slate-500 pb-2 border-b border-[#1f293d]/50">
                            <span>WELL 1: DNA RULER</span>
                            <span>WELL 2: YOUR SECRET DNA</span>
                        </div>

                        <div class="w-full h-80 gel-lane relative flex justify-around px-6 py-4 mt-2 rounded border border-[#1e293b]/60">
                            <div class="w-16 h-full relative flex flex-col items-center">
                                <div class="w-10 h-1.5 bg-[#1f293d] rounded-t mb-2"></div>
                                <div class="w-12 h-1 gel-band-ladder absolute top-8" title="1,500 bp"><span class="text-[9px] font-mono text-slate-500 absolute -left-8 -top-1">1.5kb</span></div>
                                <div class="w-12 h-1 gel-band-ladder absolute top-16" title="1,000 bp"><span class="text-[9px] font-mono text-slate-500 absolute -left-8 -top-1">1.0kb</span></div>
                                <div class="w-12 h-1 gel-band-ladder absolute top-28" title="750 bp"><span class="text-[9px] font-mono text-slate-500 absolute -left-8 -top-1">750bp</span></div>
                                <div class="w-12 h-1.5 gel-band-ladder absolute top-40 opacity-90" title="500 bp (Reference)"><span class="text-[9px] font-mono text-sky-400 absolute -left-8 -top-1">500bp</span></div>
                                <div class="w-12 h-1 gel-band-ladder absolute top-52" title="250 bp"><span class="text-[9px] font-mono text-slate-500 absolute -left-8 -top-1">250bp</span></div>
                                <div class="w-12 h-1 gel-band-ladder absolute top-64" title="100 bp"><span class="text-[9px] font-mono text-slate-500 absolute -left-8 -top-1">100bp</span></div>
                            </div>

                            <div class="w-16 h-full relative flex flex-col items-center">
                                <div class="w-10 h-1.5 bg-[#1f293d] rounded-t mb-2"></div>
                                <div id="gel-amplicon-band" class="w-14 h-2 gel-band absolute transition-all duration-500" style="top: 130px;"></div>
                            </div>
                        </div>

                        <div class="w-full flex justify-between text-[10px] font-mono text-slate-500 pt-2 border-t border-[#1f293d]/50 mt-2">
                            <span>Top (-) Start</span>
                            <span>Bottom (+) End</span>
                        </div>
                    </div>

                    <div class="md:col-span-7 space-y-4">
                        <div class="grid grid-cols-3 gap-3 text-xs font-mono">
                            <div class="bg-[#090d15] border border-[#1f293d] rounded p-3">
                                <span class="text-slate-500 text-[10px]">TOTAL FRAGMENT SIZE</span>
                                <div id="gel-stat-size" class="text-base font-semibold text-sky-400 mt-0.5">-- bp</div>
                                <span class="text-[10px] text-slate-500">Secret + 36 bp tags</span>
                            </div>
                            <div class="bg-[#090d15] border border-[#1f293d] rounded p-3">
                                <span class="text-slate-500 text-[10px]">START TAG TEMP</span>
                                <div id="gel-stat-fwd-tm" class="text-base font-semibold text-slate-200 mt-0.5">48.0 &deg;C</div>
                                <span class="text-[10px] text-slate-500">18 letters (50% GC)</span>
                            </div>
                            <div class="bg-[#090d15] border border-[#1f293d] rounded p-3">
                                <span class="text-slate-500 text-[10px]">END TAG TEMP</span>
                                <div id="gel-stat-rev-tm" class="text-base font-semibold text-slate-200 mt-0.5">48.0 &deg;C</div>
                                <span class="text-[10px] text-slate-500">18 letters (50% GC)</span>
                            </div>
                        </div>

                        <div class="bg-[#090d15] border border-[#1f293d] rounded p-3 space-y-2 text-xs font-mono">
                            <span class="text-slate-400 font-semibold block pb-1 border-b border-[#1f293d]">SPECIAL DNA TAGS (USED TO LOCATE YOUR SECRET):</span>
                            <div class="flex justify-between py-1">
                                <span class="text-slate-400">Start Tag (Forward Primer):</span>
                                <span class="text-sky-400 font-semibold">5'- ATCGTTAGGCTACGATCG -3'</span>
                            </div>
                            <div class="flex justify-between py-1">
                                <span class="text-slate-400">End Tag (Reverse Primer):</span>
                                <span class="text-purple-400 font-semibold">5'- CGATCGTAGCCTAACGAT -3'</span>
                            </div>
                            <div class="flex justify-between py-1 border-t border-[#1f293d] text-[11px] text-slate-500">
                                <span>Lab Heating Temperature (Ta):</span>
                                <span class="text-emerald-400">43.0 &deg;C (Perfect for reading)</span>
                            </div>
                        </div>

                        <div class="bg-[#090d15] border border-[#1f293d] rounded p-3 space-y-2">
                            <label class="block text-xs font-mono text-slate-300">Test Any DNA Sequence on the Virtual Gel:</label>
                            <textarea id="gel-input-seq" rows="3" class="w-full bg-[#0d121c] border border-[#1f293d] rounded p-2 text-xs text-slate-200 mono lab-scroll" placeholder="Paste any DNA sequence containing the start and end tags..."></textarea>
                            <button onclick="runGelSimulationFromInput()" class="px-3 py-1.5 bg-[#2563eb] hover:bg-[#1d4ed8] text-white font-mono text-xs rounded transition shadow">
                                Run Gel Test
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </section>

        <!-- ======================= PROTOCOL 04: BIOPHYSICAL AUDIT ======================= -->
        <section id="panel-protocol-audit" class="hidden space-y-5">

            <!-- Simple Explanation Banner -->
            <div class="bg-[#101726] border border-[#23334d] rounded-lg p-3.5 flex items-start space-x-3 text-xs">
                <div class="text-sky-400 font-bold text-sm mt-0.5">&#9432;</div>
                <div>
                    <span class="font-semibold text-slate-200">How Step 4 Works in Plain Words:</span>
                    <p class="text-slate-400 mt-0.5 leading-relaxed">
                        To survive inside a living organism or long-term freezer storage, DNA must follow biological rules:
                        <strong>1. GC content between 40% and 60%</strong> (prevents DNA from melting or folding into knots). 
                        <strong>2. No repeats of 3+ identical letters</strong> (like AAAA or GGGG which confuse DNA readers). 
                        <strong>3. No accidental stop signals</strong> (TAA, TAG, TGA). This audit checks that your DNA passes all tests.
                    </p>
                </div>
            </div>

            <div class="bg-[#131926] border border-[#1f293d] rounded p-4 space-y-4">
                <div class="pb-2 border-b border-[#1f293d]">
                    <span class="text-xs font-mono uppercase tracking-wider text-slate-300 font-semibold">4. DNA HEALTH &amp; SAFETY AUDIT</span>
                    <p class="text-[11px] text-slate-500 font-mono mt-0.5">Automated quality check against biological rules</p>
                </div>

                <div class="flex flex-col sm:flex-row gap-3">
                    <textarea id="audit-input-box" rows="3" class="flex-1 bg-[#090d15] border border-[#1f293d] rounded p-2.5 text-xs text-slate-200 placeholder-slate-600 focus:outline-none focus:border-sky-500/80 mono lab-scroll" placeholder="Paste any DNA sequence (A, C, G, T) to test if it's healthy and viable..."></textarea>
                    <button onclick="runAuditEvaluation()" class="px-4 py-2 bg-[#2563eb] hover:bg-[#1d4ed8] text-white font-mono text-xs font-semibold rounded transition self-end sm:self-stretch shadow">
                        CHECK DNA HEALTH
                    </button>
                </div>

                <div id="audit-gc-graph-box" class="hidden bg-[#090d15] border border-[#1f293d] rounded p-4 space-y-2">
                    <div class="flex items-center justify-between text-xs font-mono">
                        <span class="text-slate-300 font-semibold">GC STABILITY GRAPH (50 bp WINDOW)</span>
                        <span class="text-emerald-400">SAFE GREEN ZONE: 40% TO 60% GC</span>
                    </div>

                    <div class="w-full h-32 bg-[#060910] border border-[#1e293b] rounded relative p-2">
                        <div class="absolute left-0 right-0 top-[40%] bottom-[40%] bg-emerald-950/20 border-y border-emerald-500/30"></div>
                        <span class="absolute left-3 top-2 text-[9px] font-mono text-slate-600">100% GC</span>
                        <span class="absolute left-3 top-[38%] text-[9px] font-mono text-emerald-500">60%</span>
                        <span class="absolute left-3 top-[58%] text-[9px] font-mono text-emerald-500">40%</span>
                        <span class="absolute left-3 bottom-2 text-[9px] font-mono text-slate-600">0% GC</span>

                        <svg id="svg-gc-sparkline" class="w-full h-full" preserveAspectRatio="none" viewBox="0 0 100 100">
                            <path id="svg-gc-path" d="" fill="none" stroke="#38bdf8" stroke-width="1.5"></path>
                        </svg>
                    </div>
                </div>

                <div id="audit-output-metrics" class="hidden"></div>
            </div>
        </section>

                        <svg id="svg-gc-sparkline" class="w-full h-full" preserveAspectRatio="none" viewBox="0 0 100 100">
                            <path id="svg-gc-path" d="" fill="none" stroke="#38bdf8" stroke-width="1.5"></path>
                        </svg>
                    </div>
                </div>

                <div id="audit-output-metrics" class="hidden"></div>
            </div>
        </section>

    </main>

    <!-- Drawer: Genomic Locus Registry -->
    <div id="vault-drawer" class="hidden fixed inset-0 z-50 bg-black/70 backdrop-blur-xs flex items-center justify-center p-4">
        <div class="bg-[#131926] border border-[#1f293d] rounded-lg max-w-xl w-full p-5 space-y-4 shadow-2xl">
            <div class="flex items-center justify-between pb-3 border-b border-[#1f293d]">
                <div>
                    <h3 class="text-xs font-mono uppercase tracking-wider text-slate-200 font-bold">GENOMIC LOCUS REGISTRY</h3>
                    <p class="text-[11px] text-slate-500 font-mono">Client-side persistent sequence repository</p>
                </div>
                <button onclick="toggleVaultDrawer()" class="text-slate-400 hover:text-white text-base">&times;</button>
            </div>

            <div id="vault-records-box" class="space-y-2 max-h-72 overflow-y-auto lab-scroll text-xs font-mono"></div>

            <div class="flex justify-end pt-2 border-t border-[#1f293d]">
                <button onclick="toggleVaultDrawer()" class="px-3 py-1.5 bg-[#1e293b] hover:bg-[#2d3a52] text-slate-200 text-xs font-mono rounded">
                    Close Registry
                </button>
            </div>
        </div>
    </div>

    <!-- Institutional Lab Footer -->
    <footer class="border-t border-[#1f293d] py-4 text-center text-xs text-slate-500 bg-[#0c111a] font-mono">
        BIOCRYPT MOLECULAR GENOMICS WORKSTATION &bull; ISO-COMPLIANT COMPUTATIONAL STEGANOGRAPHY
    </footer>

    <!-- Client-Side Controller -->
    <script>
        function showLabToast(message, type = 'info') {
            const shelf = document.getElementById('toast-shelf');
            const toast = document.createElement('div');
            const colorClass = type === 'success' ? 'bg-[#062419] border-emerald-500/50 text-emerald-300' :
                               type === 'error' ? 'bg-[#290a0f] border-rose-500/50 text-rose-300' :
                               'bg-[#101726] border-slate-700 text-slate-200';

            toast.className = `pointer-events-auto px-4 py-2.5 rounded border text-xs font-mono shadow-xl transition-all duration-300 flex items-center gap-2 ${colorClass}`;
            toast.innerHTML = `<span>&bull;</span><span>${message}</span>`;
            shelf.appendChild(toast);

            setTimeout(() => {
                toast.style.opacity = '0';
                setTimeout(() => toast.remove(), 300);
            }, 3500);
        }

        function switchTab(protocolId) {
            ['embed', 'extract', 'gel', 'audit'].forEach(p => {
                document.getElementById('panel-protocol-' + p).classList.add('hidden');
                const btn = document.getElementById('btn-tab-' + p);
                btn.className = "px-4 py-2 rounded font-medium text-slate-400 hover:text-slate-200 transition flex items-center gap-2";
            });
            document.getElementById('panel-' + protocolId).classList.remove('hidden');
            const activeBtn = document.getElementById('btn-tab-' + protocolId.replace('protocol-', ''));
            if (activeBtn) {
                activeBtn.className = "px-4 py-2 rounded font-medium text-white bg-[#192233] border border-[#2a3752] transition flex items-center gap-2";
            }
        }

        function updateByteCount() {
            const val = document.getElementById('input-secret').value;
            const bytes = new TextEncoder().encode(val).length;
            document.getElementById('byte-counter-span').innerText = bytes.toLocaleString() + " bytes";
        }

        function loadExperimentBenchSample() {
            document.getElementById('input-secret').value = "CONFIDENTIAL BENCHMARK: Synthetically disguised payload inserted at coordinate 22.307 N. Zero homopolymers certified.";
            document.getElementById('input-password').value = "AcademicBenchKey2026!#";
            loadEcoliCarrier();
            updateByteCount();
            showLabToast("Benchmark control sample loaded.", "info");
        }

        function loadEcoliCarrier() {
            const unit = "GCTGATCGATCGTACGATCGATCGATCGATCGTAGCTAGCTAGCTAGCATCGATCGATCGATC\\n";
            document.getElementById('input-carrier').value = ">NC_000913.3 Escherichia coli str. K-12 substr. MG1655 reference fragment\\n" + unit.repeat(15);
        }

        function renderDuplexSequence(sequence, maxBases = 300) {
            const comp = { 'A': 'T', 'T': 'A', 'C': 'G', 'G': 'C' };
            const clean = sequence.replace(/[^ATCGatcg]/g, '').toUpperCase();
            const slice = clean.slice(0, maxBases);

            let lines = [];
            for (let i = 0; i < slice.length; i += 60) {
                const chunk = slice.slice(i, i + 60);
                const coord = String(i + 1).padStart(5, '0');

                let senseColored = "";
                let antiColored = "";
                for (let ch of chunk) {
                    const c = ch.toUpperCase();
                    senseColored += `<span class="nt-${c}">${c}</span>`;
                    antiColored += `<span class="nt-${comp[c] || 'N'}">${comp[c] || 'N'}</span>`;
                }

                lines.push(`${coord}  5'- ${senseColored} -3'`);
                lines.push(`       3'- ${antiColored} -5'`);
                lines.push("");
            }

            if (clean.length > maxBases) {
                lines.push(`... [Truncated for display: ${clean.length - maxBases} bp additional downstream bases in sequence]`);
            }

            document.getElementById('duplex-viewer-box').innerHTML = lines.join('\\n');
        }

        async function runConcealmentExperiment() {
            const secret = document.getElementById('input-secret').value.trim();
            const password = document.getElementById('input-password').value.trim();
            const carrier = document.getElementById('input-carrier').value.trim();
            const locus = document.getElementById('select-locus').value;

            if (!secret) {
                showLabToast("Payload stream cannot be empty.", "error");
                return;
            }
            if (!password) {
                showLabToast("Passphrase is required for AES-256-GCM key derivation.", "error");
                return;
            }

            const btn = document.getElementById('btn-run-synthesis');
            btn.disabled = true;
            btn.innerHTML = `<span>SYNTHESIZING...</span>`;

            try {
                const res = await fetch('/api/conceal', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ secret_text: secret, password: password, carrier_fasta: carrier || null, locus: locus })
                });
                const data = await res.json();
                if (!res.ok) throw new Error(data.detail || "Synthesis failure.");

                document.getElementById('stat-gc').innerText = data.metrics.gc_percent + "%";
                document.getElementById('stat-homo').innerText = "Max " + data.metrics.max_homopolymer_run + " bp";
                document.getElementById('stat-stops').innerText = data.metrics.in_frame_stops_count;
                document.getElementById('stat-tm').innerText = data.metrics.melting_temperature_tm + " °C";
                document.getElementById('ds-strand-len-badge').innerText = data.stego_length.toLocaleString() + " bp duplex";

                document.getElementById('raw-fasta-area').value = data.stego_fasta;
                renderDuplexSequence(data.stego_sequence);

                const coords = data.coordinates;
                document.getElementById('locus-coordinates-badge').innerText = `LOCUS: POS ${coords.fwd_start} &rarr; ${coords.rev_end} (${coords.payload_length} bp insert)`;
                document.getElementById('svg-cassette-group').setAttribute('opacity', '1.0');
                document.getElementById('svg-insert-txt').textContent = `${coords.payload_length} bp Insert`;

                updateGelElectrophoresisBand(coords.payload_length + 36);

                showLabToast("Genomic cassette successfully synthesized.", "success");

            } catch (err) {
                showLabToast(err.message, "error");
            } finally {
                btn.disabled = false;
                btn.innerHTML = `<span>SYNTHESIZE CASSETTE</span><span>&rarr;</span>`;
            }
        }

        function updateGelElectrophoresisBand(ampliconLength) {
            const minSize = 100, maxSize = 2000;
            const clamped = Math.min(maxSize, Math.max(minSize, ampliconLength));
            const logMin = Math.log(minSize);
            const logMax = Math.log(maxSize);
            const factor = (Math.log(clamped) - logMin) / (logMax - logMin);
            const topPx = Math.round(260 - factor * 220);

            const band = document.getElementById('gel-amplicon-band');
            band.style.top = topPx + 'px';
            document.getElementById('gel-stat-size').innerText = ampliconLength.toLocaleString() + " bp";
        }

        function runGelSimulationFromInput() {
            const seq = document.getElementById('gel-input-seq').value.trim();
            if (!seq) {
                showLabToast("Please provide sequence for PCR gel hybridization.", "error");
                return;
            }
            fetch('/api/simulate-pcr', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ sequence: seq })
            })
            .then(r => r.json())
            .then(data => {
                if (data.success) {
                    updateGelElectrophoresisBand(data.amplicon_length);
                    document.getElementById('gel-stat-fwd-tm').innerText = data.fwd_tm + " °C";
                    document.getElementById('gel-stat-rev-tm').innerText = data.rev_tm + " °C";
                    showLabToast(`Gel exposed: ${data.amplicon_length} bp amplicon band detected.`, "success");
                } else {
                    showLabToast(data.detail || "PCR failed.", "error");
                }
            })
            .catch(err => showLabToast(err.message, "error"));
        }

        async function runExtractionExperiment() {
            const seq = document.getElementById('extract-input-seq').value.trim();
            const pass = document.getElementById('extract-input-pass').value.trim();

            if (!seq || !pass) {
                showLabToast("Both carrier sequence and passphrase required.", "error");
                return;
            }

            const btn = document.getElementById('btn-run-extraction');
            btn.disabled = true;
            btn.innerHTML = `<span>AMPLIFYING &amp; EXTRACTING...</span>`;

            try {
                const res = await fetch('/api/extract', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ stego_fasta: seq, password: pass })
                });
                const data = await res.json();
                if (!res.ok) throw new Error(data.detail || "Extraction failed.");

                document.getElementById('extract-idle-view').classList.add('hidden');
                document.getElementById('extract-active-view').classList.remove('hidden');

                document.getElementById('extract-text-display').innerText = data.recovered_text;
                document.getElementById('extract-byte-badge').innerText = data.byte_length.toLocaleString() + " bytes verified";

                showLabToast("Authentication verified: payload recovered.", "success");

            } catch (err) {
                showLabToast(err.message, "error");
            } finally {
                btn.disabled = false;
                btn.innerHTML = `<span>ANNEAL PRIMERS &amp; EXTRACT</span><span>&rarr;</span>`;
            }
        }

        function handleDragOver(e) {
            e.preventDefault();
            document.getElementById('pcr-drop-target').classList.add('border-sky-400');
        }
        function handleDragLeave(e) {
            e.preventDefault();
            document.getElementById('pcr-drop-target').classList.remove('border-sky-400');
        }
        function handleDrop(e) {
            e.preventDefault();
            document.getElementById('pcr-drop-target').classList.remove('border-sky-400');
            if (e.dataTransfer.files.length) {
                loadSequenceFile(e.dataTransfer.files[0]);
            }
        }
        function handleFileSelect(e) {
            if (e.target.files.length) {
                loadSequenceFile(e.target.files[0]);
            }
        }
        function loadSequenceFile(file) {
            const reader = new FileReader();
            reader.onload = (evt) => {
                document.getElementById('extract-input-seq').value = evt.target.result;
                showLabToast(`Ingested file: ${file.name}`, "info");
            };
            reader.readAsText(file);
        }

        async function runAuditEvaluation() {
            const seq = document.getElementById('audit-input-box').value.trim();
            if (!seq) {
                showLabToast("Target sequence required.", "error");
                return;
            }

            try {
                const res = await fetch('/api/audit', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ sequence: seq })
                });
                const data = await res.json();
                if (!res.ok) throw new Error(data.detail || "Audit execution failed.");

                const m = data.metrics;
                const points = data.sliding_gc_points || [];

                if (points.length > 1) {
                    let d = "";
                    const step = 100 / (points.length - 1);
                    points.forEach((pt, i) => {
                        const x = (i * step).toFixed(2);
                        const y = (100 - pt).toFixed(2);
                        d += (i === 0 ? `M ${x} ${y}` : ` L ${x} ${y}`);
                    });
                    document.getElementById('svg-gc-path').setAttribute('d', d);
                    document.getElementById('audit-gc-graph-box').classList.remove('hidden');
                }

                let html = `
                    <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs font-mono mt-3">
                        <div class="p-3 bg-[#090d15] rounded border border-[#1f293d]">
                            <span class="text-slate-500 text-[10px]">GLOBAL GC</span>
                            <div class="text-sm font-semibold text-slate-100 mt-0.5">${m.gc_percent}%</div>
                            <span class="text-[10px] text-slate-500">Min/Max: ${m.sliding_gc_min}% - ${m.sliding_gc_max}%</span>
                        </div>
                        <div class="p-3 bg-[#090d15] rounded border border-[#1f293d]">
                            <span class="text-slate-500 text-[10px]">HOMOPOLYMER RUN</span>
                            <div class="text-sm font-semibold ${m.max_homopolymer_run <= 2 ? 'text-emerald-400' : 'text-amber-400'} mt-0.5">${m.max_homopolymer_run} bp</div>
                            <span class="text-[10px] text-slate-500">Violations: ${m.homopolymer_violations_count}</span>
                        </div>
                        <div class="p-3 bg-[#090d15] rounded border border-[#1f293d]">
                            <span class="text-slate-500 text-[10px]">IN-FRAME STOPS</span>
                            <div class="text-sm font-semibold ${m.in_frame_stops_count === 0 ? 'text-emerald-400' : 'text-rose-400'} mt-0.5">${m.in_frame_stops_count}</div>
                            <span class="text-[10px] text-slate-500">Sliding: ${m.sliding_stops_count}</span>
                        </div>
                        <div class="p-3 bg-[#090d15] rounded border border-[#1f293d]">
                            <span class="text-slate-500 text-[10px]">SHANNON ENTROPY</span>
                            <div class="text-sm font-semibold text-sky-400 mt-0.5">${m.shannon_entropy}</div>
                            <span class="text-[10px] text-slate-500">Bits per nucleotide</span>
                        </div>
                    </div>
                `;

                const out = document.getElementById('audit-output-metrics');
                out.innerHTML = html;
                out.classList.remove('hidden');

                showLabToast("Biophysical diagnostics updated.", "success");

            } catch (err) {
                showLabToast(err.message, "error");
            }
        }

        function getVault() {
            try { return JSON.parse(localStorage.getItem('biocrypt_locus_registry') || '[]'); }
            catch { return []; }
        }
        function saveVault(items) {
            localStorage.setItem('biocrypt_locus_registry', JSON.stringify(items));
            updateVaultPill();
        }
        function updateVaultPill() {
            document.getElementById('vault-pill-count').innerText = getVault().length;
        }
        function toggleVaultDrawer() {
            const d = document.getElementById('vault-drawer');
            if (d.classList.contains('hidden')) {
                renderVaultRecords();
                d.classList.remove('hidden');
            } else {
                d.classList.add('hidden');
            }
        }
        function saveCurrentCassetteToVault() {
            const fasta = document.getElementById('raw-fasta-area').value;
            if (!fasta) return;
            const label = prompt("Enter registration identifier for this locus:", "Synthetic_Cassette_" + new Date().toISOString().slice(0, 10));
            if (!label) return;

            const v = getVault();
            v.unshift({ label, fasta, timestamp: new Date().toLocaleTimeString() });
            saveVault(v);
            showLabToast("Locus registered in vault.", "success");
        }
        function renderVaultRecords() {
            const v = getVault();
            const box = document.getElementById('vault-records-box');
            if (!v.length) {
                box.innerHTML = `<div class="text-slate-500 text-center py-6">No sequence records registered.</div>`;
                return;
            }
            box.innerHTML = v.map((item, idx) => `
                <div class="p-3 bg-[#090d15] border border-[#1f293d] rounded flex items-center justify-between">
                    <div>
                        <div class="text-slate-200 font-semibold">${item.label}</div>
                        <div class="text-[10px] text-slate-500">${item.timestamp} &bull; ${item.fasta.length} chars</div>
                    </div>
                    <div class="flex items-center space-x-1.5">
                        <button onclick="loadVaultIntoExtract(${idx})" class="px-2 py-1 bg-[#1e293b] hover:bg-[#2e3e5c] text-slate-200 rounded text-[11px]">Load</button>
                        <button onclick="deleteVaultItem(${idx})" class="px-2 py-1 bg-rose-950/40 text-rose-300 rounded text-[11px]">Delete</button>
                    </div>
                </div>
            `).join('');
        }
        function loadVaultIntoExtract(idx) {
            const item = getVault()[idx];
            if (item) {
                document.getElementById('extract-input-seq').value = item.fasta;
                toggleVaultDrawer();
                switchTab('protocol-extract');
                showLabToast(`Loaded "${item.label}" into PCR chamber.`, "info");
            }
        }
        function deleteVaultItem(idx) {
            const v = getVault();
            v.splice(idx, 1);
            saveVault(v);
            renderVaultRecords();
        }

        function copyRawFastaSequence() {
            const area = document.getElementById('raw-fasta-area');
            area.select();
            navigator.clipboard.writeText(area.value);
            showLabToast("Raw FASTA sequence copied.", "success");
        }
        function copyExtractedPayload() {
            const txt = document.getElementById('extract-text-display').innerText;
            navigator.clipboard.writeText(txt);
            showLabToast("Payload copied to clipboard.", "success");
        }
        function downloadFastaExport() {
            const fasta = document.getElementById('raw-fasta-area').value;
            const blob = new Blob([fasta], { type: 'text/plain' });
            const a = document.createElement('a');
            a.href = URL.createObjectURL(blob);
            a.download = 'biocrypt_cassette.fasta';
            a.click();
            showLabToast("FASTA export downloaded.", "success");
        }

        updateVaultPill();
    </script>
</body>
</html>
"""

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=False)

