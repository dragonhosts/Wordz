# Native helper routing

Run from the repository root with Python 3.11+. No pip packages or Git Bash are
required. The original shell helpers are preserved under `upstream/` for audit,
but are not runtime dependencies and must not be sourced or executed by skills.

| Source helper / operation | Native route |
| --- | --- |
| resolve_config, mode/tier queries | `python tools/game-studio/studio.py config [--system combat]` |
| get_yaml_key / array / effective values | `python tools/game-studio/studio.py get <dotted-key>`; output includes source |
| set_yaml_key / local settings | `python tools/game-studio/studio.py set <key=value> [--local] [--dry-run]` |
| enum/local-scope validation | config/set reject invalid values, duplicate keys and personal overrides of shared settings |
| story-status | `python tools/game-studio/studio.py status`; inspect requested story and its dependencies |
| artifact-check / stage detection | `python tools/game-studio/studio.py workflow help`; map existing approved project docs before checking missing artifacts |
| gdd-structure-check | `python tools/game-studio/studio.py inspect gdd <path>`; presence only, apply tier afterwards |
| adr-dep-graph | `python tools/game-studio/studio.py inspect adrs <directory>`; references only, assess dependencies in workflow |
| review-scope | `python tools/game-studio/studio.py inspect changes`; use actual git diff and changed paths |
| review-receipts / project-coherence | Read the referenced review receipts and authoritative docs, compare applicable requirements; do not fabricate script verdicts |
| rotate-session-state | Preserve bounded checkpoint, copy detailed narrative into a dated log only when needed; no automatic rotation/destruction |
| skill-test static | `python tools/game-studio/studio.py check --scope migration` |
| asset validation | `python tools/game-studio/studio.py check --scope assets` |
| pre-commit validation | `python tools/game-studio/studio.py check --scope commit [--message-file <file>]` |

Settings values use JSON literals for booleans, arrays, numbers and null, or plain
strings for enums. The config files contain JSON objects, which are valid YAML;
generic indentation-style YAML is rejected with a clear error. Individual knobs
override rigor derivation without pinning the other knobs. Only personal keys
may be set locally. Configuration errors stop the workflow; do not silently use
a different tier. Upstream legacy mirror files are historical and not read.

Hook output and configuration are in `.codex/`; operational task/evidence files
are in `production/`. Source testing-framework specs/rubrics are available under
`.agents/game-studio/upstream/CCGS Skill Testing Framework/` for behavioral review;
their source tool and path assumptions still need this adapter.
