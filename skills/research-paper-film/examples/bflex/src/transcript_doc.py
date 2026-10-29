"""docs/V5_TRANSCRIPT.md: the complete corrected narration with timestamps."""
import sys, os, edl
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "narration"))
import script
def tc(t):
    m, s = divmod(t, 60); return f"{int(m)}:{s:05.2f}"
subs = {l["id"]: l["sub"] for l in script.LINES}
old = {}
try:
    import importlib.util
    sp = importlib.util.spec_from_file_location("s4", os.path.join(os.path.dirname(__file__), "..", "narration", "script_v4.py"))
    m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); old = {l["id"]: l["sub"] for l in m.LINES}
except Exception:
    pass
span = {}
for c in edl.clips():
    a, b = span.get(c["line"], (1e9, 0)); span[c["line"]] = (min(a, c["start"]), max(b, c["end"]))
L = ["# B-Flex V5: complete narration transcript", "",
     f"Film runtime {edl.DURATION:.1f} s. Voice: Kokoro-82M `af_heart`, the same as V4. Times are on the V5 film clock.",
     "Lines marked ✎ were revised in V5; see `V5_LANGUAGE_LOG.md`.", "",
     "| # | in | out | narration | |", "|---|---|---|---|---|"]
for l in script.LINES:
    a, b = span[l["id"]]
    mark = "✎" if old and old.get(l["id"]) != l["sub"] else ""
    L.append(f"| {l['id']} | {tc(a)} | {tc(b)} | {l['sub']} | {mark} |")
L += ["", "Word-level timings are in `src/out/audio_v4/placement.json`; subtitles are in `BFlex_DAC2026_film_v5.en.srt`."]
open("../docs/V5_TRANSCRIPT.md", "w").write("\n".join(L) + "\n")
print("\n".join(L))
