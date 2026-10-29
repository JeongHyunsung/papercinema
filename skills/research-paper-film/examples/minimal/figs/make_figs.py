"""Demo: slide figures from the demo film without modifying it.
Removes the corner tag (an overlay) and exports the final state as
PNG/SVG/PDF, plus a two-step sequence sharing one crop."""
import os, sys
here = os.path.dirname(os.path.abspath(__file__))
S = os.path.join(here, "..", "..", "..", "scripts")
sys.path[:0] = [os.path.join(here, "..", "src"), S, os.path.join(S, "figures")]
os.environ.setdefault("NARRATION_DIR", os.path.join(here, "..", "narration"))
import figkit as FK                                             # noqa: E402
FK.use_inter()                         # all engine font names -> Inter
FK.use_contrast()                      # darker greys for slides
F = FK.load_patched(os.path.join(here, "..", "src", "film.py"),
                    patches=[('cv.text(1400, 960, "2 of 4 survive"',
                              'cv.text(1400, 960, "" and "2 of 4 survive"')],
                    nop=["tag"])
FK.DROP |= {"toy example"}
out = os.path.join(here, "out")
steps = {"step1_candidates": 1.9, "step2_judged": 3.4}
fns = {k: (lambda t: (lambda cv: F.draw_anim(cv, t)))(t) for k, t in steps.items()}
box = FK.union_box([FK.box_of(f) for f in fns.values()])
for k, f in fns.items():
    print(FK.export(k, f, out, k=2, box=box, M=300)[0])
