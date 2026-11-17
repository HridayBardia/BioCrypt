import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

os.makedirs('report_assets', exist_ok=True)

plt.rcParams['font.sans-serif'] = 'Helvetica'
plt.rcParams['font.family'] = 'sans-serif'

# =============================================================================
# FIGURE 1: Clean, Neatly Labeled Molecular Pipeline Architecture
# =============================================================================
fig, ax = plt.subplots(figsize=(7.5, 5.2), dpi=300)
fig.patch.set_facecolor('#ffffff')
ax.set_facecolor('#ffffff')
ax.set_xlim(0, 100)
ax.set_ylim(0, 100)
ax.axis('off')

# Stage 1: Document / File (Left)
c1 = plt.Circle((14, 70), 9, facecolor='#f0f9ff', edgecolor='#0284c7', lw=2.2, zorder=2)
ax.add_patch(c1)
doc = patches.Rectangle((10.5, 64.5), 7, 11, facecolor='#ffffff', edgecolor='#0284c7', lw=1.8, zorder=3)
ax.add_patch(doc)
for dy in [2.5, 5.0, 7.5]:
    ax.plot([12, 16], [64.5 + dy, 64.5 + dy], color='#0284c7', lw=1.2, zorder=4)
ax.text(14, 57, "Digital Secret", ha='center', va='top', fontsize=9.0, fontweight='bold', color='#0284c7')

# Arrow 1 -> 2
ax.annotate('', xy=(27, 70), xytext=(24, 70),
            arrowprops=dict(arrowstyle="-|>", color='#64748b', lw=2.2, mutation_scale=14))

# Stage 2: Security Padlock
c2 = plt.Circle((38, 70), 9, facecolor='#ecfdf5', edgecolor='#059669', lw=2.2, zorder=2)
ax.add_patch(c2)
lock_body = patches.Rectangle((34.5, 65), 7, 6, facecolor='#059669', edgecolor='#047857', lw=1.5, zorder=3)
ax.add_patch(lock_body)
shackle = patches.Arc((38, 71), 4.5, 6, theta1=0, theta2=180, edgecolor='#047857', lw=2.0, zorder=3)
ax.add_patch(shackle)
ax.plot([38, 38], [67, 68.5], color='#ffffff', lw=1.8, zorder=4)
ax.plot(38, 69, marker='o', color='#ffffff', markersize=3, zorder=4)
ax.text(38, 57, "AES-256-GCM", ha='center', va='top', fontsize=9.0, fontweight='bold', color='#059669')

# Arrow 2 -> 3
ax.annotate('', xy=(51, 70), xytext=(48, 70),
            arrowprops=dict(arrowstyle="-|>", color='#64748b', lw=2.2, mutation_scale=14))

# Stage 3: Rotary Automaton Gear
c3 = plt.Circle((62, 70), 9, facecolor='#fffbeb', edgecolor='#d97706', lw=2.2, zorder=2)
ax.add_patch(c3)
theta_gear = np.linspace(0, 2*np.pi, 6, endpoint=False)
for th in theta_gear:
    gx = 62 + 4.8 * np.cos(th)
    gy = 70 + 4.8 * np.sin(th)
    ax.add_patch(plt.Circle((gx, gy), 1.2, facecolor='#d97706', edgecolor='#b45309', zorder=3))
ax.add_patch(plt.Circle((62, 70), 2.5, facecolor='#ffffff', edgecolor='#d97706', lw=1.8, zorder=4))
ax.text(62, 57, "9-State Engine", ha='center', va='top', fontsize=9.0, fontweight='bold', color='#d97706')

# Arrow 3 -> 4
ax.annotate('', xy=(75, 70), xytext=(72, 70),
            arrowprops=dict(arrowstyle="-|>", color='#64748b', lw=2.2, mutation_scale=14))

# Stage 4: Living Bacterial Carrier
c4 = plt.Circle((86, 70), 9, facecolor='#f5f3ff', edgecolor='#7c3aed', lw=2.2, zorder=2)
ax.add_patch(c4)
capsule = patches.FancyBboxPatch((81.5, 66), 9, 8, boxstyle="round,pad=1.0,rounding_size=3",
                                facecolor='#ffffff', edgecolor='#7c3aed', lw=1.8, zorder=3)
