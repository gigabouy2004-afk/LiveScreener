# Changelog

## 2026-07-30 - Active documentation synchronization

### Changed

- Updated every active V17 document to name
  `docs/MOMENTUM_ENGINE_MASTER_BLUEPRINT.md` as the primary development
  authority.
- Assigned explicit roles to the engine specification, research protocol,
  field guide, validation records, tagged handover and action plan.
- Updated the handover file map and continuation guidance for the cleaned V17
  structure.
- Removed ambiguity between current development instructions and immutable
  historical evidence.

### Maintenance rule

Future changes to calculations, data contracts, outcomes, gates, goals or
activation status must update the master blueprint, each affected supporting
document, the README when entry guidance changes, and this changelog in the
same commit.

## 2026-07-30 - Standalone Momentum Engine authority

### Added

- Created `docs/MOMENTUM_ENGINE_MASTER_BLUEPRINT.md` as the primary,
  self-contained development authority.
- Consolidated the validated V17 foundation, previous-session/current-session
  logic, inherited benchmark parameters, point-in-time research contract,
  backtesting evidence, chronological validation design, development gates,
  interim milestones, final goals, guardrails and reproduction commands.

### Why

The Momentum Engine must remain developable from one document in total
isolation. A new session should not need to reconstruct intent from multiple
handover, validation or planning files, and must never consult retired
material to fill a perceived gap.

## 2026-07-30 - Active/retired documentation boundary

### Changed

- Pre-V17 documentation was moved from `docs` to
  `Retired/Documentation/Pre-V17`.
- The prior full changelog was retained in the same archive and replaced by
  this active V17-only changelog.
- A post-signoff working appendix was separated from the authoritative V17
  handover and retained under `Retired/Documentation/Working Session Notes`.
- Generated baseline outputs and smoke-test results were moved from `output`
  to `Retired/Test Results/V17 Baseline 2026-07-29`.
- The invalid root-level local note and other superseded root documents,
  historical results, backups and temporary working files were consolidated
  under the workspace-level `Retired` directory.

### Why

Retired material is preserved for audit and recovery, but it is not a current
source of requirements, calculations, thresholds, conclusions or work
instructions. Separating it prevents superseded or invalid context from
misdirecting future application reads.

This is an ongoing documentation-lifecycle rule: when a document, work
instruction, working file or generated test result is superseded, invalidated
or no longer part of the active baseline, it must be moved to `Retired` and
the move and reason must be recorded in this changelog.

## Unreleased - V17 momentum research foundation

### Added

- U.S.-only V17 research entry point using the previous completed session as
  its immutable daily foundation.
- Completed current-session 1-hour and 4-hour diagnostics reconstructed from
  regular-session 30-minute bars.
- Point-in-time daily feature and future-outcome panel foundation for all
  supplied equity/session observations, including young listings.
- Chronological training, calibration and untouched-holdout assignment with
  outcome-boundary purging.
- Plain-language review output, research protocol, field guide, validation
  records, authoritative handover and continuation action plan.

### Validation

- 78 deterministic and regression tests passed at the baseline handover.
- The five-year inherited daily-rule replay produced a -0.0627% gross mean and
  failed the promotion gate.
- Multi-year 4-hour/1-hour efficacy remains untested pending a replayable
  several-year 30-minute archive.
- No classifier or production rule was introduced.
