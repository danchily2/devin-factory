---
name: factory-watchdog
description: Recover pilot Factory issues with one state comment stale for over six hours and a verified finished or unreachable owner; never handle intake.
---

# Watchdog

1. Read factory-linear-state and the runtime adapter. Record current UTC time.
2. Query BOTH pilot team ids for issues carrying ANY Factory child except intake/done/failed; paginate all results.
   Do not use issue.updatedAt alone: unrelated human comments must not hide stale factory state.
3. Re-read labels and all comment pages per issue. Always skip Factory › intake, even with state; A1 owns intake.
   Skip issues with no state comment: missing state is not stale. Never start or resume either case.
   Malformed/multiple state comments, invalid timestamps or ambiguous liveness require an operator report,
   never recovery. Do not resolve claim races yourself.
4. Act only when exactly one valid state comment exists, its updated_at is strictly more than six hours old,
   its stage is not intake/done/failed AND its owner is verified finished/unreachable. A waiting foreman is live:
   skip live owners without nudging them. Invoke factory-relay semantics only after all gates pass.
   Deduplicate by issue id.
5. Recheck labels, all comments, timestamp and owner liveness immediately before recovery; skip if any gate
   no longer holds. Do not change labels, synthesize human signals, bypass checkpoints, restart active stages
   or spend unbounded ACU. Stop when the run budget
   is nearly exhausted and report the unprocessed page/cursor for the next run.
6. No matches is a successful empty scan. API/pagination failures are partial/failed scans, never zero matches.

## Output contract

Report JSON {scanned, stale, notified, resumed, skipped, errors, next_cursor}; counts are integers,
errors is an array of issue/error records and next_cursor is null when complete.
Devin runs this as a bounded Lite scheduled session; it is recovery, not the primary wake path.
After reporting (including empty/partial/error scans), end your own one-shot session: Devin uses the supported
end/terminate operation via devin_session_interact or host equivalent; Claude finishes with a final report.
