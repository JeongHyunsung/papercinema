"""Argument audit: would a careful, skeptical reader accept each step? (quality bar R1-R11)

Reads the argument map a film exports (film.ARGUMENT -> argument.json) and, optionally,
the readability audit JSON (every on-screen string with its readable time), so the checks
are about what is actually on screen.

  python3 argument_audit.py --arg out/argument.json --audit out/audit.json --json out/arg.json
  python3 gate.py ... --arg out/arg.json

argument.json:
  {"defs":   [{"term": "Method-minus-X", "t": 101.2, "screen": "Method-minus-X: ..."}],
   "claims": [{"id": "R6", "kind": "ablation", "t": 104.5, "metric": "latency",
               "held_fixed": ["dataset", "budget"], "removed": "component X",
               "uses": ["Method-minus-X", "Baseline A"],
               "spread": "7 / 9 benchmarks",            # aggregates: range, wins, n
               "doubts": [{"q": "is it just component Y?", "t_raised": 101.0,
                           "screen": "just component Y?", "answered_by": "R6", "t_answer": 104.5}],
               "data_view": null}],                       # mechanism claims: true when contents shown
   "mechanisms": [{"id": "rule1", "t": 61.4, "about_data": true, "data_view": true,
                   "asserted": true}]}

  R1  comparisons and ablations name the metric and what is held fixed (ablations: also what is
      removed); with --audit, the held-fixed / removed wording is on screen (substring)
  R2  every term a claim uses is defined on screen before the claim (t_def <= t_claim)
  R3  every ablation has a doubt raised before its result; every doubt is answered by a claim
      shown later (t_raised < t_answer) or explicitly acknowledged (an "acknowledged" field)
  R4  aggregates (geomean, mean, totals) show their spread (range / wins / n) on screen
  R5  mechanism beats about storage or data show element-level contents, computed and asserted
      (data_kit.loop_nest_tile); a box with only a name fails
  R6  baselines and ablations never share the method's colour (declared "colour" fields differ)
  R7  the domain model is validated: "model_checks" is non-empty and every check passed, and every
      mechanism about data names the model it is drawn from ("model")
  R8  recurring concepts use their canonical glyph: every mechanism about data names a glyph that
      is registered in "glyphs" (concept -> glyph), and each registered glyph is used >= 3 times
  R9  coverage: every mechanism / effect / contribution the paper claims ("coverage": item -> where)
      has a beat, or an explicit omission with its reason; a result shown without the mechanism that
      produces it is a FAIL (list the result's mechanism in "coverage")
  R10 no redundancy: each claim has ONE primary visual ("visuals": claim -> [beats]); a claim drawn
      twice (a good figure, then a weaker re-draw of the same point) FAILs unless the second beat is
      declared "callback" (same glyph, adds a new fact)
  R11 budget: when "target_s" and "beats" ([{"id", "s", "needed_for"}]) are given, the film fits the
      target, and every beat names the claim or definition it is needed for (detail no claim needs
      is cut, not shortened)
"""
import argparse, json, sys

ap = argparse.ArgumentParser()
ap.add_argument("--arg", required=True)
ap.add_argument("--audit")
ap.add_argument("--json")
ap.add_argument("--budget", type=float, default=2.5)
a = ap.parse_args()
A = json.load(open(a.arg))
seen = {}
if a.audit:
    seen = {k: v.get("best", 0) for k, v in json.load(open(a.audit)).items()}
rows, gates = [], []


def gate(code, ok, msg, warn=False):
    st = "PASS" if ok else ("WARN" if warn else "FAIL")
    rows.append(f"{code:3s} {st:4s}  {msg}")
    gates.append(dict(code=code, status=st, msg=msg))


def on_screen(s):
    """True when s is a substring of a string readable for >= budget seconds."""
    if not a.audit or not s:
        return True
    return any(s in k and v >= a.budget for k, v in seen.items())


defs = {d["term"]: d for d in A.get("defs", [])}
claims = {c["id"]: c for c in A.get("claims", [])}
for d in A.get("defs", []):
    gate("R2", on_screen(d.get("screen", d["term"])), f"definition of '{d['term']}' on screen"
         f" ({d.get('screen', d['term'])!r})")