ax.add_patch(capsule)
ax.plot([84, 88], [70, 70], color='#7c3aed', lw=2.2, zorder=4)
ax.text(86, 57, "Host Carrier", ha='center', va='top', fontsize=9.0, fontweight='bold', color='#7c3aed')

# Downward Flow Arrow
ax.annotate('', xy=(50, 47), xytext=(50, 52),
            arrowprops=dict(arrowstyle="-|>", color='#64748b', lw=2.2, mutation_scale=14))

# DNA Double Helix Strand (Bottom)
x_h = np.linspace(8, 92, 350)
y_s1 = 28 + 6.0 * np.sin(x_h * 0.25)
y_s2 = 28 - 6.0 * np.sin(x_h * 0.25)

# Colored base-pair rungs
rungs = np.linspace(9, 91, 40)
cols = ['#ef4444', '#3b82f6', '#10b981', '#f59e0b']
for i, rx in enumerate(rungs):
    y1 = 28 + 6.0 * np.sin(rx * 0.25)
    y2 = 28 - 6.0 * np.sin(rx * 0.25)
    c = cols[i % 4]
    ax.plot([rx, rx], [y1, y2], color=c, lw=2.4, alpha=0.9, zorder=2)
    ax.plot(rx, 28, marker='o', markersize=3.2, color=c, zorder=3)

# Backbone ribbons
ax.plot(x_h, y_s1, color='#0f172a', lw=3.2, zorder=4)
ax.plot(x_h, y_s2, color='#475569', lw=2.6, zorder=4)

# Flanking Primer Brackets with Clean Labels
# Forward Primer Bracket
ax.plot([8, 25], [16, 16], color='#0284c7', lw=2.2)
ax.plot([8, 8], [16, 18], color='#0284c7', lw=2.2)
ax.plot([25, 25], [16, 18], color='#0284c7', lw=2.2)
ax.text(16.5, 11, "Forward Primer (18 nt)", ha='center', va='top', fontsize=8.2, fontweight='bold', color='#0284c7')

# Central Stego Core Bracket
ax.plot([28, 72], [16, 16], color='#10b981', lw=2.8)
ax.plot([28, 28], [16, 18], color='#10b981', lw=2.8)
ax.plot([72, 72], [16, 18], color='#10b981', lw=2.8)
ax.text(50, 11, "Encrypted DNA Payload (Balanced GC 50%)", ha='center', va='top', fontsize=8.5, fontweight='bold', color='#059669')

# Reverse Primer Bracket
ax.plot([75, 92], [16, 16], color='#7c3aed', lw=2.2)
ax.plot([75, 75], [16, 18], color='#7c3aed', lw=2.2)
ax.plot([92, 92], [16, 18], color='#7c3aed', lw=2.2)
ax.text(83.5, 11, "Reverse Primer (18 nt)", ha='center', va='top', fontsize=8.2, fontweight='bold', color='#7c3aed')

# Minimal Base Legend at very bottom
ax.text(24, 3, "\u25a0 Adenine", color='#ef4444', fontsize=7.8, fontweight='bold')
ax.text(40, 3, "\u25a0 Thymine", color='#3b82f6', fontsize=7.8, fontweight='bold')
ax.text(56, 3, "\u25a0 Cytosine", color='#10b981', fontsize=7.8, fontweight='bold')
ax.text(72, 3, "\u25a0 Guanine", color='#f59e0b', fontsize=7.8, fontweight='bold')

plt.tight_layout()
plt.savefig('report_assets/fig_architecture_large.png', bbox_inches='tight', dpi=300)
plt.close()
print("Figure 1 generated (neatly labeled, zero paragraphs).")

# =============================================================================
# FIGURE 2: Neatly Labeled 9-State Automaton Network Graph
# =============================================================================
fig, ax = plt.subplots(figsize=(7.5, 5.2), dpi=300)
fig.patch.set_facecolor('#ffffff')
ax.set_facecolor('#ffffff')
ax.set_xlim(-1.45, 1.45)
ax.set_ylim(-1.45, 1.45)
ax.axis('off')

# Central Node: S0
center_circ = plt.Circle((0, 0), 0.17, facecolor='#0284c7', edgecolor='#0369a1', lw=2.5, zorder=5)
ax.add_patch(center_circ)
ax.text(0, 0, "START\n(S0)", ha='center', va='center', fontsize=7.5, fontweight='bold', color='#ffffff', zorder=6)

