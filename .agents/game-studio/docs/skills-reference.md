> Codex adaptation: read `.agents/game-studio/CODEX.md` first. It supersedes
> source-runtime tool names, approvals, models, paths, helpers and engine defaults
> below. Treat upstream shell examples as reference, not executable bootstrap.

# Available Skills (Slash Commands)

74 slash commands organized by phase. Type `/` in Claude Code to access any of them.

## Onboarding & Navigation

| Command | Purpose |
|---------|---------|
| `$studio-start` | First-time onboarding — asks where you are, then guides you to the right workflow |
| `$studio-help` | Context-aware "what do I do next?" — reads current stage and surfaces the required next step |
| `$studio-project-stage-detect` | Full project audit — detect phase, identify existence gaps, recommend next steps |
| `$studio-setup-engine` | Configure engine + version, detect knowledge gaps, populate version-aware reference docs |
| `$studio-adopt` | Brownfield format audit — checks internal structure of existing GDDs/ADRs/stories, produces migration plan |
| `$studio-settings` | View or change project config — the effective merged values, or a local override in `project.local.yaml` |

## Game Design

| Command | Purpose |
|---------|---------|
| `$studio-brainstorm` | Guided ideation using professional studio methods (MDA, SDT, Bartle, verb-first) |
| `$studio-map-systems` | Decompose game concept into systems, map dependencies, prioritize design order |
| `$studio-design-system` | Guided, section-by-section GDD authoring for a single game system |
| `$studio-quick-design` | Lightweight design spec for small changes — tuning, tweaks, minor additions |
| `$studio-review-all-gdds` | Cross-GDD consistency and game design holism review across all design docs |
| `$studio-propagate-design-change` | When a GDD is revised, find affected ADRs and produce an impact report |

## Art & Assets

| Command | Purpose |
|---------|---------|
| `$studio-art-bible` | Guided, section-by-section Art Bible authoring — creates visual identity spec before asset production begins |
| `$studio-asset-spec` | Generate per-asset visual specifications and AI generation prompts from GDDs, level docs, or character profiles |
| `$studio-asset-audit` | Audit assets for naming conventions, file size budgets, and pipeline compliance |

## UX & Interface Design

| Command | Purpose |
|---------|---------|
| `$studio-ux-design` | Guided section-by-section UX spec authoring (screen/flow, HUD, or pattern library) |
| `$studio-ux-review` | Validate UX specs for GDD alignment, accessibility, and pattern compliance |

## Architecture

| Command | Purpose |
|---------|---------|
| `$studio-create-architecture` | Guided authoring of the master architecture document |
| `$studio-architecture-decision` | Create an Architecture Decision Record (ADR) |
| `$studio-architecture-review` | Validate all ADRs for completeness, dependency ordering, and GDD coverage |
| `$studio-create-control-manifest` | Generate flat programmer rules sheet from accepted ADRs |

## Stories & Sprints

| Command | Purpose |
|---------|---------|
| `$studio-create-epics` | Translate GDDs + ADRs into epics — one per architectural module |
| `$studio-create-stories` | Break a single epic into implementable story files |
| `$studio-dev-story` | Read a story and implement it — routes to the correct programmer agent |
| `$studio-sprint-plan` | Generate or update a sprint plan; initializes sprint-status.yaml |
| `$studio-sprint-status` | Fast 30-line sprint snapshot (reads sprint-status.yaml) |
| `$studio-story-readiness` | Validate a story is implementation-ready before pickup (READY/NEEDS WORK/BLOCKED) |
| `$studio-story-done` | 8-phase completion review after implementation; updates story file, surfaces next story |
| `$studio-estimate` | Structured effort estimate with complexity, dependencies, and risk breakdown |

## Reviews & Analysis

| Command | Purpose |
|---------|---------|
| `$studio-design-review` | Review a game design document for completeness and consistency |
| `$studio-code-review` | Architectural code review for a file or changeset |
| `$studio-balance-check` | Analyze game balance data, formulas, and config — flag outliers |
| `$studio-content-audit` | Audit GDD-specified content counts against implemented content |
| `$studio-scope-check` | Analyze feature or sprint scope against original plan, flag scope creep |
| `$studio-perf-profile` | Structured performance profiling with bottleneck identification |
| `$studio-tech-debt` | Scan, track, prioritize, and report on technical debt |
| `$studio-gate-check` | Validate readiness to advance between development phases (PASS/CONCERNS/NOT ASSESSED/FAIL) |
| `$studio-consistency-check` | Scan all GDDs against the entity registry to detect cross-document inconsistencies (stats, names, rules that contradict each other) |
| `$studio-security-audit` | Audit the game for security vulnerabilities: save tampering, cheat vectors, network exploits, data exposure, and input validation gaps |