for c in A.get("claims", []):
    k = c["kind"]
    if k in ("comparison", "ablation"):
        ok = bool(c.get("metric")) and bool(c.get("held_fixed"))
        if k == "ablation":
            ok = ok and bool(c.get("removed"))
        shown = all(on_screen(s) for s in c.get("held_fixed_screen", []))
        gate("R1", ok and shown, f"{c['id']}: metric={c.get('metric')}, held fixed={c.get('held_fixed')}"
             + (f", removed={c.get('removed')}" if k == "ablation" else "") + ("" if shown else " (not on screen)"))
    for u in c.get("uses", []):
        d = defs.get(u)
        ok = d is not None and d["t"] <= c["t"]
        gate("R2", ok, f"{c['id']} uses '{u}': " + (f"defined at {d['t']:.1f} s, claim at {c['t']:.1f} s"
                                                     if d else "never defined on screen"))
    if k == "ablation":
        early = [q for q in c.get("doubts", []) if q.get("t_raised", 1e9) < c["t"]]
        gate("R3", bool(early), f"{c['id']}: doubt raised before the ablation result ({len(early)})")
    for q in c.get("doubts", []):
        if "acknowledged" in q:
            gate("R3", on_screen(q.get("screen")) and bool(q["acknowledged"]),
                 f"{c['id']}: '{q['q']}' acknowledged: {q['acknowledged']}")
            continue
        ans = claims.get(q.get("answered_by"))
        ok = ans is not None and q.get("t_raised", 1e9) < q.get("t_answer", -1) and on_screen(q.get("screen"))
        gate("R3", ok, f"{c['id']}: '{q['q']}' raised {q.get('t_raised')} s -> answered by "
             f"{q.get('answered_by')} at {q.get('t_answer')} s")
    if k == "aggregate":
        gate("R4", bool(c.get("spread")) and on_screen(c.get("spread")),
             f"{c['id']}: spread {c.get('spread')!r}" + ("" if on_screen(c.get("spread")) else " (not on screen)"))
for m in A.get("mechanisms", []):
    if m.get("about_data"):
        gate("R5", bool(m.get("data_view")) and bool(m.get("asserted")),
             f"mechanism '{m['id']}': contents shown={m.get('data_view')}, computed+asserted={m.get('asserted')}")
mc = A.get("model_checks", [])
gate("R7", bool(mc) and all(c.get("ok") for c in mc),
     f"{sum(bool(c.get('ok')) for c in mc)} / {len(mc)} domain-model checks pass"
     + ("" if mc else " (no model checks: understand before drawing)"))
for m in A.get("mechanisms", []):
    if m.get("about_data"):
        gate("R7", bool(m.get("model")), f"mechanism '{m['id']}' drawn from model: {m.get('model')}")
gl = A.get("glyphs", {})
uses = {}
for m in A.get("mechanisms", []):
    if m.get("about_data"):
        g = m.get("glyph")
        uses[g] = uses.get(g, 0) + 1
        gate("R8", g in gl.values(), f"mechanism '{m['id']}' uses canonical glyph: {g}")
for concept, g in gl.items():
    n = A.get("glyph_uses", {}).get(g, uses.get(g, 0))
    gate("R8", n >= 3, f"glyph '{g}' for '{concept}' used {n} times (>= 3)")
for c in A.get("coverage", []):
    ok = bool(c.get("where")) or bool(c.get("omitted"))
    gate("R9", ok, f"coverage '{c['item']}': " + (c.get("where") or f"omitted ({c.get('omitted')})")
         if ok else f"coverage '{c['item']}': no beat and no reasoned omission")
for k, vs in A.get("visuals", {}).items():
    prim = [v for v in vs if not str(v).startswith("callback:")]
    gate("R10", len(prim) <= 1, f"claim {k}: primary visuals {prim}" + ("" if len(prim) <= 1 else
         " (redraws the same point: keep the strongest, or make the second a declared callback)"))
if A.get("target_s"):
    dur = A.get("duration_s")
    if dur is not None:
        gate("R11", dur <= A["target_s"], f"duration {dur:.1f} s vs target {A['target_s']:.0f} s")
    for b in A.get("beats", []):
        gate("R11", bool(b.get("needed_for")), f"beat '{b['id']}' ({b.get('s', 0):.1f} s) needed for: "
             f"{b.get('needed_for') or 'nothing named: cut it'}")
cols = A.get("colours", {})
if cols:
    ours = cols.get("method")
    clash = [k for k, v in cols.items() if k != "method" and v == ours]
    gate("R6", not clash, f"method colour {ours}; clashes: {clash or 'none'}")
print("\n".join(rows))
nf = sum(g["status"] == "FAIL" for g in gates)
print("ARGUMENT", "PASS" if nf == 0 else f"FAIL ({nf})")
if a.json:
    json.dump(dict(gates=gates), open(a.json, "w"), indent=1)
sys.exit(1 if nf else 0)
