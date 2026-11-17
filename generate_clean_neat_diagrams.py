import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

os.makedirs('report_assets', exist_ok=True)

# Use clean modern sans-serif
plt.rcParams['font.sans-serif'] = 'Helvetica'
plt.rcParams['font.family'] = 'sans-serif'

# =============================================================================
# FIGURE 1: Clean, Minimalist Molecular Pipeline Architecture
# =============================================================================
fig, ax = plt.subplots(figsize=(7.5, 5.2), dpi=300)
fig.patch.set_facecolor('#ffffff')
ax.set_facecolor('#ffffff')
ax.set_xlim(0, 100)
ax.set_ylim(0, 100)
ax.axis('off')

# Stage 1: Document / File (Left)
c1 = plt.Circle((14, 68), 9, facecolor='#f0f9ff', edgecolor='#0284c7', lw=2.5, zorder=2)
ax.add_patch(c1)
# Document icon inside
doc = patches.Rectangle((10.5, 62.5), 7, 11, facecolor='#ffffff', edgecolor='#0284c7', lw=1.8, zorder=3)
ax.add_patch(doc)
# Lines on doc
for dy in [2.5, 5.0, 7.5]:
    ax.plot([12, 16], [62.5 + dy, 62.5 + dy], color='#0284c7', lw=1.2, zorder=4)

# Arrow 1 -> 2
ax.annotate('', xy=(27, 68), xytext=(24, 68),
            arrowprops=dict(arrowstyle="-|>", color='#64748b', lw=2.5, mutation_scale=15))

# Stage 2: Security Shield / Padlock
c2 = plt.Circle((38, 68), 9, facecolor='#ecfdf5', edgecolor='#059669', lw=2.5, zorder=2)
ax.add_patch(c2)
# Padlock icon
lock_body = patches.Rectangle((34.5, 63), 7, 6, facecolor='#059669', edgecolor='#047857', lw=1.5, zorder=3)
ax.add_patch(lock_body)
shackle = patches.Arc((38, 69), 4.5, 6, theta1=0, theta2=180, edgecolor='#047857', lw=2.0, zorder=3)
ax.add_patch(shackle)
# Keyhole
ax.plot([38, 38], [65, 66.5], color='#ffffff', lw=1.8, zorder=4)
ax.plot(38, 67, marker='o', color='#ffffff', markersize=3, zorder=4)

# Arrow 2 -> 3
ax.annotate('', xy=(51, 68), xytext=(48, 68),
            arrowprops=dict(arrowstyle="-|>", color='#64748b', lw=2.5, mutation_scale=15))

# Stage 3: Rotary Automaton / Translation Gear
c3 = plt.Circle((62, 68), 9, facecolor='#fffbeb', edgecolor='#d97706', lw=2.5, zorder=2)
ax.add_patch(c3)
# Clean rotary wheel with 6 satellite dots
theta_gear = np.linspace(0, 2*np.pi, 6, endpoint=False)
for th in theta_gear:
    gx = 62 + 4.8 * np.cos(th)
    gy = 68 + 4.8 * np.sin(th)
    ax.add_patch(plt.Circle((gx, gy), 1.2, facecolor='#d97706', edgecolor='#b45309', zorder=3))
ax.add_patch(plt.Circle((62, 68), 2.5, facecolor='#ffffff', edgecolor='#d97706', lw=1.8, zorder=4))

# Arrow 3 -> 4
ax.annotate('', xy=(75, 68), xytext=(72, 68),
            arrowprops=dict(arrowstyle="-|>", color='#64748b', lw=2.5, mutation_scale=15))

# Stage 4: Cell / Carrier Host
c4 = plt.Circle((86, 68), 9, facecolor='#f5f3ff', edgecolor='#7c3aed', lw=2.5, zorder=2)
ax.add_patch(c4)
# Cell capsule / plasmid inside
capsule = patches.FancyBboxPatch((81.5, 64), 9, 8, boxstyle="round,pad=1.0,rounding_size=3",
                                facecolor='#ffffff', edgecolor='#7c3aed', lw=1.8, zorder=3)
ax.add_patch(capsule)
ax.plot([84, 88], [68, 68], color='#7c3aed', lw=2.2, zorder=4)

# Downward Flow Arrow to Helix
ax.annotate('', xy=(50, 48), xytext=(50, 55),
            arrowprops=dict(arrowstyle="-|>", color='#64748b', lw=2.5, mutation_scale=15))

