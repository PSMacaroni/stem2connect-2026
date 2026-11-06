# Demo video

Rules: 6 minutes or less, YouTube or Vimeo, public or unlisted, and it must show the project **working** (not only slides).
The same video also serves the Presentation criterion: problem, solution, next steps.

Record a first take early. Record the shots after the last UI change, not before.

Budget: the narration below is 797 words, which is 5 minutes 30 at a normal speaking pace, and the shot list adds
up to 5:35. That leaves 25 seconds under the 6:00 limit for the app to respond on screen. Do not speed up to fit.
If a take runs long, cut the sentence marked **(cut first)** in shot 1, then the last sentence of shot 8.

## Before you record
1. Open the live app: https://stem2connect-2026-cjfcmxcaxddeqtfvyvjzbw.streamlit.app/
   Open it once a few minutes early, so it is awake and not showing the waking-up screen.
2. Set the browser to full screen and zoom to about 110%, so the tables are readable in a 1080p recording.
3. Leave the target on **CDK6** for the whole recording. Shots 3, 4 and 7 all depend on it.
4. Have these ready, one per shot:
   - the Activity tab's own **Example** button (no typing needed)
   - caffeine: `CN1C=NC2=C1C(=O)N(C)C(=O)N2C`
   - the Cell lines tab's own **Example** button (fills KRAS, TP53, STK11)
   - the Analogs tab's own **Example** button (fills the most potent known CDK6 active)
5. Record screen and voice together in one pass. If you fluff a line, pause, breathe, and say the line again;
   cut the bad take out afterwards.
6. No music. Nothing copyrighted on screen: close other tabs, hide bookmarks.

## Script

Each heading is one shot. The time is where that shot should end.

### 1. The problem (ends 0:35) — on screen: the app's front page, Activity tab

> To find out whether a molecule might act on a cancer protein you normally need commercial screening software or
> a specialist pipeline. As a student I have neither. The data itself is public: ChEMBL, DepMap, PRISM and Tox21
> all publish their measurements. Getting the data is not the hard part. Using it honestly is. **(cut first)** Most
> free tools show one confident number and hide how uncertain it is. So I built a workbench that answers four
> questions and shows its evidence and its limits every time.

### 2. What it is (ends 1:10) — slowly scroll the four tabs, then back to Activity

> This is the Molecule Screening Workbench: a browser app, free, built only on public data. Four tabs, four
> questions. Is this molecule active on a cancer target? Which screened cell lines carry a set of mutations, and
> how did they respond to drugs? Does it look like something that was active in a safety assay? And what does one
> atom's change do to the score? This is lab data, not patients. Not medical advice, and it does not discover
> drugs.

### 3. Activity (ends 1:45) — CDK6, click Example, open the first expander

> First question. CDK6 drives cell division in several cancers. I click Example and it scores three known
> inhibitors. The score is not the interesting part. Underneath each molecule it draws the three most similar
> molecules it learned from, with their measured activity from ChEMBL and how similar they are. That is the
> evidence: you can see why it answered the way it did. And in the sidebar, the held-out score for this target with
> a confidence interval, and the simple baseline it had to beat.

### 4. The abstain (ends 2:20) — clear the box, paste caffeine, open the expander

> Now the part I care about most. This is caffeine. It is not a kinase inhibitor, and the model has never seen
> anything like it. A plain classifier would hand you a confident number anyway, and it would be meaningless. This
> one refuses: outside what this model has seen, maximum similarity zero point one five against a cut-off of zero
> point seven one, no prediction shown. The probability column is empty and abstain is ticked. I wrote that rule
> before I trained anything.

Do not say the hidden score out loud. The model does produce one for caffeine, but the app never shows it, and a
number that is not on screen is a claim the viewer cannot check.

### 5. Cell lines (ends 2:50) — Cell lines tab, Example, pick NCI-H1573, scroll the drug table

> Second question. Three mutated genes: KRAS, TP53 and STK11. It finds the screened cell lines sharing the most of
> those hotspot mutations. This lung line shares all three. Pick it, and you see how that line actually responded
> to two hundred and two drugs in the PRISM screen, most sensitive first, with structures. These are measurements,
> not predictions. It is a lookup, and the app says so.

### 6. Safety flags (ends 3:15) — Safety flags tab, Example, open the first expander

> Third question. Twelve Tox21 assays. For each one it shows the score next to how often molecules are really
> active in that assay, and how well the model ranked held-out molecules. A score above the assay's own rate gets
> marked. There is no toxicity verdict, because these models are not good enough to give one, and the screen says
> so.

