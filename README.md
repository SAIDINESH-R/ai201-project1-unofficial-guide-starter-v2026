# The Unofficial Guide

Saidinesh R — advice_threads corpus.



---

# Unit 1

## What This Does

This system answers questions about campus advice threads — short Q&A-style
discussions where students ask things like "is a bike worth it?" or "how do
meal plan tiers work?" and others reply with tips, often disagreeing with each
other. It answers specific factual questions (deadlines, costs, policies) by
retrieving the most relevant reply from these threads and citing which thread
it came from.

## Chunking Strategy

**Chunk size:**
**Overlap:**

**Chunk size:** variable — one reply per chunk (merged forward if under 100 characters)
**Overlap:** none

Each document is a Q&A thread with multiple replies separated by
"--- reply N (votes) ---" markers. The starter's fixed 800-character chunker
barely split anything (23 documents became 26 chunks) and produced a
2-character fragment from a document that didn't divide evenly at the
800-character mark — clearly unusable.

I switched to splitting on reply boundaries instead, since each reply in
these threads is usually a self-contained answer to a sub-question. I
prepended the thread's original question to every chunk so it stays readable
on its own. Replies shorter than 100 characters get merged into the next
reply rather than kept as tiny fragments. This produced 75 chunks averaging
174 characters, with a shortest chunk of 104 characters — no more unusable
fragments.

## Sample Chunks

======================================================================
Chunk 1  |  source: thread_bike_commute.txt#0  |  produced by: chunker.py::split_documents
======================================================================
THREAD: Is a bike worth it for a 20 minute walk commute?
Yeah. Cuts an 18 minute walk to about 6. The thing nobody mentions is storage — covered bike parking exists at three buildings and is full by 9am at all three.

======================================================================
Chunk 2  |  source: thread_first_gen.txt#1  |  produced by: chunker.py::split_documents
======================================================================
THREAD: Anything specific for first-generation students?
The thing I'd say: the unwritten rules are the hard part, not the coursework. Ask about the unwritten rules explicitly. People are happy to explain them and nobody volunteers them.

======================================================================
Chunk 3  |  source: thread_laptop_specs.txt#2  |  produced by: chunker.py::split_documents
======================================================================
THREAD: How much laptop do I actually need for CS courses?
I did two years on an 8GB machine and it was fine until the last project, at which point it very much wasn't. 16 is the answer.

======================================================================
Chunk 4  |  source: thread_parking.txt#1  |  produced by: chunker.py::split_documents
======================================================================
THREAD: Worth getting a parking permit?
Street parking on Verrill is legal and free and unmarked, which is why half the upper years do it.

======================================================================
Chunk 5  |  source: thread_sleep_schedule.txt#1  |  produced by: chunker.py::split_documents
======================================================================
THREAD: Everyone says fix your sleep. Does it actually matter?
The library being open until 2am is a trap. It's a resource, not a schedule.

```
```

## Sample Answer

Question: How many times can I change my meal plan tier?

Answer: You can only change your meal plan tier once.
Source: thread_meal_plan_tier.txt

Retrieval details: best distance 0.158, cutoff 0.6, sources retrieved:
thread_meal_plan_tier.txt, thread_pass_fail.txt

```
```

