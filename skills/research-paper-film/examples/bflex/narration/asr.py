"""Offline English ASR with token timestamps (sherpa-onnx zipformer, Apache-2.0)."""
import numpy as np, sherpa_onnx, soundfile as sf
import os
D = os.environ.get("SHERPA_DIR", "models/sherpa-onnx-zipformer-en-2023-06-26") + "/"
_r = None
def rec():
    global _r
    if _r is None:
        _r = sherpa_onnx.OfflineRecognizer.from_transducer(
            encoder=D+"encoder-epoch-99-avg-1.onnx", decoder=D+"decoder-epoch-99-avg-1.onnx",
            joiner=D+"joiner-epoch-99-avg-1.onnx", tokens=D+"tokens.txt", num_threads=4,
            decoding_method="greedy_search")
    return _r
def resample16(a, sr):
    if sr == 16000: return a
    from scipy.signal import resample_poly
    from math import gcd
    g = gcd(sr, 16000); return resample_poly(a, 16000//g, sr//g).astype(np.float32)
def transcribe(a, sr):
    a = resample16(a, sr)
    s = rec().create_stream(); s.accept_waveform(16000, a); rec().decode_stream(s)
    r = s.result
    return r.text, list(r.tokens), list(r.timestamps)