# DNA Double Helix Strand (Bottom)
x_h = np.linspace(8, 92, 350)
y_s1 = 26 + 6.0 * np.sin(x_h * 0.25)
y_s2 = 26 - 6.0 * np.sin(x_h * 0.25)

# Colored base-pair rungs
rungs = np.linspace(9, 91, 40)
cols = ['#ef4444', '#3b82f6', '#10b981', '#f59e0b']
for i, rx in enumerate(rungs):
    y1 = 26 + 6.0 * np.sin(rx * 0.25)
    y2 = 26 - 6.0 * np.sin(rx * 0.25)
    c = cols[i % 4]
    ax.plot([rx, rx], [y1, y2], color=c, lw=2.4, alpha=0.9, zorder=2)
    ax.plot(rx, 26, marker='o', markersize=3.2, color=c, zorder=3)

# Helical backbone ribbons
ax.plot(x_h, y_s1, color='#0f172a', lw=3.2, zorder=4)
ax.plot(x_h, y_s2, color='#475569', lw=2.6, zorder=4)

# Flanking Primer Brackets (Clean geometry)
# Forward Primer Bracket (Left)
ax.plot([8, 25], [14, 14], color='#0284c7', lw=2.5)
ax.plot([8, 8], [14, 16], color='#0284c7', lw=2.5)
ax.plot([25, 25], [14, 16], color='#0284c7', lw=2.5)
ax.plot(16.5, 14, marker='v', color='#0284c7', markersize=6)

# Central Stego Core Bracket
ax.plot([28, 72], [14, 14], color='#10b981', lw=3.0)
ax.plot([28, 28], [14, 16], color='#10b981', lw=3.0)
ax.plot([72, 72], [14, 16], color='#10b981', lw=3.0)
ax.plot(50, 14, marker='s', color='#10b981', markersize=6)

# Reverse Primer Bracket (Right)
ax.plot([75, 92], [14, 14], color='#7c3aed', lw=2.5)
ax.plot([75, 75], [14, 16], color='#7c3aed', lw=2.5)
ax.plot([92, 92], [14, 16], color='#7c3aed', lw=2.5)
ax.plot(83.5, 14, marker='^', color='#7c3aed', markersize=6)

plt.tight_layout()
plt.savefig('report_assets/fig_architecture_large.png', bbox_inches='tight', dpi=300)
plt.close()
print("Figure 1 generated (clean, neat, zero text).")

# =============================================================================
# FIGURE 2: Clean, Symmetrical 9-State Automaton Network Graph
# =============================================================================
fig, ax = plt.subplots(figsize=(7.5, 5.2), dpi=300)
fig.patch.set_facecolor('#ffffff')
ax.set_facecolor('#ffffff')
ax.set_xlim(-1.4, 1.4)
ax.set_ylim(-1.4, 1.4)
ax.axis('off')

# Central Node: S0
center_circ = plt.Circle((0, 0), 0.16, facecolor='#0284c7', edgecolor='#0369a1', lw=2.5, zorder=5)
ax.add_patch(center_circ)
ax.plot(0, 0, marker='*', color='#ffffff', markersize=10, zorder=6)

# 8 Orbital Nodes
angles = np.linspace(0, 2*np.pi, 8, endpoint=False)
node_colors = ['#ef4444', '#b91c1c', '#10b981', '#047857', '#f59e0b', '#b45309', '#3b82f6', '#1d4ed8']
node_coords = []

for i, ang in enumerate(angles):
    x = 0.95 * np.cos(ang)
    y = 0.95 * np.sin(ang)
    node_coords.append((x, y))
    # Radial line from center
    ax.plot([0, x], [0, y], color='#cbd5e1', lw=1.2, linestyle=':', zorder=1)

# Connect outer nodes with smooth curved transition arcs
for i in range(8):
    x1, y1 = node_coords[i]
    x2, y2 = node_coords[(i + 1) % 8]
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="-|>", color='#94a3b8', lw=1.4,
                                connectionstyle="arc3,rad=0.15", mutation_scale=11), zorder=2)
    # Cross connections across ring
    x3, y3 = node_coords[(i + 3) % 8]
    ax.plot([x1, x3], [y1, y3], color='#e2e8f0', lw=0.9, zorder=1)

