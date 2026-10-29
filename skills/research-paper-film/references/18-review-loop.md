# 18: The review loop: generator, independent reviewer, human every K rounds

A producer cannot review its own film: it sees what it meant, not what is on screen. So the film is made by a **generator** and judged by a **reviewer** who never sees how it was made. A **human** joins the reviewer every K rounds. This file is the protocol for the orchestrator and the generator; references/19 is the reviewer's brief.

```
 paper PDF ─┬──────────────► GENERATOR ──── video (round r) ───► REVIEWER ◄── paper PDF
 intake  ───┘                    ▲                                 ▲  ▲
 (initial preferences)           │                                 │  └── own previous reviews
                                 │                                 └───── human review (every K-th round)
                                 └──────────── review.md (feedback) ◄──────┘
```

## 1. Roles

| Role | Who | Sees | Never sees |
|---|---|---|---|
| **Orchestrator** | the main agent, the one talking to the user | everything, to route it | — (it never authors film content and never paraphrases between roles) |
| **Generator** | one persistent subagent, named `generator` | the paper, `materials/`, `gen/` (incl. the intake brief), each round's `review.md`, `exchange/generator.md`, `exchange/rulings.md` | anything else: `review/`, `rounds/*/human.md`, `exchange/reviewer.md`, `LOOP.md` |
| **Reviewer** | a **fresh** subagent every round | the round's deliverable (video + subtitles), the paper, `materials/`, `review/` (its own earlier reviews and notes), every `rounds/*/human.md` so far, `exchange/reviewer.md`, `exchange/rulings.md` | anything else: `gen/`, `deliver/` (except in the delivery check), `exchange/generator.md`, `LOOP.md` |
| **Human** | the user | the cut every K-th round and every ship candidate; any request from either role; anything they ask the orchestrator for | — |

- The orchestrator is not the generator: it reads the human's comments verbatim, and the generator must meet them only through the reviewer.
- The reviewer does not see the intake brief: in this design the initial preferences go to the generator only. The reviewer judges the screen against the paper and the quality bar; the user's taste reaches it through the human rounds.
- Who reads which part of the skill:

  | Role | Reads |
  |---|---|
  | Orchestrator | SKILL.md §1 (intake), §2, §4, §6; this file |
  | Generator | SKILL.md §2, §3, §4 (checkpoint table), §5 phases 1–7 and 10; references/12; this file §1, §2, §6; the phase references. It skips everything addressed to the orchestrator (intake, AskUserQuestion, talking to the user) |
  | Reviewer | references/19; SKILL.md §2 and the appendix; references/00, 08, 13–17 as needed; `templates/review.md` |

## 2. Workspace layout (the routing is the file system)

The orchestrator creates the project in its working directory, e.g. `<cwd>/film-<short-name>/`, and writes the absolute path into every spawn prompt. Paths below are relative to it.

```
paper/paper.pdf                 shared source
materials/                      shared source: data the user supplied on request
  INDEX.md                      one line per file: file name and what it contains, in the user's words
gen/                            GENERATOR ONLY: code, BRIEF.md, plan, ledger, gates, renders, STATE.md
rounds/r01/
  deliverable/film.mp4          the review cut: 1080p30, narration, mastered mix
  deliverable/film.srt
  human.md                      human rounds only: the user's comments, verbatim ("none" allowed)
  review.md                     the reviewer's output: the ONLY thing passed to the generator
review/                         REVIEWER ONLY: copies of its reviews (r01.md …), NOTES.md, packs/
exchange/
  generator.md                  generator's requests and the user's answers
  reviewer.md                   reviewer's requests and the user's answers
  rulings.md                    the user's decisions on findings the GENERATOR disputed: id + decision only
deliver/                        after approval: final film files, figures/, docs/ (QA.md, report)
LOOP.md                         ORCHESTRATOR ONLY: K, max rounds, round table, findings ledger
```

