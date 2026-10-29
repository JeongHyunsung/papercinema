# 17. Story arc and the persistent visual spine

Learned from a later revision of the skill, with the B-Flex film (`examples/bflex`) as the storytelling benchmark.

## The arc (about 2 min)

| Share | Beat | Rule |
|---|---|---|
| 0–18 % | Hook | Show the problem without jargon. Cost first (what one instance costs), then repetition (why it repeats), then scale (one number). Peak 1 lands on the scale number. |
| 18–24 % | Question → title | One spoken question that the method answers, then the name and its one-line idea as the answer. Hold for ≥ 3 s. |
| 24–75 % | One mechanism | Every step acts on the spine: the concept it operates on, then each operation in turn and why it is safe (the rule, and the paper's evidence that the rule is sound), then what remains. Honesty about what the method does not decide belongs here. |
| 75–92 % | Climax | Fair doubt → controlled test → **one hero number** (number_land, accent signature), alone, with metric, scope, spread and what was held fixed. Then the baselines as secondary bars with an explicit trade-off line (where a baseline is better, say so, with the count of settings). |
| 92–100 % | Reprise | Return to the spine reduced to what the method kept; the title again; hold ≥ 3 s. |

## The persistent spine

- Generate the spine's identities once, deterministically, in its own module, with a fixed RNG seed. Every membership set (candidate, expanded, pruned by rule X, kept, evaluated) is computed from those identities, never redrawn per scene. In B-Flex the spine is the candidate state-machine space: each candidate keeps its position from the hook to the reprise, and the pruning rules recolour members in place.
- Use one camera (`kfv` keys on yaw, pitch, f, cx, cy, target). The detail scenes move it to a corner mini-map, a side panel, or full frame, and the spine never disappears or re-randomises.
- Colour hierarchy, used everywhere it appears, one colour per role the method defines, for example:
  - gray: candidate
  - teal: kept by the method
  - muted red: pruned (with the rule named)
  - blue: evaluated / final
- A legend appears only in the beat where all roles coexist.
- Weak perspective (a far camera with a long lens) avoids radial streaks in dot clouds. Scale the dot radius by zoom, and lighten crowded zoomed-out views.
- Operations act on the units the paper defines (a candidate, a branch of the search tree, a group), never on arbitrary geometric neighbourhoods of dots. A step that does not move between candidates is shown as a curve or bars, not as dots sliding to their neighbours.
- Any illustrative count drawn on the spine says so in a footnote ("illustration"). The real numbers are stated in text (the paper's budgets and counts).

## Checks that bit in earlier cuts

- Peak reveals must be sharp. Change the spine within about 0.1 s of the reveal frame, not as a 0.3 s cascade (W2 ≥ 4 % of the frame). Keep the setup drifting so G2 does not see a static run.
- Text that anticipates the reveal can appear at the start of its sentence. It still needs ≥ 2.5 s readable before the next scene (B1).
- A trade-off line belongs under the bar it qualifies and appears when that bar lands, not when the narrator reaches "though".