# Blocked loop markers on outer nodes (red barrier rings)
for i in [1, 3, 5, 7]:
    x, y = node_coords[i]
    bx = x * 1.25
    by = y * 1.25
    # Red slash circle
    barrier = plt.Circle((bx, by), 0.08, facecolor='#fee2e2', edgecolor='#dc2626', lw=1.6, zorder=4)
    ax.add_patch(barrier)
    ax.plot([bx - 0.05, bx + 0.05], [by - 0.05, by + 0.05], color='#dc2626', lw=1.8, zorder=5)
    # Connecting dashed line
    ax.plot([x, bx], [y, by], color='#dc2626', lw=1.2, linestyle='--', zorder=3)

# Draw Orbital Node Circles on top
for i, (x, y) in enumerate(node_coords):
    col = node_colors[i]
    circ = plt.Circle((x, y), 0.13, facecolor='#ffffff', edgecolor=col, lw=3.0, zorder=5)
    ax.add_patch(circ)
    # Inner colored core
    ax.add_patch(plt.Circle((x, y), 0.06, facecolor=col, zorder=6))

plt.tight_layout()
plt.savefig('report_assets/fig_fsm_large.png', bbox_inches='tight', dpi=300)
plt.close()
print("Figure 2 generated (clean, neat, zero text).")

# =============================================================================
# FIGURE 3: Photorealistic UV Agarose Gel Electrophoresis Photo
# =============================================================================
fig, ax = plt.subplots(figsize=(7.5, 5.2), dpi=300)
fig.patch.set_facecolor('#040711')
ax.set_facecolor('#03050c')
ax.set_xlim(0, 100)
ax.set_ylim(0, 100)
ax.axis('off')

# Gel Cassette Tray with UV transillumination glow
gel_tray = patches.FancyBboxPatch((8, 6), 84, 88, boxstyle="round,pad=1.5,rounding_size=3",
                                  facecolor='#060c1d', edgecolor='#1e293b', lw=2.0)
ax.add_patch(gel_tray)

# Gel Wells (Top)
wells = [20, 40, 60, 80]
for wx in wells:
    ax.add_patch(patches.Rectangle((wx - 5.5, 84), 11, 4.5, facecolor='#0b1528', edgecolor='#334155', lw=1.2))

# Realistic UV background gradient
for yg in np.linspace(6, 92, 120):
    ax.axhspan(yg, yg+0.8, xmin=0.08, xmax=0.92, color='#0284c7', alpha=0.012)

# Helper function to draw realistic fluorescent bands with Gaussian bloom
def draw_fluorescent_band(x_center, y_pos, width, height, intensity, color='#38bdf8'):
    bloom = patches.Ellipse((x_center, y_pos), width*1.9, height*3.5, facecolor=color, alpha=intensity*0.28, zorder=3)
    ax.add_patch(bloom)
    core = patches.Rectangle((x_center - width/2, y_pos - height/2), width, height, facecolor='#ffffff', edgecolor=color, lw=0.6, alpha=intensity*0.95, zorder=4)
    ax.add_patch(core)

# Lane 1: 1 kb DNA Ladder (6 bands)
ladder_bands = [
    (74, 9, 1.2, 0.70),
    (63, 9, 1.2, 0.75),
    (52, 9, 1.2, 0.75),
    (39, 9, 1.8, 0.98), # 500 bp intense reference band
    (25, 9, 1.2, 0.65),
    (13, 9, 1.2, 0.55)
]
for y_pos, w, h, intens in ladder_bands:
    draw_fluorescent_band(20, y_pos, w, h, intens, color='#38bdf8')

# Lane 2: Blank (no bands)

# Lane 3: Wild-type Host band (320 bp -> y = 29)
draw_fluorescent_band(60, 29, 9, 1.4, 0.85, color='#38bdf8')

# Lane 4: Stego Recombinant Amplicon (620 bp -> y = 46)
draw_fluorescent_band(80, 46, 9.5, 2.0, 1.0, color='#38bdf8')

# Minimalist cathode (-) and anode (+) markers
ax.plot(4, 86, marker='_', color='#ef4444', markersize=10, markeredgewidth=2.5)
ax.plot(4, 14, marker='+', color='#3b82f6', markersize=10, markeredgewidth=2.5)
ax.annotate("", xy=(4, 22), xytext=(4, 78),
            arrowprops=dict(arrowstyle="-|>", color='#64748b', lw=1.8, mutation_scale=14))

plt.tight_layout()
plt.savefig('report_assets/fig_gel_large.png', bbox_inches='tight', dpi=300)
plt.close()
print("Figure 3 generated (clean, neat, zero text).")

