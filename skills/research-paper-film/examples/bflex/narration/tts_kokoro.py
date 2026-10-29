"""Kokoro-82M v1.0 (Apache-2.0) local synthesis helper."""
import os, numpy as np
from kokoro_onnx import Kokoro
M = os.environ.get("KOKORO_DIR", "models")
_k = None
def kokoro():
    global _k
    if _k is None:
        _k = Kokoro(os.path.join(M, "kokoro-v1.0.onnx"), os.path.join(M, "voices-v1.0.bin"))
    return _k
def synth(text, voice, speed=1.0, lang="en-us"):
    a, sr = kokoro().create(text, voice=voice, speed=speed, lang=lang)
    return np.asarray(a, np.float32), sr
