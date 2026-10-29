"""Demo score + SFX cued from film.CUES (animation clock) via edl.inv."""
import os, sys
here = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [os.path.join(here, "src"), os.path.join(here, "..", "..", "scripts"),
                os.path.join(here, "..", "..", "scripts", "audio")]
os.chdir(os.path.join(here, "src"))
import film, edl                                                # noqa: E402
from synth import Track, pad, tick, thump, bell                 # noqa: E402

D = film.DURATION + 1.5
music, sfx = Track(D), Track(D)
music.add(0.0, pad(["D3", "A3", "F4"], 6.0), gain=.6)
music.add(5.0, pad(["D3", "A3", "F#4"], D - 5.0), gain=.6)
for k in range(4):
    sfx.add(edl.inv(film.T_CAND + .12 * k), tick(), gain=.35, pan=-.3 + .2 * k)
for k, (_, _, st) in enumerate(film.DATA["candidates"]):
    t = edl.inv(film.T_JUDGE + .1 * k)
    sfx.add(t, thump() if st == "pruned" else tick(2400), gain=.5)
sfx.add(edl.inv(film.T_DONE), bell(880), gain=.4)
os.makedirs("../out/audio", exist_ok=True)
music.write("../out/audio/music_src.wav", room=(4.0, 2200, .8))
sfx.write("../out/audio/sfx_src.wav", room=(2.6, 3000, .5))
print("cues placed; film", round(film.DURATION, 2), "s")
