# Demo video

Rules: 6 minutes or less, YouTube or Vimeo, public or unlisted, and it must show the project **working** (not only slides).
The same video also serves the Presentation criterion: problem, solution, next steps.

Record a first take early. Record the shots after the last UI change, not before.

Budget: the narration below is 772 words, which is 5 minutes 20 at a normal speaking pace, and the shot list adds
up to 5:25. That leaves about half a minute under the 6:00 limit for the app to respond on screen. Do not speed up
to fit; cut a sentence instead.

## Before you record
1. Open the live app: https://stem2connect-2026-cjfcmxcaxddeqtfvyvjzbw.streamlit.app/
   Open it once a few minutes early, so it is awake and not showing the waking-up screen.
2. Set the browser to full screen and zoom to about 110%, so the tables are readable in a 1080p recording.
3. Have these three things ready to paste, one per shot:
   - the Activity tab's own **Example** button (no typing needed)
   - caffeine: `CN1C=NC2=C1C(=O)N(C)C(=O)N2C`
   - the Cell lines tab's own **Example** button (fills KRAS, TP53, STK11)
4. Record screen and voice together in one pass. If you fluff a line, pause, breathe, and say the line again;
   cut the bad take out afterwards.
5. No music. Nothing copyrighted on screen: close other tabs, hide bookmarks.

## Script

Each heading is one shot. The time is where that shot should end.

### 1. The problem (ends 0:45) — on screen: the app's front page, Activity tab

> To find out whether a molecule might act on a cancer protein, you normally need commercial screening software
> or a specialist pipeline. As a student I have neither. The data itself is public: ChEMBL holds millions of lab
> measurements, DepMap and PRISM hold cancer cell lines screened against drugs, Tox21 holds safety assays.
> Getting the data is not the hard part. Using it honestly is. A model tested on molecules that resemble its
> training set always looks better than it is, and most free tools show one confident number and hide how
> uncertain it is. So I built a workbench that answers three questions and shows its evidence and its limits
> every time.

### 2. What it is (ends 1:10) — slowly scroll the three tabs, then back to Activity

> This is the Molecule Screening Workbench. It runs in a browser, it is free, and everything behind it is public
> data. Three tabs, three questions. Is this molecule likely active on a cancer target? Which screened cancer cell
> lines carry a set of mutations, and how did they respond to drugs? Does this molecule resemble compounds that
> were active in lab safety assays? This is lab data on proteins and cell lines. Not patients, not medical advice,
> and it does not discover drugs.

### 3. Activity (ends 2:00) — pick CDK6, click Example, open the first expander

> Here is the first question. CDK6 is a protein that drives cell division in several cancers. I click Example and
> it scores three known inhibitors. But the score is not the interesting part. Underneath each molecule it draws
> the three most similar molecules it learned from, with their measured activity from ChEMBL and how similar they
> are. That is the evidence, so you can see why it answered the way it did. And in the sidebar: the held-out
> score for this target with a confidence interval, and the simple baseline it had to beat.

### 4. The abstain (ends 2:45) — clear the box, paste caffeine, open the expander

> Now the part I care about most. This is caffeine. It is not a kinase inhibitor, and the model has never seen
> anything like it. A plain classifier would hand you a confident number here anyway, and it would be meaningless.
> This one refuses. It says: outside what this model has seen, maximum similarity zero point one five against a
> cut-off of zero point seven one, no prediction shown. The probability column is left empty and abstain is
> ticked. I wrote that rule before I trained anything.

Do not say the hidden score out loud. The model does produce one for caffeine, but the app never shows it, and a
number that is not on screen is a claim the viewer cannot check.

### 5. Cell lines (ends 3:25) — Cell lines tab, Example, pick NCI-H1573, scroll the drug table

