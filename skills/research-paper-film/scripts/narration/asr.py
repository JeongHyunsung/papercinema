"""Offline English ASR with token timestamps (sherpa-onnx zipformer, Apache-2.0).

Model (not included): sherpa-onnx-zipformer-en-2023-06-26 from the
k2-fsa/sherpa-onnx release 'asr-models'. Set $SHERPA_DIR to its folder.
"""
import os
import numpy as np

D = os.environ.get("SHERPA_DIR", "models/sherpa-onnx-zipformer-en-2023-06-26")
_r = None


def rec():
    global _r
    if _r is None:
        import sherpa_onnx
        j = lambda f: os.path.join(D, f)        # noqa: E731
        _r = sherpa_onnx.OfflineRecognizer.from_transducer(
            encoder=j("encoder-epoch-99-avg-1.onnx"),
            decoder=j("decoder-epoch-99-avg-1.onnx"),
            joiner=j("joiner-epoch-99-avg-1.onnx"), tokens=j("tokens.txt"),
            num_threads=4, decoding_method="greedy_search")
    return _r


def resample16(a, sr):
    if a.ndim > 1:
        a = a.mean(1)
    if sr == 16000:
        return a.astype(np.float32)
    from math import gcd
    from scipy.signal import resample_poly
    g = gcd(sr, 16000)
    return resample_poly(a, 16000 // g, sr // g).astype(np.float32)


def transcribe(a, sr):
    """-> (text, tokens, token start times in s)."""
    a = resample16(np.asarray(a, np.float32), sr)
    s = rec().create_stream()
    s.accept_waveform(16000, a)
    rec().decode_stream(s)
    r = s.result
    return r.text, list(r.tokens), list(r.timestamps)
