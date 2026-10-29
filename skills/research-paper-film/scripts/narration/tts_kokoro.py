"""Kokoro-82M v1.0 (Apache-2.0) local TTS via kokoro-onnx.

Model files (not included): kokoro-v1.0.onnx and voices-v1.0.bin from the
GitHub release thewh1teagle/kokoro-onnx 'model-files-v1.0'. Put them in
$KOKORO_DIR (default ./models).
"""
import os
import numpy as np

M = os.environ.get("KOKORO_DIR", "models")
_k = None


def kokoro():
    global _k
    if _k is None:
        from kokoro_onnx import Kokoro
        _k = Kokoro(os.path.join(M, "kokoro-v1.0.onnx"),
                    os.path.join(M, "voices-v1.0.bin"))
    return _k


def synth(text, voice, speed=1.0, lang="en-us"):
    a, sr = kokoro().create(text, voice=voice, speed=speed, lang=lang)
    return np.asarray(a, np.float32), sr