- Round folders are `r01`, `r02`, … Finding ids are `F<round>.<n>` (`F03.2`: round 3, finding 2); request ids are `Q<round>.<n>` with a role prefix in the exchange files (`gen Q02.1`, `rev Q03.1`). Ids never change once given. (Gate names A1, G2, R7 … are a different namespace.)
- Subagents share one file system, so isolation is by instruction: each spawn prompt has an allow-list of paths and says everything else is off limits.
- The generator writes only under `gen/`, `rounds/rNN/deliverable/` and `deliver/` (except `deliver/docs/delivery_review.md`); the reviewer only under `review/`, `rounds/rNN/review.md` and, in the delivery check, `deliver/docs/delivery_review.md`; the orchestrator writes `LOOP.md`, `rounds/*/human.md`, `exchange/`, `materials/`, `deliver/docs/QA.md`, and copies a ship candidate's `deliverable/` into the next round (§8).
- What crosses from the generator to the reviewer is what an audience gets: the video and its subtitle file. No notes, no change list, no "what I fixed". What crosses back is `review.md`, nothing else.

## 3. Intake (orchestrator, once)

Ask the intake questions of SKILL.md §1 in one round: AskUserQuestion for the multiple-choice items (it takes up to four questions per call), and the free-form ones (numbers, which examples, constraints) in plain text in the same turn. Include:
- **K, the human-review period:** the user reviews the cut every K rounds (rounds K, 2K, …). Suggest 2; K = 1 means every round.
- **Maximum rounds** before the loop stops and asks (suggest 6).

Write the answers to `gen/BRIEF.md`; write K and the maximum to `LOOP.md`. Then spawn the generator (§7).

## 4. One round

Round r = 1, 2, …

1. **Generator builds or revises.**
   - Round 1: phases 1–5 (paper and model, story, engine, narration, audio) with the checkpoints K1–K3b, then the review cut.
   - Later rounds: read `rounds/r−1/review.md`, `exchange/rulings.md` and `exchange/generator.md`; act on every finding (§6); re-render the review cut.
   - Before handing off, run the pre-handoff gates (references/12): motion, linkage, peaks, argument, readability, EDL, loudness and speech (D1–D3). Fix every FAIL it can.
   - Hand off `rounds/rNN/deliverable/film.mp4` + `film.srt`. Reply to the orchestrator with three things only: `done`, one gate line (`gates: all PASS`, or `gates: FAIL G2, W5` with the unfixed ones), and any requests (§5). No description of the film.
