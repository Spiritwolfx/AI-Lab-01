"""
LUXURY FRACTAL — Iridescent Lotus / Liquid Chrome Mandala
============================================================
An avant-garde, print-ready fractal design for high-fashion apparel.

Aesthetic: obsidian ink-black ground, mother-of-pearl iridescence,
liquid chrome, rose gold, twilight violet. Built from three
superposed vector fields — recursive floral (lotus/mandala) geometry,
liquid interference waves, and fractal "cosmic smoke" noise — then
finished with soft bloom, feathered gradients and a vignette so it
reads as fluid and organic rather than a math-plot screensaver.

Output: luxury_fractal_shirt.png  — 3600x3600px @ 300 DPI (12"x12")
"""

import numpy as np
from scipy.ndimage import gaussian_filter
from matplotlib.colors import LinearSegmentedColormap
import matplotlib.pyplot as plt

# ------------------------------------------------------------------
# 0. CONFIG — the knobs you'll actually want to tweak live here
# ------------------------------------------------------------------
RESOLUTION   = 3600          # final pixel width/height (square, print-ready)
DPI          = 300
SEED         = 7             # change for a different "cosmic smoke" pull

PETALS       = 12            # symmetry order of the lotus/mandala
RECURSION    = 5             # how many nested/scaled petal layers stack
WAVE_FREQ    = 26.0          # radial frequency of the liquid interference field
WAVE_FREQ2   = 17.0          # secondary interference frequency (creates moiré)
SWIRL        = 3.4           # how much the smoke layer twists around center

GLOW_STRENGTH = 0.55         # bloom intensity on bright ridges
VIGNETTE_DEPTH = 0.85        # how strongly edges fall to obsidian black

rng = np.random.default_rng(SEED)

# ------------------------------------------------------------------
# 1. COORDINATE FIELD
# ------------------------------------------------------------------
N = RESOLUTION
lin = np.linspace(-1.0, 1.0, N, dtype=np.float32)
x, y = np.meshgrid(lin, lin)
r = np.sqrt(x**2 + y**2)
theta = np.arctan2(y, x)

# ------------------------------------------------------------------
# 2. RECURSIVE FLORAL / SACRED-GEOMETRY LOTUS LAYER
#    Nested, scaled, counter-rotating petal harmonics summed together
#    so each recursion "blooms" inside the last — a hyper-dimensional
#    lotus rather than a single flat rosette.
# ------------------------------------------------------------------
lotus = np.zeros_like(r)
for k in range(1, RECURSION + 1):
    scale   = 0.72 + 0.30 * k                    # each layer breathes outward, further out
    rot     = (k * np.pi / PETALS) * (1 if k % 2 == 0 else -1)
    petals_k = PETALS + (k - 1) * (2 if k % 2 else 0)  # occasionally deepens symmetry
    radial_bloom = np.exp(-((r * scale - 0.62) ** 2) * (3.2 + 0.6 * k))
    lotus += (1.0 / k) * np.cos(petals_k * (theta + rot)) * radial_bloom

lotus += 0.35 * np.exp(-((r - 0.06) ** 2) * 40)   # soft luminous pistil at the core
lotus = lotus / np.max(np.abs(lotus))

# ------------------------------------------------------------------
# 3. LIQUID INTERFERENCE FIELD
#    Two radial/angular wave systems crossed to create an oil-on-water,
#    moiré-like ripple — the "liquid chrome" shimmer.
# ------------------------------------------------------------------
wave1 = np.sin(WAVE_FREQ * r - 5 * theta + 1.3 * np.sin(3 * theta))
wave2 = np.sin(WAVE_FREQ2 * r + 8 * theta - 0.7)
interference = 0.5 * wave1 + 0.5 * wave2
interference *= np.exp(-1.4 * r**2)               # keep it luminous near center
interference = interference / np.max(np.abs(interference))

# ------------------------------------------------------------------
# 4. FRACTAL "COSMIC SMOKE" — multi-octave value noise
#    (band-limited noise summed across octaves = cheap, dependency-free
#    Perlin-like fractal noise, vectorized and smoothed with scipy).
# ------------------------------------------------------------------
def fractal_noise(shape, octaves=5, base_sigma=90, persistence=0.55, seed_rng=rng):
    field = np.zeros(shape, dtype=np.float32)
    amp = 1.0
    total_amp = 0.0
    for o in range(octaves):
        sigma = max(base_sigma / (2 ** o), 1.0)
        raw = seed_rng.standard_normal(shape).astype(np.float32)
        smoothed = gaussian_filter(raw, sigma=sigma)
        field += amp * smoothed
        total_amp += amp
        amp *= persistence
    field /= total_amp
    field -= field.mean()
    field /= (np.std(field) + 1e-8)
    return field

smoke = fractal_noise((N, N), octaves=6, base_sigma=140, persistence=0.58)

# swirl the smoke around the mandala center for a cosmic, wind-blown feel
swirl_theta = theta + SWIRL * np.exp(-2.2 * r) * np.sin(4 * np.pi * r)
sx = (r * np.cos(swirl_theta) + 1) * 0.5 * (N - 1)
sy = (r * np.sin(swirl_theta) + 1) * 0.5 * (N - 1)
sx = np.clip(sx, 0, N - 1).astype(np.int32)
sy = np.clip(sy, 0, N - 1).astype(np.int32)
smoke = smoke[sy, sx]
smoke = gaussian_filter(smoke, sigma=2.0)
smoke = smoke / np.max(np.abs(smoke))

