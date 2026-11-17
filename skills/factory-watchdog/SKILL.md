---
name: factory-watchdog
description: Find pilot Factory issues stale for over six hours and safely nudge or resume their foreman through the relay.
---

# Watchdog

1. Read factory-linear-state and the runtime adapter. Record current UTC time.
2. Query BOTH pilot team ids for issues carrying ANY Factory child except done/failed; paginate all results.
   Do not use issue.updatedAt alone: unrelated human comments must not hide stale factory state.
3. Read each issue's single state comment. If valid and updated_at is strictly more than six hours old,
   invoke factory-relay semantics with the issue id and a stale-state event. Deduplicate by issue id.
   A waiting foreman is live: nudge it, never replace it just because it is old.
4. Intake with no state may start a foreman after checking for a live intake owner; non-intake without state,
   malformed/multiple comments, invalid timestamps or ambiguous liveness require an operator report.
5. Recheck state before each nudge to avoid racing a new transition. Do not change labels, synthesize human
   signals, bypass checkpoints, restart active stages or spend unbounded ACU. Stop when the run budget
   is nearly exhausted and report the unprocessed page/cursor for the next run.
6. No matches is a successful empty scan. API/pagination failures are partial/failed scans, never zero matches.

## Output contract

Report JSON {scanned, stale, notified, resumed, skipped, errors, next_cursor}; counts are integers,
errors is an array of issue/error records and next_cursor is null when complete.
Devin runs this as a bounded Lite scheduled session; it is recovery, not the primary wake path.
