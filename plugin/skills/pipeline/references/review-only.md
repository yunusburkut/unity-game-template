# Review only: `review et` / `puanla`

Loaded when the user asks for `review et` or `puanla`. It runs pipeline phase 6 alone: on the range they name, else
the card's commits, else the commits of the last task.

- **The key.** With no card those commits carry no `Card:` line: the key in place of `<Base>` is the parent of the
  range's first commit (`git rev-parse --short=7 <first>~1`), every round's brief names the range as `<key>..HEAD`
  (the reviewed commits plus the fix commits, no grep), and 6.6 writes that range into the commit body.
- **The brief.** When the range is not the card's commits, the brief's spec line reads "Spec: <the user's request, or
  the task's goal from its commit messages>; PLAN.md Now is another task, do not score its Accept items" in place of
  "Spec card: PLAN.md Now", and no Accept items or disputes of that card go with it.
- **The end.** No phase 7 follows: when a round passes, prune the `review <key>: ` lines by 6.4.3 (its `disputed` and
  `önceden` lines stay), write each [orta] it still lists as one, and, if that changed PLAN.md, commit it as `design:
  review passed` with the range and the scores in the body.