# =============================================================================
# FIGURE 4: Clean Biophysical Stability Curve
# =============================================================================
fig, ax = plt.subplots(figsize=(7.5, 5.2), dpi=300)
fig.patch.set_facecolor('#ffffff')
ax.set_facecolor('#ffffff')

x = np.linspace(0, 800, 400)
np.random.seed(42)
# Stable BioCrypt curve
gc_stego = 50.0 + 3.0 * np.sin(x / 45) + np.random.normal(0, 0.6, len(x))
# Unstable naive curve
gc_naive = 50.0 + 26.0 * np.sin(x / 65) + np.random.normal(0, 3.5, len(x))

# Safe green corridor
ax.axhspan(40, 60, color='#dcfce7', alpha=0.75, zorder=1)
ax.axhline(60, color='#16a34a', linestyle='--', lw=1.5, zorder=2)
ax.axhline(50, color='#94a3b8', linestyle=':', lw=1.0, zorder=2)
ax.axhline(40, color='#16a34a', linestyle='--', lw=1.5, zorder=2)

# Curves
ax.plot(x, gc_naive, color='#dc2626', linestyle=':', lw=1.6, alpha=0.7, zorder=3)
ax.plot(x, gc_stego, color='#0284c7', lw=3.0, zorder=4)

ax.set_ylim(15, 85)
ax.set_xlim(0, 800)
ax.grid(True, linestyle=':', alpha=0.4, color='#cbd5e1')
# Clean minimal border
for spine in ax.spines.values():
    spine.set_color('#94a3b8')
    spine.set_linewidth(1.0)
ax.set_xticks([])
ax.set_yticks([])

plt.tight_layout()
plt.savefig('report_assets/fig_gc_density_large.png', bbox_inches='tight', dpi=300)
plt.close()
print("Figure 4 generated (clean, neat, zero text).")

# =============================================================================
# FIGURE 5: Clean, Minimalist Circular Plasmid Map
# =============================================================================
fig, ax = plt.subplots(figsize=(7.5, 5.2), dpi=300, subplot_kw={'projection': 'polar'})
fig.patch.set_facecolor('#ffffff')
ax.set_facecolor('#ffffff')

# Circular backbone ring
theta = np.linspace(0, 2*np.pi, 500)
ax.plot(theta, [1.0]*len(theta), color='#334155', lw=3.5, zorder=2)

# Feature arcs (pure geometric arcs, beautiful colors, zero text)
features = [
    (0.12 * np.pi, 0.52 * np.pi, 0.16, '#10b981'),  # Stego insert (emerald green)
    (0.60 * np.pi, 0.80 * np.pi, 0.10, '#a855f7'),  # Promoter (purple)
    (0.85 * np.pi, 0.98 * np.pi, 0.10, '#f59e0b'),  # MCS (amber)
    (1.10 * np.pi, 1.55 * np.pi, 0.14, '#3b82f6'),  # AmpR selection marker (blue)
    (1.65 * np.pi, 1.90 * np.pi, 0.12, '#0284c7'),  # Origin of rep (cyan)
    (1.95 * np.pi, 2.05 * np.pi, 0.10, '#ef4444'),  # Terminator (red)
]

for s_rad, e_rad, width, col in features:
    rad_pts = np.linspace(s_rad, e_rad, 100)
    ax.fill_between(rad_pts, 1.0 - width/2, 1.0 + width/2, color=col, alpha=0.92, zorder=3)

# Radial cut-site ticks
for tick_rad in [0.05*np.pi, 0.55*np.pi, 1.05*np.pi, 1.60*np.pi]:
    ax.plot([tick_rad, tick_rad], [0.96, 1.12], color='#0f172a', lw=1.8, zorder=4)
    ax.plot(tick_rad, 1.15, marker='o', color='#0f172a', markersize=3.5, zorder=5)

# Center minimalist emblem
ax.add_patch(plt.Circle((0, 0), 0.28, facecolor='#f8fafc', edgecolor='#cbd5e1', lw=1.5, zorder=3, transform=ax.transData._b))
ax.plot(0, 0, marker='o', color='#0284c7', markersize=8, zorder=4)

ax.set_yticklabels([])
ax.set_xticklabels([])
ax.grid(False)
ax.spines['polar'].set_visible(False)

plt.tight_layout()
plt.savefig('report_assets/fig_locus_map_large.png', bbox_inches='tight', dpi=300)
plt.close()
print("Figure 5 generated (clean, neat, zero text).")
