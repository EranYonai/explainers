# explainers

A skill for Claude Code and Pi that turns a topic into an interactive HTML explainer you can share as a link.

You ask "make an explainer of how git bisect finds a bad commit", or of a PR, an incident or an onboarding
topic. The agent asks a few short questions, then writes one self-contained page: prose, step-through scenes
(Back / Next / Play), captions that carry the teaching, and something the reader controls, like picking an
input, dragging a slider or approving a step.

Explainers are **silent by design**: captions, motion and drawings do the explaining, so they work on a
phone, in a PR description, and later as a short video without a voice.

> Status: early. The repo is being scaffolded. The skill's workflow, shared player and self-check land next.

## Install

Claude Code:

```bash
/plugin marketplace add EranYonai/explainers
/plugin install explainers@explainers
```

Pi:

```bash
pi install git:github.com/EranYonai/explainers
```

## Examples

The five drafts that shaped the format, each one self-contained HTML (open in a browser):

| Explainer | What the reader does |
|---|---|
| [How an explainer gets made](examples/how-an-explainer-gets-made/index.html) | Picks the bad commit; a real binary search builds the steps |
| [Hash tables and collisions](examples/hash-table/index.html) | Steps through hashing, chaining, resizing and probing |
| [Why a flaky test lies](examples/flaky-test/index.html) | Drags timing sliders over 200 seeded runs |
| [What is an AI coding harness?](examples/ai-harness/index.html) | Plays the harness and approves a tool call |
| [LangChain and LangGraph, explained](examples/langgraph/index.html) | Chooses the route at a graph junction |

## Principles

1. **Content first, engine second, platform last.** Each layer is pulled out of real use of the one before.
2. **The agent interviews before it draws.** Short, and skippable for day-to-day asks.
3. **Scenes describe states, not animations.** Each step says what is true; the player animates the change.
4. **Numbers come from code.** Every number on screen is computed by a function in the page, never typed by hand.
5. **Random things are seeded,** so captions can quote results and a video renders the same every time.
6. **Cheap to make.** Every run is logged in [`runs.csv`](runs.csv). Targets for v0: under 60K tokens, at most
   10 tool calls, under 5 minutes, at most 1 fix pass.

## Layout

```
skills/explainer/      the skill: SKILL.md, references, player template, themes, check script
examples/              finished explainers
docs/themes/           gallery of 25 themes and the generator (3 ship with the skill)
docs/findings/         field notes from the first drafts
runs.csv               cost of every explainer made with the skill
```

## License

[Apache-2.0](LICENSE)