> Second question. Three mutated genes: KRAS, TP53 and STK11. It finds the screened cancer cell lines sharing the
> most of those hotspot mutations. This lung line shares all three. Pick it, and you see how that line actually
> responded to two hundred and two drugs in the PRISM screen, most sensitive first, with structures. These are
> measurements, not predictions. It is a lookup, and the app says so.

### 6. Safety flags (ends 3:55) — Safety flags tab, Example, open the first expander

> Third question. Twelve Tox21 assays. For each one it shows the score next to how often molecules are really
> active in that assay, and how well the model ranked held-out molecules. A score above the assay's own rate gets
> marked. There is no toxicity verdict here, because these models are not good enough to give one, and the screen
> says that.

### 7. The honest part (ends 4:40) — Cell lines tab, scroll to the greyed-out model ranks

> This is the part I am most pleased with. I wrote the evaluation rules down before training anything: scaffold
> splits, so test molecules share no core structure with training ones; leave-lineage-out splits for cell lines;
> baselines and confidence intervals throughout. Then I kept the answers I did not like. The drug response models,
> on this tab, barely beat a coin flip: a median score of zero point five five, and a hundred and seventy-one of
> two hundred and two are statistically weak. So the tab leads with the measured data and greys the weak model
> ranks out. A negative result is still a result, and hiding it would have made the tool a liar.

### 8. Learning, AI, next (ends 5:25) — back to the front page

> Three things I learned. A high score can come from the data rather than the model: most molecules in these
> ChEMBL sets are active, so even a random ranking looks good on some metrics. Licences matter: my first
> cell-line source turned out to forbid this exact use, so I moved to one that allows it. And a README written
> inside your own project forgets to tell anyone to clone it, which only a fresh clone revealed.
> The app uses classic machine learning trained here on public data. No language model runs inside it. I built it
> with Claude Code, which wrote code and tests from my briefs, and a reviewer agent found reporting problems that
> changed my evaluation protocol. Every decision was mine, and they are all listed in the plan.
> Next is analog enumeration: take an active molecule, make small edits, and score them through this same
> pipeline. Thanks for watching.

## Shot list
| # | What is on screen | What is said | Length | Recorded? |
|---|---|---|---|---|
| 1 | Front page, Activity tab | The problem | 0:45 | [ ] |
| 2 | Scroll across the three tabs | What it is, and what it is not | 0:25 | [ ] |
| 3 | CDK6, Example, first expander open | Scores, then the drawn evidence | 0:50 | [ ] |
| 4 | Paste caffeine, expander open | It abstains, and why | 0:45 | [ ] |
| 5 | Cell lines, Example, NCI-H1573, drug table | Lookup, measured responses | 0:40 | [ ] |
| 6 | Safety flags, Example, expander open | Score against the assay's own rate | 0:30 | [ ] |
| 7 | Cell lines, greyed model ranks | The negative result, kept on purpose | 0:45 | [ ] |
| 8 | Front page | Learning, AI disclosure, next step | 0:45 | [ ] |

Total 5:25. The 6:00 limit leaves 35 seconds of slack for the app to load between clicks.

## Numbers said out loud, and where they come from
Say these only if the screen shows them in the same shot.
| Said | Source |
|---|---|
| CDK6 held-out ROC-AUC 0.894, 95% CI 0.784 to 0.980 | `results/activity_models.md`, shown in the sidebar |
| caffeine: max similarity 0.15, cut-off 0.71 | the app's own warning line, checked 2026-11-05 |
| 202 drugs in the PRISM screen | `results/loop2_models.md` |
| drug models: median ROC-AUC 0.546, 171 of 202 weak | `results/loop2_models.md` |
| 12 Tox21 assays | `results/tox21_models.md` |

## Upload checklist
- [ ] Under 6:00
- [ ] Shows the project working
- [ ] No copyrighted music
- [ ] Visibility is public or unlisted, link opens when signed out
- [ ] Link pasted into the Devpost form
- [ ] Link pasted into `docs/submission.md` and the README