# ------------------------------------------------------------------
# 5. COMPOSE THE MASTER LUMINANCE FIELD
#    Weighted blend => organic depth instead of a flat single fractal.
# ------------------------------------------------------------------
field = (0.48 * lotus) + (0.34 * interference) + (0.30 * smoke * (0.4 + 0.6 * (1 - r)))
field = gaussian_filter(field, sigma=1.1)          # feather hard edges -> fluid lines
field = (field - field.min()) / (field.max() - field.min())   # normalize -> [0,1]

# contrast / gamma shaping: keeps the ground truly obsidian-black and
# lets only the ridge-lines of the design carry the luminous color,
# instead of a flat pastel wash across the whole canvas.
CONTRAST_GAMMA = 2.0
field = field ** CONTRAST_GAMMA
field = (field - field.min()) / (field.max() - field.min())

# ------------------------------------------------------------------
# 6. IRIDESCENT IMAGE ASSEMBLY
#    Three phase-shifted "views" of the same field become R/G/B channel
#    biases -> a genuine mother-of-pearl / oil-slick iridescence instead
#    of a single flat gradient lookup.
# ------------------------------------------------------------------
luxury_colors = [
    (0.00, "#050308"),   # obsidian / ink black
    (0.30, "#0C0814"),   # near-black, cool undertone
    (0.46, "#2C1E44"),   # deep twilight violet
    (0.60, "#5C4E7A"),   # dusk violet-lilac transition
    (0.72, "#9C9DB8"),   # liquid chrome silver
    (0.83, "#D8B8B0"),   # soft rose gold
    (0.93, "#EFD9CE"),   # champagne / mother-of-pearl
    (1.00, "#FCF6EF"),   # pearl highlight
]
cmap = LinearSegmentedColormap.from_list("luxury_lotus", luxury_colors, N=1024)

# phase-shifted samples create the iridescent channel drift — pushed
# wider than a subtle nudge so the mother-of-pearl / oil-slick color
# separation actually reads (rose gold vs. chrome vs. violet edges).
IRIDESCENCE = 0.07
phase_r = np.clip(field + IRIDESCENCE * interference, 0, 1)
phase_g = np.clip(field, 0, 1)
phase_b = np.clip(field - IRIDESCENCE * lotus, 0, 1)

img = np.empty((N, N, 3), dtype=np.float32)
img[..., 0] = np.array(cmap(phase_r))[..., 0]
img[..., 1] = np.array(cmap(phase_g))[..., 1]
img[..., 2] = np.array(cmap(phase_b))[..., 2]

# ------------------------------------------------------------------
# 7. LUMINOUS BLOOM / GLOW
#    Screen-blend a blurred copy of the bright ridges back onto the
#    image for that soft, expensive glow rather than flat vector lines.
# ------------------------------------------------------------------
brightness = img.mean(axis=2)
highlight_mask = np.clip((brightness - 0.68) / 0.32, 0, 1) ** 1.8
bloom = np.stack([gaussian_filter(highlight_mask, sigma=s) for s in (3, 10, 28)], axis=-1).mean(axis=-1)
bloom = bloom[..., None]

img = 1 - (1 - img) * (1 - GLOW_STRENGTH * bloom)   # screen blend
img = np.clip(img, 0, 1)

# faint cosmic-smoke wisps threaded through the black ground — keeps
# the "swirling smoke" promise alive even where the gamma curve has
# otherwise crushed the field to obsidian.
smoke_pos = (smoke - smoke.min()) / (smoke.max() - smoke.min())
smoke_wisp = gaussian_filter(smoke_pos, sigma=2.5) ** 3
wisp_tint = np.array([0.55, 0.48, 0.62], dtype=np.float32)   # cool violet-grey smoke tone
img += (0.10 * smoke_wisp)[..., None] * wisp_tint[None, None, :] * (1 - field[..., None])
img = np.clip(img, 0, 1)

# ------------------------------------------------------------------
# 8. VIGNETTE — feather the composition back into obsidian at the
#    edges so it sits like a medallion rather than a hard-cropped tile.
# ------------------------------------------------------------------
vignette = 1 - VIGNETTE_DEPTH * np.clip((r - 0.42) / 0.62, 0, 1) ** 1.4
img *= vignette[..., None]
img = np.clip(img, 0, 1)

# ------------------------------------------------------------------
# 9. SAVE — print-ready PNG, exact pixel resolution at 300 DPI
# ------------------------------------------------------------------
fig = plt.figure(figsize=(RESOLUTION / DPI, RESOLUTION / DPI), dpi=DPI)
ax = fig.add_axes([0, 0, 1, 1])
ax.imshow(img, interpolation="bicubic")
ax.axis("off")
fig.patch.set_facecolor("#05040A")

out_path = "luxury_fractal_shirt.png"
fig.savefig(out_path, dpi=DPI, facecolor="#05040A")
plt.close(fig)

print(f"Saved {out_path} at {RESOLUTION}x{RESOLUTION}px, {DPI} DPI")
