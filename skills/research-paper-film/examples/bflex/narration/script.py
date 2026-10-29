"""B-Flex film v5: narration script (single source of truth).

Each line is synthesized separately, so pauses between lines are edited
silence and speech is never time-stretched.
  sub   : subtitle / on-record text (what the narrator says, in print form)
  tts   : the same words, spelled for the TTS front end (see PRONUNCIATION)
  gap   : silence after the line, in seconds (edit decision, may be retuned)
"""

LINES = [
    # Act I: the challenge
    dict(id="L01", sub="A flip-flop has one job: on a rising clock, capture D and hold it.",
         tts="A flip-flop has one job: on a rising clock, capture dee, and hold it.", gap=.5),
    dict(id="L02", sub="This one, from the earlier tool SeGen, passes its test vector.",
         tts="This one, from the earlier tool See-Jen, passes its test vector.", gap=.4),
    dict(id="L03", sub="Change one transition, and it outputs zero where it must output one.",
         tts="Change one transition, and it outputs zero, where it must output one.", gap=.8),
    dict(id="L04", sub="A flip-flop can be modeled as a state machine. With three state bits, candidate tables exceed ten to the nineteenth.",
         tts="A flip-flop can be modeled as a state machine. With three state bits, candidate tables exceed ten to the nineteenth.", gap=.35),
    dict(id="L05", sub="Beyond brute force.",
         tts="Beyond brute force.", gap=.9),
    # Act II: the idea
    dict(id="L06", sub="B-Flex starts from behavior instead.",
         tts="Bee-Flex starts from behavior, instead.", gap=.6),
    dict(id="L07", sub="Its reference behavior graph covers every input order a D flip-flop must handle.",
         tts="Its reference behavior graph covers every input order a dee flip-flop must handle.", gap=.55),
    dict(id="L08", sub="The failing sequence is one path through it, and the graph requires Q to stay at one, where SeGen-20 gave zero.",
         tts="The failing sequence is one path through it. And the graph requires queue to stay at one, where See-Jen twenty gave zero.", gap=.8),
    # Act III: inside the algorithm
    dict(id="L09", sub="Candidates grow one stable transition at a time, and each must match an edge of the reference graph.",
         tts="Candidates grow one stable transition at a time, and each must match an edge of the reference graph.", gap=.6),
    dict(id="L10", sub="Here the clock falls, so Q must stay at zero. Two candidate states would output one, so those branches are pruned.",
         tts="Here, the clock falls, so queue must stay at zero. Two candidate states would output one, so those branches are pruned.", gap=.7),
    dict(id="L11", sub="Deeper in, a settling path needs a table entry that an earlier transition set differently. That entry conflict prunes the branch.",
         tts="Deeper in, a settling path needs a table entry that an earlier transition set differently. That entry conflict prunes the branch.", gap=.8),
    dict(id="L12", sub="Pruning early makes the two-bit search 20,000 times faster than brute force.",
         tts="Pruning early makes the two-bit search twenty thousand times faster than brute force.", gap=.7),
    # Act IV: impact
    dict(id="L13", sub="At three state bits, B-Flex finds all 568 million valid state machines in its search space, in about thirteen minutes.",
         tts="At three state bits, Bee-Flex finds all five hundred sixty-eight million valid state machines in its search space, in about thirteen minutes.", gap=1.1),
    dict(id="L14", sub="Twenty of the 468 simplest were sampled and turned into transistor-level schematics.",
         tts="Twenty of the four hundred sixty-eight simplest were sampled and turned into transistor-level schematics.", gap=.6),
    dict(id="L15", sub="One of them is FF1. When the clock rises, its state settles in two steps, and Q flips on the first.",
         tts="One of them is F F one. When the clock rises, its state settles in two steps, and queue flips on the first.", gap=.7),
    dict(id="L16", sub="In SPICE, at 0.9 volts, its sequencing overhead is 2.53 times lower than a transmission-gate flip-flop's,",
         tts="In spice, at zero point nine volts, its sequencing overhead is two point five three times lower than a transmission-gate flip-flop's,", gap=.25),
    dict(id="L17", sub="at a higher energy cost.",
         tts="at a higher energy cost.", gap=1.0),
    # Act V
    dict(id="L18", sub="B-Flex: a broader flip-flop design space, searched exhaustively.",
         tts="Bee-Flex. A broader flip-flop design space, searched exhaustively.", gap=0),
]

