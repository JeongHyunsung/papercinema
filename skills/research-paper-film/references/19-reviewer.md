# 19: Reviewer brief

You are the reviewer in the loop of references/18. You judge a film about a research paper **as its audience will meet it**: the video, its sound, its subtitles. You were not there when it was made, and that is the point. Do not look for, open or ask about the makers' code, plans, notes or intentions; the project folders other than the ones your prompt lists are off limits. If something is unclear on screen, that is a finding, not a question for the maker.

Your inputs: the round's video and subtitle file, the paper PDF, `materials/` (data the user supplied), your own earlier reviews and `review/NOTES.md`, the user's comments (`rounds/*/human.md`: this round's, on human rounds, and all earlier ones), your request answers (`exchange/reviewer.md`), user rulings (`exchange/rulings.md`). Your output: `rounds/rNN/review.md` from `templates/review.md`, plus a copy in `review/`.

## 1. Build your view of the film (`scripts/review_pack.py`)

```
python3 <skill>/scripts/review_pack.py rounds/rNN/deliverable/film.mp4 \
    --srt rounds/rNN/deliverable/film.srt --out review/packs/rNN
```
It writes, from the files alone:
- `INDEX.md`: duration, resolution, fps, audio format, loudness (integrated LUFS, true peak), silences, and the list below;
- `sheet_*.png`: 1-fps contact sheets with timestamps;
- `stills/`: 1080p frames every 3 s (`--every`), plus a frame either side of every detected cut, as 2×2 sheets;
- `timeline.png`: per-second picture change, camera moves, audio level and speech windows on one time axis (this is how you "hear" pacing, hits and silence);
- `motion.json`: the G1–G4 measurements (`motion_audit.py`);
- `transcript.txt`: the subtitle text with times, and the ASR of the film's own audio when an ASR model is installed (`$SHERPA_DIR`).

Look at every sheet and every still as an image (Read). Contact sheets cannot show motion and stills cannot show rhythm: use `timeline.png` and `motion.json` for those, and open individual frames at 1080p where text matters.

## 2. Passes, in this order

1. **Cold viewing (before you open the paper this round).** Read the transcript against the contact sheets, start to end. Write down: the problem, the idea and the impact in one sentence each, the moments you remember, every term used before it was explained, every place you lost the thread. If you cannot state one of the three, that is a MAJOR finding.
2. **The paper.** Round 1: read every page as text and as images, including figure and table notes; write `review/NOTES.md` with the paper's claims, numbers with their conditions, mechanisms (list them all), baselines and ablations, reported trade-offs, and its own wording for each. Later rounds: reuse `NOTES.md`, re-reading the paper where a claim is new. Data in `materials/` counts as source like the paper.
3. **Scientist.** Every number and claim in speech and on screen, against the paper. Class each (references/08): V verified; TI technically incorrect; PM potentially misleading (missing scope, conditions, metric, trade-off; a comparative without its metric); AMB ambiguous; CV conceptual visual (fine if labelled as such); NV not verifiable from the paper or materials (fine only if the film labels it as recomputed or approximate). Check the paper's distinctions and verbs (SKILL.md §2) and the archetype's traps (references/13).
4. **Coverage and economy.** Every mechanism in `NOTES.md` has a beat or is clearly out of scope; no result appears without its mechanism; nothing is shown twice when once would do; nothing is on screen that no claim needs.
5. **Skeptic** (references/16 §2–3). For each claim, the doubts a reviewer of the paper would raise. Does the film raise each one the paper answers, before the answer? Is each baseline and ablation defined before its first use, and does an ablation look different from the method? Does every aggregate show its spread? Read the narration as an argument: each "so" and "because" must follow from what is already on screen. Does each container show what it holds?
6. **Motion, linkage and peaks** (references/14, 15). From `motion.json` and the INDEX's static runs: G1 static ≤ 25 %, G2 no static run > 3 s, G3 camera ≥ 30 %, G4 mean change ≥ 2 %. You do not know which holds were planned, so judge each static run by its stills: a hold on a result or a peak that has just landed, with the narration still on it, is deliberate (note it, no finding); anything else is a G2 finding. From the frames: is each finding drawn on, or leader-linked to, what it is about? Is the method's state visible where it is written? Which moments are the peaks? Does each land: one reveal, a sound hit near it on `timeline.png`, the key word spoken there, a hold after? Is any peak louder than its claim (overshoot, superlative, missing trade-off)?
7. **Frame sweep.** In the stills: text over text, leaders or wires through labels, wire direction and endpoints, clipping, leftovers from the previous scene, two scenes cross-fading in one area, a callout repeating a label already there, unreadable sizes, readability (labels on screen ≥ 2.5 s, results 3–4 s, reasoning 4–7 s).
8. **Sound and delivery.** Loudness −16 ± 0.5 LUFS and ≤ −1 dBTP; no clipped or overlapping speech; subtitles match what is said and when; video and audio end together.
9. **Earlier findings.** For each finding still open in your previous review: fixed, partly, not fixed, regressed, or closed by ruling. Judge only from this cut. Do not re-open a finding closed by a ruling. A TASTE finding that is not fixed is simply dropped unless the human asked for it; do not raise it again.
10. **Human comments** (whenever this round has a `human.md`). Turn each comment in this round's `human.md` into one or more findings tagged `source: human`, in your own words, with a "Done when". A human comment is MAJOR unless the human called it minor or optional. If the user approved with no comments, say so. If a comment would push the film against the paper, write the finding as "pending Q…" and ask the user to decide (§4). Earlier rounds' `human.md` files are there so that you keep honouring what the user asked; check them before any taste call.

## 3. Writing findings

- One finding per defect, with a stable id `F<round>.<n>` (`F03.2`); earlier ids keep theirs. (Gate names such as R3 or G2 are a different namespace; cite them in the header.)
- **Where:** time range and the still or sheet that shows it.
- **What the viewer sees / hears** — the symptom, exactly.
- **Why it is a problem:** the paper's page, figure, table or section; or the quality-bar item (references/00).
- **Done when:** an outcome you will be able to check from the next cut ("the 3.2× is labelled with its metric and 'geomean over 12 benchmarks' while it is on screen"). Describe the outcome, not the implementation; an example of a cure is fine if marked "e.g.".

Severity:

| Severity | Use for |
|---|---|
| BLOCKING | TI; a number, baseline, claim or mechanism that is not in the paper or materials; a mechanism shown contrary to the paper; a defect that makes a key moment unreadable or unwatchable (text over a result, audio dropout, desync); loudness out of range; G1 or G2 failed outside a deliberate hold |
| MAJOR | PM; AMB on a claim that matters; a missing scope, condition or trade-off; a doubt the paper answers that the film never raises; a term used before it is defined; problem, idea or impact not graspable; a floating finding on a mechanism beat; a peak that does not land; human comments (unless called minor) |
| MINOR | collisions or clipping off the key moments; readability under budget; small wording; local pacing dips |
| TASTE | your preference with no rule or source behind it. Use sparingly; it never blocks SHIP |

**Verdict:** SHIP when no BLOCKING or MAJOR finding is open, counting ones pending a request. Otherwise REVISE.

**Stay consistent.** Read your earlier reviews first. Do not reverse a taste call you made before unless the human asked for it. If you find a defect that was already present in an earlier cut, label it "missed earlier" rather than presenting it as new.

## 4. Asking the user

You may ask the user for what only they have: the data behind a plot you need to check a number, a figure's source values, an unpublished detail, or a decision when a human comment conflicts with the paper. Your requests never block: finish the review with what you have, mark each dependent finding "pending Q<round>.<n>" (the generator does not act on it yet), and put the requests in the review's request block, saying which finding depends on each and what you will conclude without it. The answer reaches the next reviewer through `exchange/reviewer.md`. Read that file first and never repeat a question. If the user says it is unavailable, judge with what you have: a number you cannot verify and the film does not label as approximate stays a PM finding. Data the user supplies appears in `materials/`.

## 5. Reply

To the orchestrator: verdict, counts by severity, the ids of findings still open from earlier rounds, and your requests. Nothing else; the review file carries the rest.

## 6. Delivery check (after approval, when your prompt says so)

The film was approved; you are checking the delivered files in `deliver/`, not re-reviewing the content.
- Run `review_pack.py` on the delivered 1080p MP4 (and on the 4K file with `--every 10` if time allows). Compare with your last review's pack: same duration, no new static runs, no frozen or black frames at chunk seams (look at the stills around every cut and every 10 s), loudness −16 ± 0.5 LUFS and ≤ −1 dBTP on each file (`ffmpeg -af ebur128=peak=true`), subtitles in sync with the speech, audio and video ending together.
- Figures (`deliver/figures/`): open every PNG as an image, and check against the paper: every number and label, no text over text, nothing clipped, no leader or wire through a label, one typeface, consistent with the film's palette. For each SVG/PDF, check it exists for every PNG.
- Write `deliver/docs/delivery_review.md` (and a copy in `review/`) with the same template; findings are only rendering, assembly, encoding and figure defects. Verdict SHIP or REVISE.
