> Codex adaptation: read `.agents/game-studio/CODEX.md` first. It supersedes
> source-runtime tool names, approvals, models, paths, helpers and engine defaults
> below. Treat upstream shell examples as reference, not executable bootstrap.

> Gate definition. The spawning skill passes this file's path to the director agent; the AGENT reads it — the parent session should not.

# CD-PLAYTEST — Player Experience Validation

Agent: `creative-director` | Model tier: Opus | Domain: Vision, pillars, player experience

**Trigger**: After playtest reports are generated (`$studio-playtest-report`), or after
any session that produces player feedback

**Context to pass**:
- Playtest report — its file path, or its content inline when the calling skill
  reviews before saving (`$studio-playtest-report` does)
- Game pillars and core fantasy statement
- The specific hypothesis being tested

**Prompt**:
> "Review this playtest report against the game's design pillars and core fantasy.
> Is the player experience matching the intended fantasy? Are there systematic issues
> that represent pillar drift — mechanics that feel fine in isolation but undermine
> the intended experience? Return APPROVE (core fantasy is landing), CONCERNS [gaps
> between intended and actual experience], or REJECT [core fantasy is not present —
> redesign needed before further playtesting]."

**Verdicts**: APPROVE / CONCERNS / REJECT
