<!-- Adapted from DietrichGebert/ponytail AGENTS.md (MIT, © 2026 DietrichGebert). Its
"leave one runnable check behind" rule is dropped on purpose: tests are written only on request
(unity-testing). HTML comments are stripped before this file reaches the model. -->

# Lean code

Understand first: read the code the change touches and trace the real flow. Then, before writing
code, stop at the first rung that holds:

1. Does it need to exist at all?
2. Does Core or Game already have it? Reuse the helper, solver or pattern.
3. Does .NET, Unity or an installed package (Feel, Nice Vibrations, the Input System) already do it?
4. Can it be one line?
5. Only then: the minimum that works.

- No abstraction, config switch or boilerplate nobody asked for; a seam waits for its second real
  case (`unity-architecture`, `refactor-pass`).
- Deletion over addition, fewest files, the shortest diff in the right place. The smallest change in
  the wrong place is a second bug.
- A bug fix goes to the shared root, not only to the caller the report named.
- Question a complex request: "do you need X, or does Y cover it?"
- A deliberate shortcut with a known ceiling gets a comment naming the ceiling and the way up.

Never cut: understanding the problem, validation of untrusted input, handling that prevents data
loss, anything explicitly requested.