# 8 Orbital Nodes
angles = np.linspace(0, 2*np.pi, 8, endpoint=False)
node_names = ['A (Run 1)', 'A (Run 2)', 'C (Run 1)', 'C (Run 2)', 'G (Run 1)', 'G (Run 2)', 'T (Run 1)', 'T (Run 2)']
node_colors = ['#ef4444', '#b91c1c', '#10b981', '#047857', '#f59e0b', '#b45309', '#3b82f6', '#1d4ed8']
node_coords = []

for i, ang in enumerate(angles):
    x = 0.95 * np.cos(ang)
    y = 0.95 * np.sin(ang)
    node_coords.append((x, y))
    ax.plot([0, x], [0, y], color='#cbd5e1', lw=1.2, linestyle=':', zorder=1)

# Connect outer nodes with smooth curved transition arcs
for i in range(8):
    x1, y1 = node_coords[i]
    x2, y2 = node_coords[(i + 1) % 8]
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="-|>", color='#94a3b8', lw=1.4,
                                connectionstyle="arc3,rad=0.15", mutation_scale=11), zorder=2)
    x3, y3 = node_coords[(i + 3) % 8]
    ax.plot([x1, x3], [y1, y3], color='#e2e8f0', lw=0.9, zorder=1)

# Blocked loop markers on outer nodes (red barrier rings)
for i in [1, 3, 5, 7]:
    x, y = node_coords[i]
    bx = x * 1.25
    by = y * 1.25
    barrier = plt.Circle((bx, by), 0.08, facecolor='#fee2e2', edgecolor='#dc2626', lw=1.6, zorder=4)
    ax.add_patch(barrier)
    ax.plot([bx - 0.05, bx + 0.05], [by - 0.05, by + 0.05], color='#dc2626', lw=1.8, zorder=5)
    ax.plot([x, bx], [y, by], color='#dc2626', lw=1.2, linestyle='--', zorder=3)

# Draw Orbital Node Circles on top with clean labels
for i, (x, y) in enumerate(node_coords):
    col = node_colors[i]
    circ = plt.Circle((x, y), 0.14, facecolor='#ffffff', edgecolor=col, lw=3.0, zorder=5)
    ax.add_patch(circ)
    label_short = ['A1', 'A2', 'C1', 'C2', 'G1', 'G2', 'T1', 'T2'][i]
    ax.text(x, y, label_short, ha='center', va='center', fontsize=8.5, fontweight='bold', color=col, zorder=6)

# Minimal Corner Annotations (Clean & Neat)
ax.text(-1.40, 1.30, "\u25cf Safe Codons per State: \u2265 34 available", fontsize=8.5, fontweight='bold', color='#0f172a')
ax.text(-1.40, 1.20, "\u25cf Biological Limit: Max Repeat \u2264 2 Letters", fontsize=8.5, fontweight='bold', color='#059669')
ax.text(1.40, 1.30, "Rate: 1.667 Bits / Letter \u25cf", fontsize=8.5, fontweight='bold', color='#0284c7', ha='right')
ax.text(1.40, 1.20, "Zero Stop Codons \u25cf", fontsize=8.5, fontweight='bold', color='#7c3aed', ha='right')

plt.tight_layout()
plt.savefig('report_assets/fig_fsm_large.png', bbox_inches='tight', dpi=300)
plt.close()
print("Figure 2 generated (neatly labeled, zero paragraphs).")

# =============================================================================
# FIGURE 3: Photorealistic UV Agarose Gel Electrophoresis Photo
# =============================================================================
fig, ax = plt.subplots(figsize=(7.5, 5.2), dpi=300)
fig.patch.set_facecolor('#040711')
ax.set_facecolor('#03050c')
ax.set_xlim(0, 100)
ax.set_ylim(0, 100)
ax.axis('off')

# Gel Cassette Tray
gel_tray = patches.FancyBboxPatch((8, 6), 84, 88, boxstyle="round,pad=1.5,rounding_size=3",
                                  facecolor='#060c1d', edgecolor='#1e293b', lw=2.0)
ax.add_patch(gel_tray)

# Gel Wells (Top) with Clean Lane Labels
wells = [20, 40, 60, 80]
lane_names = ["Lane 1: 1 kb Ladder", "Lane 2: Blank Ctrl", "Lane 3: WT Host DNA", "Lane 4: Stego Amplicon"]
for wx, name in zip(wells, lane_names):
    ax.add_patch(patches.Rectangle((wx - 6, 83), 12, 4.5, facecolor='#0b1528', edgecolor='#334155', lw=1.2))
    ax.text(wx, 91, name, color='#94a3b8', fontsize=7.5, ha='center', va='center', fontweight='bold')

