"""Negative test: a broken peak plan must FAIL W2, W4, W5 and W7 on the demo video.

  python3 neg_test.py        (after rendering out/demo.mkv and running film.py)
"""
import json, subprocess, sys

p = json.load(open("out/peaks.json"))
p["peaks"][1]["signature"] = None                      # night stage left undeclared   -> W4
p["peaks"][2].update(t_setup=24.6, t_reveal=26.5, t_hold=29.5)   # reveal on a quiet second -> W2, W5, W7
p["peaks"][0]["claim"] = "T9"                          # claim not in the ledger       -> W7
json.dump(p, open("out/peaks_bad.json", "w"))
r = subprocess.run([sys.executable, "../../scripts/wow_audit.py", "--peaks", "out/peaks_bad.json",
                    "--video", "out/demo.mkv", "--cues", "out/cues.json", "--ledger", "LEDGER.md"],
                   capture_output=True, text=True)
fails = {l.split()[0] for l in r.stdout.splitlines() if l.split()[1:2] == ["FAIL"] and l.startswith("W") and not l.startswith("WOW")}
print(r.stdout)
assert fails == {"W2", "W4", "W5", "W7"}, fails
print("negative test OK: W2, W4, W5, W7 fail as intended")