PRONUNCIATION = [
    # term, say it as, IPA (General American), TTS spelling used, note
    ("B-Flex", "BEE-flex", "ˈbiː.flɛks", "Bee-Flex", "Letter B + 'flex'; stress on BEE."),
    ("SeGen", "SEE-jen", "ˈsiː.dʒɛn", "See-Jen", "Prior work [10]. Pronunciation not stated by its authors; confirm."),
    ("SeGen-20", "SEE-jen TWEN-tee", "ˈsiː.dʒɛn ˈtwɛn.ti", "See-Jen twenty", "The 20th FF of SeGen [10]; spoken in L08 so the failure is never attributed to SeGen as a whole."),
    ("FSM / AFSM", "eff-ess-EM", "ˌɛf.ɛsˈɛm", "(not spoken)", "Narration says 'state machine'; on screen 'FSM'."),
    ("RBG", "ar-bee-GEE", "ˌɑɹ.biːˈdʒiː", "(not spoken)", "Narration says 'reference behavior graph'."),
    ("ESTG", "ee-ess-tee-GEE", "ˌiː.ɛs.tiːˈdʒiː", "(not spoken)", "Extended State Transition Graph. On screen as 'Candidate ESTG'. Never 'ESG'."),
    ("D flip-flop", "DEE FLIP-flop", "ˈdiː ˈflɪp.flɑp", "dee flip-flop", "'D' is the data pin; spell 'dee' so it is never read as a grade."),
    ("Q", "KYOO", "kjuː", "queue", "Output pin. Spelled 'queue' to force /kjuː/: in the casting take a bare 'Q' was transcribed by ASR as 'quee'."),
    ("FF1", "eff-eff ONE", "ˌɛf.ɛf ˈwʌn", "F F one", "Never 'ff-one' or 'fortissimo'."),
    ("SPICE", "SPYSS", "spaɪs", "spice", "Circuit simulator; read as a word."),
    ("TGFF / transmission-gate flip-flop", "trans-MISH-un gate FLIP-flop", "tɹænzˈmɪʃ.ən ɡeɪt", "transmission-gate flip-flop", "Spoken in full."),
    ("behavioral equivalence", "bih-HAY-vyer-ul ih-KWIV-uh-lunss", "bɪˈheɪ.vjɚ.əl ɪˈkwɪv.ə.ləns", "(not spoken)", "Narration says 'behavior'."),
    ("metastability", "MET-uh-stuh-BIL-ih-tee", "ˌmɛt.ə.stəˈbɪl.ɪ.ti", "(not spoken)", "On screen in the scatter footnote only."),
    ("2.53×", "two point five three times", "", "two point five three times", "Always about sequencing overhead (T_setup + T_CK→Q), never CK-to-Q delay alone."),
    ("0.9 V", "zero point nine volts", "", "zero point nine volts", ""),
    ("568,832,054", "five hundred sixty-eight million", "", "", "Rounded in speech; exact on screen."),
    ("δ (delta)", "DEL-tuh", "ˈdɛl.tə", "(not spoken)", "Next-state (transition) function; narration says 'table entry'."),
    ("transistor-level schematics", "tran-ZIS-ter LEV-ul skee-MAT-iks", "tɹænˈzɪs.tɚ ˈlɛv.əl skiˈmæt.ɪks", "transistor-level schematics", "Paper §4.2 wording; not 'fabricated circuits'."),
]

if __name__ == "__main__":
    import re
    words = sum(len(re.findall(r"[A-Za-z0-9.,'-]+", l["sub"])) for l in LINES)
    print("lines", len(LINES), "words", words)