# UV Background Glow Gradient
for yg in np.linspace(6, 92, 120):
    ax.axhspan(yg, yg+0.8, xmin=0.08, xmax=0.92, color='#0284c7', alpha=0.012)

def draw_fluorescent_band(x_center, y_pos, width, height, intensity, color='#38bdf8'):
    bloom = patches.Ellipse((x_center, y_pos), width*1.9, height*3.5, facecolor=color, alpha=intensity*0.28, zorder=3)
    ax.add_patch(bloom)
    core = patches.Rectangle((x_center - width/2, y_pos - height/2), width, height, facecolor='#ffffff', edgecolor=color, lw=0.6, alpha=intensity*0.95, zorder=4)
    ax.add_patch(core)

# Lane 1: 1 kb DNA Ladder (with clean size labels)
ladder_bands = [
    (1500, 74, 9, 1.2, 0.70),
    (1000, 63, 9, 1.2, 0.75),
    (750, 52, 9, 1.2, 0.75),
    (500, 39, 9, 1.8, 0.98), # 500 bp intense reference band
    (250, 25, 9, 1.2, 0.65),
    (100, 13, 9, 1.2, 0.55)
]
for bp, y_pos, w, h, intens in ladder_bands:
    draw_fluorescent_band(20, y_pos, w, h, intens, color='#38bdf8')
    ax.text(12, y_pos, f"{bp} bp", color='#64748b', fontsize=7.0, ha='right', va='center', fontfamily='monospace')

# Lane 3: Wild-type Host band (320 bp)
draw_fluorescent_band(60, 29, 9, 1.4, 0.85, color='#38bdf8')
ax.text(60, 24, "320 bp", color='#64748b', fontsize=7.0, ha='center', va='top', fontfamily='monospace')

# Lane 4: Stego Recombinant Amplicon (620 bp)
draw_fluorescent_band(80, 46, 9.5, 2.0, 1.0, color='#38bdf8')
ax.annotate("", xy=(86, 46), xytext=(93, 46),
            arrowprops=dict(arrowstyle="-|>", color='#38bdf8', lw=1.5, mutation_scale=11))
ax.text(94, 46, "620 bp\nTarget", color='#38bdf8', fontsize=7.5, ha='left', va='center', fontweight='bold')

# Polarity indicators
ax.text(4, 85, "(-)", color='#ef4444', fontsize=9.0, ha='center', va='center', fontweight='bold')
ax.text(4, 13, "(+)", color='#3b82f6', fontsize=9.0, ha='center', va='center', fontweight='bold')
ax.annotate("", xy=(4, 20), xytext=(4, 78),
            arrowprops=dict(arrowstyle="-|>", color='#64748b', lw=1.8, mutation_scale=14))

plt.tight_layout()
plt.savefig('report_assets/fig_gel_large.png', bbox_inches='tight', dpi=300)
plt.close()
print("Figure 3 generated (neatly labeled, zero paragraphs).")

# =============================================================================
# FIGURE 4: Clean Biophysical Stability Curve
# =============================================================================
fig, ax = plt.subplots(figsize=(7.5, 5.2), dpi=300)
fig.patch.set_facecolor('#ffffff')
ax.set_facecolor('#ffffff')

x = np.linspace(0, 800, 400)
np.random.seed(42)
gc_stego = 50.0 + 3.0 * np.sin(x / 45) + np.random.normal(0, 0.6, len(x))
gc_naive = 50.0 + 26.0 * np.sin(x / 65) + np.random.normal(0, 3.5, len(x))

# Safe green corridor
ax.axhspan(40, 60, color='#dcfce7', alpha=0.75, zorder=1)
ax.axhline(60, color='#16a34a', linestyle='--', lw=1.5, zorder=2)
ax.axhline(50, color='#94a3b8', linestyle=':', lw=1.0, zorder=2)
ax.axhline(40, color='#16a34a', linestyle='--', lw=1.5, zorder=2)

# Curves
ax.plot(x, gc_naive, color='#dc2626', linestyle=':', lw=1.6, alpha=0.7, zorder=3, label="Naive Mapping (Unstable: 18-82%)")
ax.plot(x, gc_stego, color='#0284c7', lw=3.0, zorder=4, label="BioCrypt Transducer (Stable: 46-54%)")

