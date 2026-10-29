# 10: Pitfalls met in production, and their fixes

| Symptom | Cause | Fix |
|---|---|---|
| Some 4K chunks never finish; the log stops mid-way | Too many parallel workers; OOM-killed silently | Lower `JOBS`; check that every log ends with `done`; re-run (finished chunks are skipped) |
| Wait loop never ends | `pgrep -f render.py` matches the waiting shell's own command line | `pgrep -f "[r]ender.py"`, or test the logs for `done` |
| `No space left on device` mid-render | Old chunks and intermediates; per-session disk quota (`df` misleads) | Delete old renders and intermediates before starting; free space is reusable immediately |
| Final MP4 shorter than the film | `-shortest` with a subtitle stream ends at the last cue | Always `-t $DUR` from the EDL |
| Subtitle cue breaks mid-sentence or lags the voice | Cue boundaries computed by character share | Count spoken words per chunk via a print → spoken table, and assert the totals |
| Soft subtitles show by default in some players | The MP4 muxer marks `mov_text` enabled | Document it; ship the `.srt` separately |
| Grey ghost discs on white | Glow dots designed for a dark background | No glows on white; use faint flat tints |
| Unit chart invisible on white | Additive compositing (light on dark) | Alpha-over, with a darker growing front |
| Header crossed by a long arc edge | Arc drawn over the header area | White knockout rectangle behind the header block (remove it in figure mode) |
| Labels readable for < 1 s | Designed for the silent cut, then retimed | Readability audit; extend holds in the EDL; move facts into the scene or the narration |
| Facts vanished when the caption band was removed | Captions carried unique facts | List every caption fact and re-home each one in its scene (accuracy checklist) |
| Narration line stretched to fit | — | Never. Retime the picture (EDL); lengthen the segment before the clip |
| Data race no longer proportional | Its EDL segment was not at slope 1 | Keep data-encoding segments at slope 1, and check in the timing sheet |
| Overclaiming wording | "is", "the simplest", "circuits", tool vs design | Scientific audit classes (references/08) |
| Slide figures look like a mess | Mid-animation frame captures pasted together | Purpose-built compositions; fixed orthographic camera; identical crops (references/09) |
| Far elements tiny in step figures | Perspective camera | Near-orthographic camera (distant eye, matching focal length) |
| Text in the figure is the wrong weight | fontconfig resolves "Inter" to Medium for cairo's toy API | Renamed font copy ("Inter Regular"); check with `pdffonts` |
| Figure content cut at the left | Film camera shifts the stage off-frame | Margin canvas and content-box crop |
| Boosted text doubled in size inside chips | `text()` calls `measure()`, and both were boosted | Re-entrancy flag: no boost inside `text()`'s own measure |
| Patched film source fails silently | Patch target text not found or not unique | Assert `src.count(target) == 1` for every patch |
| Requested "real" example doesn't exist | The method's structure forbids it (e.g. no cycles in generated settling paths) | Search, report the size of the search, and offer a labelled illustration |
| Chat refuses a preview image | Image > 8000 px per side | Send a downscaled preview; put the originals in the zip |
| Every gate passes but the film feels like slides | Gates measured only legibility, science and delivery | `motion_audit.py` + `gate.py --motion` (G1–G4); choreograph beats with references/14 §4 |
| Camera never moves in the centrepiece | One fixed StageCam keyframe set | `beat_keys(wide, beats)`: push-in, hold with drift, pull-back per beat |
| Labels float near the graph; viewers can't tell what they refer to | Annotations drawn as free chips | `callout_at(anchor, …)` with leader + dot; `linkage_audit.py` (L1) |
| "Show me where that goes in the table" | Table rows appended as they are written | `AddressTable` with every address present; `tether()` node → row per event |
| Pruning looks arbitrary | Only reached states drawn | `pill()` with ghost / live / pruned slots: show the space pruned from |
| Centrepiece too dense to zoom into | Walked the headline design's full search | Walk the paper's smallest running example; replay the headline design later |
| A 1-fps contact sheet looks fine, the film still feels dead | Stills cannot show motion | Watch at 1× with sound; read the per-second list of `motion_audit.py` |