### 7. Analogs (ends 3:55) — Analogs tab, Example, let it score, then read the orange warning

> Fourth question, and the newest. This is a known CDK6 inhibitor. The app edits it, one small change at a time
> from a fixed list of nine, and scores every copy. Nothing here has been measured anywhere; the app made these
> molecules up. And read what it says about its own answer: all ten copies score the same, a spread of zero,
> smaller than the zero point zero four four these models move between splits. So it tells you this is not a
> ranking, and that nothing beats the molecule I started with.

Two things to get right in this shot. **Read the warning the app prints, do not recite the numbers above.** The
spread is computed at render time from the rows on screen, so a different parent molecule gives different numbers;
the figures here are what the Example molecule gave on 2026-11-05. And do not call these analogs candidates,
leads, or anything that implies they are worth making. They are edits to a training molecule, which is why the tab
says so before it shows a single score.

### 8. The honest part (ends 4:35) — Cell lines tab, scroll to the greyed-out model ranks

> I wrote the evaluation rules down before training anything: scaffold splits, so test molecules share no core
> structure with training ones; leave-lineage-out splits for cell lines; baselines and confidence intervals
> throughout. Then I kept the answers I did not like. The drug response models, on this tab, barely beat a coin
> flip: a median score of zero point five five, and a hundred and seventy-one of two hundred and two are
> statistically weak. So the tab leads with the measured data and greys the weak model ranks out. A negative result
> is still a result.

### 9. Learning, AI, next (ends 5:35) — back to the front page

> Three things I learned. A high score can come from the data, not the model: most molecules in these ChEMBL sets
> are active, so even a random ranking scores well. Licences matter: my first cell-line source forbids this exact
> use, so I moved to one that allows it. And a README written inside your own project forgets to tell anyone to
> clone it. Only a fresh clone caught that.
> The app uses classic machine learning trained here on public data. No language model runs inside it. I built it
> with Claude Code, which wrote code and tests from my briefs, and a reviewer agent found reporting problems that
> changed my evaluation protocol. Every decision was mine, and they are all listed in the plan.
> All four loops are live. What is left is one final check that every number in the README matches its source file.
> Thanks for watching.

## Shot list
| # | What is on screen | What is said | Length | Recorded? |
|---|---|---|---|---|
| 1 | Front page, Activity tab | The problem | 0:35 | [ ] |
| 2 | Scroll across the four tabs | What it is, and what it is not | 0:35 | [ ] |
| 3 | CDK6, Example, first expander open | Scores, then the drawn evidence | 0:35 | [ ] |
| 4 | Paste caffeine, expander open | It abstains, and why | 0:35 | [ ] |
| 5 | Cell lines, Example, NCI-H1573, drug table | Lookup, measured responses | 0:30 | [ ] |
| 6 | Safety flags, Example, expander open | Score against the assay's own rate | 0:25 | [ ] |
| 7 | Analogs, Example, the orange warning | Made-up molecules, and a ranking that is not one | 0:40 | [ ] |
| 8 | Cell lines, greyed model ranks | The negative result, kept on purpose | 0:40 | [ ] |
| 9 | Front page | Learning, AI disclosure, next step | 1:00 | [ ] |

Total 5:35. The 6:00 limit leaves 25 seconds of slack for the app to load between clicks. Shot 7 needs the most of
it: scoring the analogs runs a spinner for a second or two.

## Numbers said out loud, and where they come from
Say these only if the screen shows them in the same shot.
| Said | Source |
|---|---|
| CDK6 held-out ROC-AUC 0.894, 95% CI 0.784 to 0.980 | `results/activity_models.md`, shown in the sidebar |
| caffeine: max similarity 0.15, cut-off 0.71 | the app's own warning line, checked 2026-11-05 |
| 202 drugs in the PRISM screen | `results/loop2_models.md` |
| drug models: median ROC-AUC 0.546, 171 of 202 weak | `results/loop2_models.md` |
| 12 Tox21 assays | `results/tox21_models.md` |
| analogs: ten scored, spread 0.000 | the Analogs tab's own warning, computed at render time, seen 2026-11-05 |
| the 0.044 these models move between splits | `results/activity_models.md`, "Split variance (disclosure)": the CDK6 random forest over scaffold-split seeds 0 to 4 |

## Upload checklist
- [ ] Under 6:00
- [ ] Shows the project working
- [ ] No copyrighted music
- [ ] Visibility is public or unlisted, link opens when signed out
- [ ] Link pasted into the Devpost form
- [ ] Link pasted into `docs/submission.md` and the README
