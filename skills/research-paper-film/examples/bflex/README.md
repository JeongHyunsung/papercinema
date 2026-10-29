# Case study: B-Flex (DAC 2026)

The production this skill was distilled from. B-Flex: *Exploration of Broader Flip-Flop Design Space Based on FSM Exhaustive Search*, DAC 2026, doi:10.1145/3770743.3804333.

**Result:** a 119-second narrated 4K60 film and a slide-figure set, built in this order:

| Version | What was made |
|---|---|
| v1–v3 | Silent cut, ~62 s |
| v4 | White identity, Kokoro narration, narration-first retime, procedural mix, SRT |
| V5 | Paper-grounded scientific audit and narration polish |
| Figures | Slide figures |

**Not included:**
- the paper PDF and page renders (read the paper from the publisher);
- rendered media and audio;
- TTS/ASR model weights;
- fonts.

| Phase (SKILL.md) | Files here |
|---|---|
| 1. Paper study and re-implementation | `src/bflex_model.py`, `src/scene_data.py` → `data/scene_data.json`; `docs/VERIFICATION.md` |
| 2. Storyboard | `docs/STORYBOARD.md`, timing constants at the top of `src/film.py` |
| 3. Engine and scenes | `src/engine.py`, `src/film.py` (`draw3` = animation clock, `draw` = film clock) |
| 4. Narration and retime | `narration/script.py`, `narrate.py`, `align.py`, `cast*.py`, `regen.py`; `src/edl.py`; `docs/VOICE_CASTING.md` |
| 5. Audio | `src/audio4.py` |
| 6–7. Subtitles, render, deliver | `src/subtitles.py`, `render_chunks_v5.sh`, `assemble_v5.sh` |
| 8. QA | `src/audit.py`, `narration/mix_check.py`, `narration/srt_check.py`; `docs/QA_REVIEWS_V4.md`, `docs/readability_audit_table.md`, `docs/ACCURACY_CHECKLIST_V4.md` |
| 9. Scientific audit | `docs/V5_SCIENTIFIC_VERIFICATION.md`, `docs/V5_LANGUAGE_LOG.md`, `docs/V5_TRANSCRIPT.md` |
| 10. Slide figures | `figs/figlib.py` (patched loader), `figs/design.py` (purpose-built figures), `figs/make_figs.py`, `figs/find_nonconv.py`, `figs/setup_fonts.py`; `docs/FIGURES_README.md` |

**Run.** Commands are in `PROJECT_README.md`. They assume this folder as the project root.

Quick checks with no models needed:

```bash
cd src && python3 render.py stills --w 960 --times 40 70   # needs pycairo, numpy, pillow
python3 edl.py                                            # narration placement check
cd ../figs && python3 setup_fonts.py && python3 make_figs.py --k 1 --preview
```