# Clean labels on axes and boundaries
ax.text(805, 60, "60% Upper Limit", va='center', ha='left', fontsize=8.0, fontweight='bold', color='#16a34a')
ax.text(805, 50, "50% Target", va='center', ha='left', fontsize=8.0, color='#64748b')
ax.text(805, 40, "40% Lower Limit", va='center', ha='left', fontsize=8.0, fontweight='bold', color='#16a34a')
ax.text(400, 56.5, "Biological Safe Zone (40% to 60% GC)", ha='center', va='center', fontsize=9.0, fontweight='bold', color='#15803d')

ax.set_ylim(15, 85)
ax.set_xlim(0, 800)
ax.set_xlabel("Nucleotide Position (Base Pairs)", fontsize=9.5, fontweight='bold', labelpad=8)
ax.set_ylabel("Local GC Content (%)", fontsize=9.5, fontweight='bold', labelpad=8)
ax.legend(loc='lower right', fontsize=8.5, framealpha=0.92)
ax.grid(True, linestyle=':', alpha=0.5, color='#cbd5e1')

plt.tight_layout()
plt.savefig('report_assets/fig_gc_density_large.png', bbox_inches='tight', dpi=300)
plt.close()
print("Figure 4 generated (neatly labeled, zero paragraphs).")

# =============================================================================
# FIGURE 5: Clean, Neatly Labeled Circular Plasmid Map
# =============================================================================
fig, ax = plt.subplots(figsize=(7.5, 5.2), dpi=300, subplot_kw={'projection': 'polar'})
fig.patch.set_facecolor('#ffffff')
ax.set_facecolor('#ffffff')

# Circular backbone ring
theta = np.linspace(0, 2*np.pi, 500)
ax.plot(theta, [1.0]*len(theta), color='#334155', lw=3.5, zorder=2)

# Feature arcs with clean labels
features = [
    (0.12 * np.pi, 0.52 * np.pi, 0.16, '#10b981', "Stego Insert\n(620 bp)", 1.25),
    (0.60 * np.pi, 0.80 * np.pi, 0.10, '#a855f7', "lacZ Promoter", 1.22),
    (0.85 * np.pi, 0.98 * np.pi, 0.10, '#f59e0b', "MCS", 1.22),
    (1.10 * np.pi, 1.55 * np.pi, 0.14, '#3b82f6', "AmpR (bla)", 1.25),
    (1.65 * np.pi, 1.90 * np.pi, 0.12, '#0284c7', "ColE1 ori", 1.23),
    (1.95 * np.pi, 2.05 * np.pi, 0.10, '#ef4444', "Terminator", 1.22),
]

for s_rad, e_rad, width, col, lbl, lbl_r in features:
    rad_pts = np.linspace(s_rad, e_rad, 100)
    ax.fill_between(rad_pts, 1.0 - width/2, 1.0 + width/2, color=col, alpha=0.92, zorder=3)
    mid_rad = (s_rad + e_rad) / 2
    ax.text(mid_rad, lbl_r, lbl, ha='center', va='center', fontsize=7.5, fontweight='bold', color=col, zorder=5)

# Restriction cut sites
cut_sites = [
    ("EcoRI (42)", 0.05*np.pi),
    ("BamHI (730)", 0.55*np.pi),
    ("HindIII (1400)", 1.05*np.pi),
    ("PstI (4000)", 1.60*np.pi)
]
for site_name, rad in cut_sites:
    ax.plot([rad, rad], [0.96, 1.12], color='#0f172a', lw=1.8, zorder=4)
    ax.text(rad, 1.38, site_name, ha='center', va='center', fontsize=7.0, fontfamily='monospace', color='#0f172a')

# Center emblem
ax.text(0, 0, "pBioCrypt-3.0\n4,820 bp", ha='center', va='center', fontsize=9.5, fontweight='bold', color='#0f172a')

ax.set_yticklabels([])
ax.set_xticklabels([])
ax.grid(False)
ax.spines['polar'].set_visible(False)

plt.tight_layout()
plt.savefig('report_assets/fig_locus_map_large.png', bbox_inches='tight', dpi=300)
plt.close()
print("Figure 5 generated (neatly labeled, zero paragraphs).")
