# 03: Engine and scenes

## Why pycairo + numpy

Manim and Blender are options. A plain pycairo renderer gives a few things they don't:

- exact control of type and lines;
- a deterministic `draw(t)`;
- trivial parallel chunked rendering;
- the same drawing code for stills, video, audits and SVG/PDF figures.

The case study used only pycairo, numpy and ffmpeg.

## `scripts/engine.py` (copy into `src/`)

- **`Canvas(W, H)`**: `begin()` scales the 1920×1080 design space to W×H and paints the background. Primitives: `line`, `poly`, `circle`, `rrect`, `bezier`, `arrowhead`, `shadow`, `glow_dot`, and `text(x, y, s, font, size, col, a, anchor, track, reveal)`.
  - `text` supports `^{sup}` runs and per-character reveal.
  - `measure` uses the same run logic.
- **Easing and keyframes**: `seg`, `smooth`, `io3`, `ocub`, `oexpo`, `window(t, a, b, fin, fout)`, `lerp`, `lerp2`, `mix`.
- **`Cam3`**: a 3-D projection for small objects such as a cube.
- **`Post`**: the post-processing hook. In the white identity it is the identity function.

Film-specific code lives in `film.py`.

## `scripts/motion_kit.py` (copy into `src/` with engine.py and scene_kit.py)

This is the craft layer distilled from the case study:
- camera direction: `beat_keys`, `lagged`, `stage_cam`, `View2`;
- focus and motion primitives: `focus`, `tracer`, `proposal`, `pulse`;
- linkage: `callout_at`, `tether`, `AddressTable`, `pill` / `slot_node` / `stable_loop`, `breadcrumb`.

`examples/motion_kit_demo/film.py` uses every one of them in a 12 s beat and passes G1–G4 and L1. Start the centrepiece act from it. Call `begin_frame()` at the top of `draw()` and flush `OVERLAY` at the end.

## Patterns that worked

- **Pure frames.** `draw(cv, t)` clears overlays, calls `cv.begin()`, runs every scene gated by its time window, then flushes the overlays. With no hidden state, any frame can be rendered alone.
- **Deferred overlays**:
  ```python
  OVERLAY = []
  def overlay(fn):
      def wrap(*a, **k): OVERLAY.append(lambda: fn(*a, **k))
      return wrap
  ```
  Act labels, captions, tags, breadcrumbs, the table panel and HUDs are overlays. This lets figure mode remove or transform them (references/09-slide-figures.md).
- **Keyframed cameras**: `kfv(t, KEYS, logi=(index_of_distance,))`, with per-key easing names. Interpolate the distance logarithmically for natural zooms.
- **Stage camera for a "3-D graph over a graph"** (case study: candidate states hovering over a reference graph). Use a look-at `StageCam(tx, ty, th, D, tau, psi, ox, oy, f)`:
  - `tau` is the tilt, `psi` the azimuth;
  - `ox`/`oy` shift the stage in screen space (e.g. to make room for a panel).
  
  Project world points with `cam.P((x, y, h)) → (sx, sy, scale, depth)`, and scale text and stroke widths sub-linearly with `scale`.
- **Billboard text and chips**: `bb_text(cv, cam, world_pt, dx, dy, s, ...)` and `chip(...)`. The offsets scale with depth.
- **Data-driven everything.** Graph nodes, edges, the walk, candidates, the tree and replays come from `scene_data.json`. Add `assert`s for invariants, e.g. "each replay step is an edge of the reference graph" or "the expected Q sequence equals the paper's".
- **Exact counters.** A counter shows the number of cells actually drawn, and lands exactly on the paper's value.
- **Numpy layers** for huge unit charts (millions of cells): composite a numpy raster into the frame. Remember that this layer cannot become vector in SVG/PDF exports.
- **Motion blur**: `blur_n(t)` returns the number of sub-frames (1 = no blur). Turn it on only for fast camera moves. Use a 180° shutter.

## Review loop

```bash
python3 render.py stills --w 1280 --times 5 12.5 21 33.5     # key moments
python3 scripts/contact_sheet.py film.mp4 --fps 1 --out sheet.png   # whole film
```

Look at every still you render before moving on. Problems that only show up in stills:

- labels crossing long arcs (fix with a white knockout behind header blocks);
- text clipped at the frame edge;
- ghost discs left by glows on white;
- legends colliding with data labels.