2. **Human review** — when r mod K = 0, or when this cut is a ship candidate (step 5). (A `human.md` can also exist on other rounds when the user commented on the film while answering a request, §5; the reviewer handles every round's `human.md` the same way.)
   - The orchestrator gives the user the path of the rendered cut (and attaches it if the host offers a file tool), says which round it is and that their comments go to the reviewer, and asks for comments, or approval if it is a ship candidate.
   - Save the reply verbatim to `rounds/rNN/human.md` (append, with the time, if the file already holds earlier comments for this round). "No comments" is valid.
   - Do not summarise, rank or answer the comments; route them.
3. **Reviewer reviews** — a fresh subagent (§7). It builds its view with `scripts/review_pack.py`, follows references/19, writes `rounds/rNN/review.md` (`templates/review.md`) and a copy in `review/`. Verdict: **SHIP** (no BLOCKING or MAJOR finding open) or **REVISE**.
4. **Orchestrator routes.** It relays requests (§5), adds the round to `LOOP.md` (round row + one ledger row per finding, from `review.md`), handles stalled findings (§8), tells the user one line (round, verdict, what happens next), and sends the generator only the path of `review.md` (SendMessage to `generator`). Exception: a SHIP review on a non-human round is not sent; the next round is a human round on the same cut (§8), and its review is the one the generator gets.
5. **Stop or continue** (§8).

## 5. Requests to the user (either role)

Either role may need something only the user has: the data behind a plot, a figure's source values, an unpublished number, the authors' intent, a choice between two faithful options.

- A role lists requests at the end of its output (`templates/review.md` has the block; the generator uses the same block in its reply):
  ```
  ## Requests to the user
  - Q02.1 [blocking | non-blocking] What is needed, why (which finding or beat), and what will be done without it.
  ```
- **Generator requests** may be blocking: the generator saves its state to `gen/STATE.md`, ends its turn with the reply `blocked · requests`, and is resumed with SendMessage once the orchestrator has the answer. Non-blocking ones: the generator goes on with what it has and lists them in its normal reply.
- **Reviewer requests** are always non-blocking: the reviewer finishes its review with what it has and marks the dependent findings "pending Q03.1"; a pending finding does not require the generator to act yet. The answer reaches the next reviewer.
- The orchestrator asks the user, saying which role asks and why, and records question and answer verbatim in that role's `exchange/` file. Batch requests from both roles into one message when they arrive together, grouped by role.
- **"There is none" is a valid answer.** Record "unavailable"; the role proceeds with what it has (a typed value marked "approx.", a labelled illustration, a stated omission). Neither role asks the same thing twice: both read their `exchange/` file first.
- **Supplied data** goes to `materials/` with an `INDEX.md` line: file name and what it contains, in the user's words — not who asked or why. Material is source, like the paper; both roles may use it.
- **Keep the channels clean.** If the user's answer to a generator request also comments on the film, do not split or reword it: save the whole reply verbatim to the next round's `human.md` (for the reviewer), and save to `exchange/generator.md` only the sentences that answer the question, copied verbatim. Tell the user in one line that their comments on the film go to the reviewer. A reviewer request that settles a human comment conflicting with the paper stays in `exchange/reviewer.md` and reaches the generator only through the next `review.md`.

## 6. Generator: acting on a review

- **Every BLOCKING, MAJOR and MINOR finding gets one outcome** in `gen/STATE.md`: fixed, or disputed. Nothing is silently skipped. **TASTE** findings may be declined without asking ("declined: taste"), unless tagged `source: human`.
- **Fix** to the finding's "Done when", not its wording: the reviewer describes symptoms, the generator chooses the cure. A fix never breaks a non-negotiable (SKILL.md §2); fidelity outranks reviewer and human taste.
- **Dispute** when a finding contradicts the paper, the brief or a non-negotiable: a request to the user citing the finding id and the evidence (page, table, brief line), with the options. The orchestrator writes the user's decision to `exchange/rulings.md` as id + decision only ("F03.2: keep as is"), never with the generator's argument. Both roles read rulings; the reviewer does not re-open a finding a ruling closed.
- Keep `gen/STATE.md` current (round, findings and outcomes, disputes, decisions), so a new generator can take over if the persistent one is lost.

## 7. Spawning the roles

**Generator** — once, with the Agent tool (`subagent_type: general-purpose`, name `generator`), continued every round with SendMessage. If it cannot be continued, spawn a new one and point it at `gen/STATE.md`.

```
You are the GENERATOR of an explainer film, in the review loop of <skill>/references/18-review-loop.md.
Read §1–§2 and §6 of that file, then what §1 lists for the generator. You are not the
orchestrator: skip every instruction addressed to it, and never ask the user directly;
put questions in a "Requests to the user" block in your reply.
Project: <abs path>. Brief: gen/BRIEF.md. Paper: paper/paper.pdf.
You may open only: gen/, paper/, materials/, rounds/*/review.md, rounds/*/deliverable/,
exchange/generator.md, exchange/rulings.md, deliver/, and <skill>/.
Everything else in the project is off limits (review/, rounds/*/human.md, exchange/reviewer.md, LOOP.md).
Write only under gen/, rounds/<rNN>/deliverable/ and deliver/.
Build round 1 and hand off rounds/r01/deliverable/film.mp4 + film.srt.
Reply with: done · one gate line · requests. Nothing else. If a request blocks you: save gen/STATE.md
and reply: blocked · requests. You will be resumed with the answer.
```
Each later round: `Round <r>: act on rounds/<r−1>/review.md (and exchange/rulings.md, exchange/generator.md if changed); hand off rounds/<rNN>/deliverable/.`

**Reviewer** — a **new** Agent every round (`subagent_type: general-purpose`). **Never `fork`**: a fork inherits the orchestrator's context, which holds everything the reviewer must not know. Never continue an old reviewer with SendMessage; its memory is `review/`. Fill the brackets; add nothing about the film's intent, history or the generator:
```
You are the independent REVIEWER of an explainer film about a research paper.
Read <skill>/references/19-reviewer.md first and follow it.
Project: <abs path>. Round: <rNN>. Human comments this round: <rounds/rNN/human.md, if the file exists | none>. <"This is a human round on the same cut as <rNN−1>", when it is.>
You may open only:
  rounds/<rNN>/deliverable/   the film and its subtitles
  paper/paper.pdf             the paper
  materials/                  data the user supplied
  review/                     your own earlier reviews, NOTES.md, packs
  rounds/*/human.md           the user's comments, this round and earlier ones
  exchange/reviewer.md, exchange/rulings.md
  <skill>/  (references, SKILL.md, templates, scripts)
Everything else in the project is off limits.
Write rounds/<rNN>/review.md from <skill>/templates/review.md, and a copy to review/<rNN>.md.
Reply with: verdict · counts by severity · ids still open from earlier rounds · requests. Nothing else.
```

## 8. Stopping

- **Ship candidate:** the reviewer says SHIP and the generator's gate line is all PASS.
  - If that round was already a human round and the user approved, the loop ends.
  - Otherwise the next round, r+1, is a **human round on the same cut**: the orchestrator copies `rounds/rNN/deliverable/` to `rounds/r(N+1)/deliverable/` (no generator step, and the SHIP review is not sent to the generator), asks the user for approval or comments, and runs a fresh reviewer on it. That reviewer carries forward the earlier review's open MINOR findings. Approval with no comments and a SHIP verdict ends the loop; otherwise its review goes to the generator and the loop continues.
- **The user approves but the reviewer says REVISE:** the orchestrator lists the open BLOCKING and MAJOR finding titles to the user and asks: ship anyway (they go in the report as open items) or continue. BLOCKING scientific findings (TI, invented content) are named as such.
- **A finding open for 3 rounds** (same id, not fixed, not disputed): before routing the review, the orchestrator asks the user to decide it — keep the film as is, require the change, or drop the finding — and records the answer verbatim in `exchange/reviewer.md`. A fresh reviewer then amends `rounds/rNN/review.md` accordingly (closes the finding, or keeps it with the user's decision in its "Why"), and that amended review is what the generator gets. The loop continues.
- **Maximum rounds reached:** show the user the latest cut, the open findings by severity and the options (another K rounds, accept with the open items listed, or change scope). Never continue silently.

After approval:
1. The generator renders the deliverables into `deliver/` (4K60 master, 4K and 1080p MP4, SRT, stems; K6) and the slide figures into `deliver/figures/` (phase 10, K7), and replies with the gate line.
2. **Delivery check:** one more fresh reviewer, with `deliver/` added to its allow-list, writing `deliver/docs/delivery_review.md` (and a copy in `review/`), with the line "Delivery check: report only defects introduced by rendering, assembly or encoding, and figure defects (references/19 §6)." Its findings go to the generator like any review; fix and re-check if there are any.
3. The orchestrator writes `deliver/docs/QA.md` from `LOOP.md` (references/07: one row per finding across all rounds) and the final report (SKILL.md §6), including the loop: rounds, human rounds, findings opened and closed by severity, disputes and rulings, requests and what was unavailable.

## 9. Orchestrator discipline

- Route files, not summaries. Pass paths; never retell a review to the generator or the film's intent to the reviewer.
- Never edit `review.md`, `human.md` or a role's request text.
- Talk to the user in their language; the film's language follows the brief.
- Keep `LOOP.md`: a round table (r, human round y/n, gate line, verdict, BLOCKING/MAJOR/MINOR/TASTE open, requests, rulings) and a findings ledger (id, severity, source, opened, status per round).
- Between rounds, tell the user one line: round r, verdict, what happens next. Track the rounds in the task list.

## 10. Auditing an existing film

The audit mode (SKILL.md phase 9) starts as the reviewer alone: a fresh reviewer on the user's film and the paper, writing `review.md` plus the evidence table of references/08 Pass 1 (it reads the film from `review_pack.py`, since it has no code to instrument). It does not change the film. If the user then wants the corrections made (narration polish, re-voicing, re-render), a generator does them from that review, and a fresh reviewer runs Pass 2 on the new render.
