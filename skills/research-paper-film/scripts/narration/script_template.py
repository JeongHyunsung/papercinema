"""Narration script: the single source of truth for words.

Copy to your narration/ folder as script.py.
  sub  : printed text (subtitles, transcript)
  tts  : the same words respelled for the TTS front end (acronyms, letters,
         numbers in words, commas for breaths)
  gap  : edited silence after the line (s); speech itself is never stretched
SPOKEN maps printed tokens -> spoken words; subtitles.py and srt_check.py use
it to count spoken words per subtitle cue.
"""
LINES = [
    dict(id="L01", sub="A flip-flop has one job: on a rising clock, capture D and hold it.",
         tts="A flip-flop has one job: on a rising clock, capture dee, and hold it.", gap=.5),
    dict(id="L02", sub="At three state bits, the search finds all 568 million valid state machines.",
         tts="At three state bits, the search finds all five hundred sixty-eight million valid state machines.", gap=.8),
]

SPOKEN = [  # longest first where prefixes overlap
    ("568", "five hundred sixty-eight"),
    ("D", "dee"),
    ("Q", "queue"),
]