**My relevance cutoff:** 0.6 (kept the starter's default)


I didn't have time this unit to run the full 5 in-scope / 5 out-of-scope
comparison to tune this further. One real query I ran came back with a best
distance of 0.158, well under the 0.6 cutoff, suggesting the default is
reasonable for this corpus, but this needs more testing.

| Question | In corpus? | Best distance |
|---|---|---|
| How many times can I change my meal plan tier? | Yes | 0.158 |
|  |  |  |

## How I Used AI

<!-- Two specific moments. For each: what you asked for, what came back, and
     what you changed about it.

     "I asked Claude to write the chunking function from my notes. It ignored
     the overlap, so I added that myself" is the level of detail we're after.
     "I used AI to help me code" is not.

     Milestone 5. -->

**1.**
I asked Claude to help write the chunking function in chunker.py,
since I was short on time and hadn't worked with regex before. It suggested
splitting on the "--- reply ---" markers and merging short replies forward
so nothing stayed under 100 characters. I ran it, checked the output (shortest
chunk went from 2 characters to 104), and kept it as given since it matched
what I'd noticed in Milestone 1 about replies being self-contained.

**2.**
I used Claude to sanity-check my acceptance criteria wording — I
described what I wanted (a minimum chunk length, and votes mattering for
ranking) and it helped me phrase them as testable sentences with numbers.
<!-- ── Stretch features ─────────────────────────────────────────────────────
     Doing one? Say so here BEFORE you start. A feature this README never
     claims earns nothing.
     ───────────────────────────────────────────────────────────────────────── -->

---

# Unit 2

<!-- These sections get ADDED to what's already above. Don't delete or rewrite
     unit 1 — the point is that someone can see what you said before you knew
     how it went. -->

## Run Log — Before

<!-- Your five criteria, three runs each. `python run_eval.py --label before`
     runs the questions, puts the OUT_OF_SCOPE ones through the gate, and
     writes it all into results/ for you. Targets come from criteria.md; the
     verdict column is your call.

     Criterion 3 is measured in one deterministic pass rather than three, so
     the same number goes in all three run columns. That's correct, not lazy.

     Milestone 1. -->

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Retrieved chunk contains the answer | 4 of 5 |  |  |  |  |
| 2. Every answer names a source | 5 of 5 |  |  |  |  |
| 3. Gate stops out-of-corpus questions | 4 of 5 |  |  |  |  |
| 4. | | | | | |
| 5. | | | | | |

<!-- Underneath, paste the REAL output for each criterion from one of your
     runs — the actual text your system produced, not a description of it.
     Name the file and function that produced it. -->

## Verdicts

<!-- MET or MISSED for each of the five, against the target you wrote last
     unit — not a new one. Plus a sentence on how you decided. That sentence
     matters most where it was close.

     If your target said 4 of 5 and your runs came out 4, 3, 4, that's a MISS.
     The target has to hold, not show up occasionally.

     Milestone 2. -->

| # | Criterion | Verdict | How I decided |
|---|---|---|---|
| 1 |  |  |  |
| 2 |  |  |  |
| 3 |  |  |  |
| 4 |  |  |  |
| 5 |  |  |  |

## Diagnoses

<!-- For each miss: which stage caused it, and how. The stage alone isn't
     enough — you need the mechanism.

     Not a diagnosis: "Question 3 didn't work."
     A diagnosis:     "Question 3 asks about laundry costs. The answer is in
                       one sentence that got split across two chunks, so
                       neither chunk on its own contains it."

     The five stages: loading → chunking → embedding → retrieval → generation.

     Look for a pattern. If three misses all ask about numbers, that's one
     problem, not three.

     Missed nothing? Say so, then say honestly whether your targets were set
     low, and which one you'd tighten and to what.

     Milestone 3. -->

## The Improvement

**What I changed:**

**Why I picked it:**

<!-- Connect it to a specific diagnosis above in one sentence. If you can't,
     you picked a fix because it sounded impressive. -->

### Run Log — After

<!-- Same format, same five criteria, three runs each.
     `python run_eval.py --label after` -->

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Retrieved chunk contains the answer | 4 of 5 |  |  |  |  |
| 2. Every answer names a source | 5 of 5 |  |  |  |  |
| 3. Gate stops out-of-corpus questions | 4 of 5 |  |  |  |  |
| 4. | | | | | |
| 5. | | | | | |

**Did it help?**

<!-- Say plainly whether it did, and how you know. If it made things worse,
     say that — a change that backfired, honestly reported, earns full credit
     and is more interesting than one that worked. What matters is that you can
     tell.

     Milestone 4. -->

## What's Still Broken

<!-- For each criterion still missed after your fix: what you'd do about it,
     and why you stopped where you did.

     "I ran out of time" is fine if it's true. Pretending nothing is left is
     not.

     Milestone 5. -->

## What I'd Do Differently

<!-- Knowing what you know now — which of your five criteria would you write
     differently, and why?

     Milestone 5. -->
