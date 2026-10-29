# What's inside `skills/research-paper-film/`

```
(paths relative to skills/research-paper-film/)
SKILL.md                 the skill: ask-once intake, non-negotiables, draft-1 defaults,
                         checkpoints with critic loops, phases
references/00-quality-bar.md        definition of done (science, pacing, craft, sound, figures)
references/11-iteration-lessons.md  what each earlier version got wrong -> rules for draft 1
references/12-critic-loop.md        the generator's checkpoints K1-K7 and pre-handoff gates
references/18-review-loop.md        v7 loop: orchestrator / generator / independent reviewer, routing,
                                    human review every K rounds, requests to the user, stopping
references/19-reviewer.md           the reviewer's brief: video-only view, passes, severities, verdict
templates/review.md                 the reviewer's feedback format
references/13-paper-archetypes.md  what to show and how to say it, per CS/EE paper archetype
references/14-motion-camera-linkage.md  camera grammar, meaningful motion, pinned findings,
                                    beat choreography, calibration data (G and L gates)
references/15-wow-beats.md          peaks: setup/tension/reveal/hold, devices, the 2-per-film
                                    signature budget, peak sound (W gates)
references/16-argument-and-data.md  domain model first, data-level grounding, canonical glyphs,
                                    the skeptic pass, logic-chain check (R gates)
references/17-story-spine.md        story arc (title as the answer, one climax, reprise) and the
                                    persistent visual spine
references/01..10                   one deep-dive per phase + a table of pitfalls
templates/film_plan.md              the plan to fill in before building (archetype, walk instance vs replay,
                                    beats, shot list, linkage map, results)
templates/               brief, claim ledger, storyboard, audit report
scripts/
  engine.py              pycairo canvas in a 1920x1080 design space, easing, 3-D projection
  scene_kit.py           overlays, keyframes, look-at stage camera, billboard text, chips, markers
  motion_kit.py          camera direction (beat_keys, lagged, View2), focus, tracer, proposal, pulse,
                         pinned callouts, tethers, fixed-address AddressTable, pills/slots, breadcrumb
  viz_kit.py             CS/EE components in the house style: waveform, graph, state table, axes,
                         bars, lines, scatter + Pareto, unit histogram, unit block + lens,
                         block diagram + wires, PE/heat grid, pipeline/timeline, callouts
  render.py              stills / video segments (raw RGB -> ffmpeg x264, -tune animation)
  render_chunks.sh       resumable, parallel chunked render
  assemble.sh            concat + mux (-t DUR, never -shortest) + master/4K/1080p + loudness readout
  edl.py                 narration-first retime: piecewise-linear warp, word anchors, overlap check
  subtitles.py           SRT cues timed by spoken-word count
  audit.py               readability audit (how long each string is readable)
  gate.py                PASS/FAIL gates: readability, EDL, loudness, durations, SRT, mix,
                         motion (G1-G4, --motion)
  motion_audit.py        per-second motion and camera measurement of a video (static %, freezes,
                         camera %, mean change; per act)
  linkage_audit.py       finds findings (=, ≠, →, δ, pruned, conflict…) drawn without an anchor
  peak_kit.py            peak plan + budget (<= 2 signature breaks), cascade, collapse, exact
                         counters, number land, log zoom, breath; night / spot / accent / flood
  wow_audit.py           W1-W7: plan, reveal contrast, hold, signature budget, sound cue,
                         key word, claim + trade-off (gate.py --wow)
  data_kit.py            loop-nest tile contents, element grids, 3-D slabs, same-element links,
                         load meters, the canonical Storage glyph and its icon
  loopnest_sim.py        cycle-level loop-nest model: MACs per PE per cycle, storage tiles,
                         fills, reads -> destination PEs, utilisation
  argument_audit.py      R1-R11: metric + held fixed, define before use, doubt before ablation, coverage, no redundancy, budget,
                         spreads, data views, colours, domain-model checks, canonical glyphs
  contact_sheet.py       1-fps contact sheets of a video
  review_pack.py         the reviewer's video-only view: sheets, 1080p stills, timeline (change,
                         camera, audio, silences, subtitles), motion gates, loudness, transcript
  narration/             Kokoro TTS, sherpa-onnx ASR, line synthesis, word alignment,
                         voice casting, line regeneration, mix and SRT intelligibility checks
  audio/                 procedural score/SFX (licence-clean) and the mixer
                         (ducking, -16 LUFS, <= -1.2 dBTP)
  figures/               figkit (patched loader, text filter, margin canvas, PNG/SVG/PDF export),
                         lint_figs (min text pt, aspect, fonts, identical crops),
                         verify_vectors, setup_fonts (true Inter Regular for cairo)
examples/
  gallery/               one slide figure per archetype, built only from viz_kit (gallery.py)
  minimal/               an ~11 s toy film that runs the whole pipeline (run_demo.sh)
  motion_kit_demo/       a 12 s mechanism beat built with motion_kit; passes G1-G4 and L1
  peak_demo/             a 30 s, 3-peak demo with 2 signature breaks; passes W1-W7, G1-G4, L1
  bflex/                 the full case study: film, model, narration, figures and docs
                         (docs/FRESH_REBUILD_POSTMORTEM.md + compare_v4_vs_fresh.png)
```