## QA & Testing

| Command | Purpose |
|---------|---------|
| `$studio-qa-plan` | Generate a QA test plan for a sprint or feature |
| `$studio-smoke-check` | Run critical path smoke test gate before QA hand-off |
| `$studio-soak-test` | Generate a soak test protocol for extended play sessions |
| `$studio-regression-suite` | Map test coverage to GDD critical paths, identify fixed bugs without regression tests |
| `$studio-test-setup` | Scaffold the test framework and CI/CD pipeline for the project's engine |
| `$studio-test-helpers` | Generate engine-specific test helper libraries for the test suite |
| `$studio-test-evidence-review` | Quality review of test files and manual evidence documents |
| `$studio-test-flakiness` | Detect non-deterministic (flaky) tests from CI run logs |
| `$studio-skill-test` | Validate skill files for structural compliance and behavioral correctness |
| `$studio-skill-improve` | Improve a skill using a test-fix-retest loop — diagnose, propose fix, rewrite, verify |

## Production

| Command | Purpose |
|---------|---------|
| `$studio-milestone-review` | Review milestone progress and generate status report |
| `$studio-retrospective` | Run a structured sprint or milestone retrospective |
| `$studio-bug-report` | Create a structured bug report |
| `$studio-bug-triage` | Read all open bugs, re-evaluate priority vs. severity, assign owner and label |
| `$studio-reverse-document` | Generate design or architecture docs from existing implementation |
| `$studio-playtest-report` | Generate a structured playtest report or analyze existing playtest notes |

## Release

| Command | Purpose |
|---------|---------|
| `$studio-release-checklist` | Generate and validate a pre-release checklist for the current build |
| `$studio-launch-checklist` | Complete launch readiness validation across all departments |
| `$studio-changelog` | Auto-generate changelog from git commits and sprint data |
| `$studio-patch-notes` | Generate player-facing patch notes from git history and internal data |
| `$studio-hotfix` | Emergency fix workflow with audit trail, bypassing normal sprint process |
| `$studio-day-one-patch` | Prepare a focused day-one patch for known issues discovered after gold master but before or at public launch |

## Creative & Content

| Command | Purpose |
|---------|---------|
| `$studio-prototype` | Concept prototype — throwaway build right after brainstorm to validate core idea (Phase 1) |
| `$studio-vertical-slice` | Pre-Production validation — production-quality end-to-end build before committing to Production (Phase 4) |
| `$studio-onboard` | Generate contextual onboarding document for a new contributor or agent |
| `$studio-localize` | Localization workflow: string extraction, validation, translation readiness |

## Team Orchestration

Coordinate multiple agents on a single feature area:

| Command | Coordinates |
|---------|-------------|
| `$studio-team-combat` | game-designer + gameplay-programmer + ai-programmer + technical-artist + sound-designer + qa-tester |
| `$studio-team-narrative` | narrative-director + writer + world-builder + level-designer |
| `$studio-team-ui` | ux-designer + ui-programmer + art-director + accessibility-specialist |
| `$studio-team-release` | release-manager + qa-lead + devops-engineer + producer |
| `$studio-team-polish` | performance-analyst + technical-artist + sound-designer + qa-tester |
| `$studio-team-audio` | audio-director + sound-designer + technical-artist + gameplay-programmer |
| `$studio-team-level` | level-designer + narrative-director + world-builder + art-director + systems-designer + qa-tester |
| `$studio-team-live-ops` | live-ops-designer + economy-designer + community-manager + analytics-engineer |
| `$studio-team-qa` | qa-lead + qa-tester + gameplay-programmer + producer |

## Overlap with Claude Code's bundled skills

Claude Code ships its own skills, and one name collides with CCGS's.

| You type | You get | Use it for |
|---------|---------|-----------|
| `$studio-code-review` | **CCGS's** — project skills take the bare name | Architectural review against this project's coding standards, SOLID, testability and the control manifest. Knows about ADRs, stories and `docs/architecture/`. |
| `/review` | **Claude Code's bundled** review — the alias of its `$studio-code-review`, which CCGS's skill shadows | Reviewing a pull request or a plain diff for correctness bugs, with no knowledge of CCGS's design documents or gates. |

Both are useful; they answer different questions. Reach for the CCGS one during
`$studio-dev-story` and before `$studio-story-done`, because it checks the things the gates
later check. Reach for the bundled one when you want a general review of a diff
that has nothing to do with a story.

CCGS does **not** turn the bundled skills off. `disableBundledSkills` would
remove all of them, including `/debug`, `/security-review` and `/simplify`,
which are worth keeping. If you want a bundled skill hidden, use
`skillOverrides` in your own `.claude/settings.local.json` rather than disabling
the whole set.
