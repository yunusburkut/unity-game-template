# Project reviewers and the co-op gate

Loaded from pipeline 6.1 when the game has its own agents in `.claude/agents` or the
`.claude/skills/coop-chaos-design` skill (the coop-multiplayer pack adds both).

- **Project agents.** A project agent in the game's `.claude/agents` whose description matches the change joins every
  round too (when `.claude/agents/net-auditor.md` exists, `net-auditor` for a change that touches Game/Net, a
  NetworkBehaviour, spawning or a moving device): its brief adds "map each finding to the review rubric's severities
  and list them in its format", and its findings are scored like any reviewer's. A generator such as `idea-forge`
  reviews nothing.
- **Co-op gate.** A co-op mechanic card (the game has `.claude/skills/coop-chaos-design`) also runs that skill's gate
  table on the built mechanic in the main session before round 1, since `design-critic` leaves the ship verdict to it.
  A failed row whose "Fail means" is "Do not build" or "Fix before building" becomes a [karar] in Next (fix it, or ship
  with the weakness named) and the card gets no handoff until the user answers; any other failed row is named in the
  handoff.
