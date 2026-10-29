# B-Flex V5: complete narration transcript

Film runtime 119.1 s. Voice: Kokoro-82M `af_heart`, the same as V4. Times are on the V5 film clock.
Lines marked ✎ were revised in V5; see `V5_LANGUAGE_LOG.md`.

| # | in | out | narration | |
|---|---|---|---|---|
| L01 | 0:00.45 | 0:05.01 | A flip-flop has one job: on a rising clock, capture D and hold it. |  |
| L02 | 0:05.46 | 0:09.41 | This one, from the earlier tool SeGen, passes its test vector. |  |
| L03 | 0:09.93 | 0:14.20 | Change one transition, and it outputs zero where it must output one. |  |
| L04 | 0:15.04 | 0:22.79 | A flip-flop can be modeled as a state machine. With three state bits, candidate tables exceed ten to the nineteenth. | ✎ |
| L05 | 0:23.73 | 0:25.04 | Beyond brute force. |  |
| L06 | 0:25.60 | 0:27.94 | B-Flex starts from behavior instead. |  |
| L07 | 0:29.07 | 0:34.18 | Its reference behavior graph covers every input order a D flip-flop must handle. | ✎ |
| L08 | 0:34.55 | 0:41.88 | The failing sequence is one path through it, and the graph requires Q to stay at one, where SeGen-20 gave zero. | ✎ |
| L09 | 0:42.40 | 0:48.58 | Candidates grow one stable transition at a time, and each must match an edge of the reference graph. | ✎ |
| L10 | 0:51.55 | 0:59.03 | Here the clock falls, so Q must stay at zero. Two candidate states would output one, so those branches are pruned. | ✎ |
| L11 | 1:02.65 | 1:11.06 | Deeper in, a settling path needs a table entry that an earlier transition set differently. That entry conflict prunes the branch. | ✎ |
| L12 | 1:11.45 | 1:16.20 | Pruning early makes the two-bit search 20,000 times faster than brute force. |  |
| L13 | 1:16.68 | 1:25.43 | At three state bits, B-Flex finds all 568 million valid state machines in its search space, in about thirteen minutes. | ✎ |
| L14 | 1:25.74 | 1:32.12 | Twenty of the 468 simplest were sampled and turned into transistor-level schematics. | ✎ |
| L15 | 1:32.62 | 1:39.64 | One of them is FF1. When the clock rises, its state settles in two steps, and Q flips on the first. | ✎ |
| L16 | 1:40.07 | 1:48.91 | In SPICE, at 0.9 volts, its sequencing overhead is 2.53 times lower than a transmission-gate flip-flop's, |  |
| L17 | 1:49.44 | 1:50.90 | at a higher energy cost. |  |
| L18 | 1:53.75 | 1:58.25 | B-Flex: a broader flip-flop design space, searched exhaustively. |  |

Word-level timings are in `src/out/audio_v4/placement.json`; subtitles are in `BFlex_DAC2026_film_v5.en.srt`.
