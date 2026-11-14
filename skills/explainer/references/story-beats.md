# Story beats

Every explainer is four beats. Write them as four lines before any code.

| Beat | Job | Shape on the page |
|---|---|---|
| Hook | A question the reader cannot answer yet, and wants to | `h1.hook`, big type, one sentence ending in `?` |
| Setup | One or two frames of what the reader already knows | short prose, or the first 1 to 2 steps of the scene |
| Mechanism | How it works, one true statement per step | the scene: 5 to 15 steps, plus the reader action |
| Payoff | One sentence that answers the hook | `p.payoff` with one `<mark>`ed phrase |

## Hooks that work

- A contradiction the reader has seen: "Same model, different tool, different result. Why?"
- A number that sounds wrong: "A thousand requests arrive at once. Why do only ten fail?"
- A choice: "Your agent wants to run `rm -rf build/`. Do you let it?"

Avoid hooks that need a term the reader does not know yet. Avoid hooks that are a topic ("Understanding caches") or a promise ("Learn how X works").

## Mechanism steps

- Each step changes something visible. The first step of the scene is already a picture.
- Each caption says what is **true now**: "The worker holds r5. Three requests wait." Not "the worker moves".
- One new fact per step. If a caption needs "and then", split the step.
- Name the wrong idea the reader came in with, and let one step break it.
- Put the reader action where the reader has just enough to decide, usually after the middle.
  Mark that step `wait: true` so Play stops there.
- After the action, show the consequence of *their* choice (`api.branch`) before the payoff.

## Payoff

One sentence, under 20 words, that the reader could repeat to a colleague. It answers the hook directly.
Below it, at most two sentences on where this matters in practice, and a Sources list for current tech.

## Length

A good explainer reads in 3 to 6 minutes: 150 to 400 words of prose outside the scene, one scene (a deck of
3 to 7 sections), 10 to 25 steps in total.
