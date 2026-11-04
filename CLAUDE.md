# STEM2Connect AI Hackathon 2026: rules for Claude

An online student hackathon on Devpost. Submission deadline: **Nov 21, 2026, 11:59 PM EST**. The owner is Prakhar.
What gets built, and the plan for it, are his decisions. Do not invent a project or a plan.

## Read first, every session
1. `PLAN.md`: his plan, decisions and what is next. If it is empty, plan with him before writing code.
2. `docs/hackathon.md`: the rules, dates and judging criteria (read from Devpost). The Rules page wins if they differ.
3. If `CLAUDE.local.md` exists, follow it. It points to his notes vault, where everything done here is also recorded.

## Working with him
- He plans with you. Suggest options, ask one question at a time, and do not decide for him.
- After each task, say in plain words what you built, how to run it, and how to tell it worked. Keep it short.

## Hard rules
- The project must be a **working solution that can be shown**, not a deck or mockup.
- **New work only.** Everything must be created between Oct 11 and Nov 21, 2026. Before reusing any code, data or
  design from an earlier project (including his other hackathon work), check its date and tell him. Disclose all
  reused work in the README under "Credits and reused work".
- **Disclose AI.** The README and the Devpost description say which AI tools were used and what they contributed.
- **Credit** every library, dataset and API in the README.
- Do not collect personal data from users without consent. No harmful, offensive or misleading content.
- Never claim what the project does not do. Every number in the README, the write-up and the video traces to a
  source file or a run, and says how it was computed.
- No secrets in git (API keys, tokens, `.env`). Never print them.
- The repo is **private for now and must be made public before the submission**. Check it is public, and that a
  fresh clone runs from the README, before the last day.
- The demo video is 6 minutes or less, on YouTube or Vimeo (public or unlisted), and shows the project working.
- Run the tests and the linter before saying a task is done.

## Git
Branch per topic (`area/topic`), small commits, message style `area: what changed`. Do not force-push.

## Recording everything
Everything done here also goes in the owner's notes vault (see `CLAUDE.local.md`). Run
`python scripts/sync_to_vault.py` after each finished task to refresh the vault copy of this project, and write
decision, lesson and concept notes there as you learn things.
