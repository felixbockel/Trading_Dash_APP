# Development Roadmap

This roadmap separates improvements suggested by the supplied implementation from capabilities that would require additional design and testing. It does not imply that every item is currently implemented.

## 1. Data quality and traceability
- Record run IDs, timestamps, and source-data dates in generated outputs.
- Track per-ticker/per-strategy success and failure counts.
- Distinguish missing data from a valid empty strategy result.
- Add schema/version metadata to the serialised datasets.
- Validate freshness before the dashboard presents a dataset as current.

## 2. Synchronisation reliability
- Test Dropbox transfers interrupted during copy, replacement, or cloud sync.
- Preserve local outputs until destination integrity has been confirmed.
- Add checksums or equivalent content verification for critical files.
- Make producer/consumer filename case and folder conventions consistent.
- Define recovery behaviour after the 900-second folder-stability timeout.
- Consider publishing a run-complete manifest only after all outputs have synced.

## 3. Scheduler and service operations
- Resolve the weekday-versus-Saturday schedule discrepancy.
- Configure the intended timezone explicitly.
- Prevent overlapping scheduled runs.
- Define restart behaviour after Windows updates or power interruptions.
- Add log rotation, retention, and alerting.

## 4. Dashboard robustness
- Validate input files before loading.
- Handle missing, malformed, stale, and partially synchronised datasets clearly.
- Display dataset generation time and coverage.
- Add graceful error states when Dropbox data is unavailable.
- Test application restarts and Render deployment updates.

## 5. Security and maintainability
- Keep credentials and personal paths outside version control.
- Load pickle files only from trusted sources.
- Consider a versioned, portable data schema for longer-term storage.
- Separate configuration from processing logic.
- Add automated tests for serialisation, aggregation, and file handoff.

## 6. Quantitative validation
- Document strategy definitions and assumptions in a controlled location.
- Verify calculations against independently reproducible examples.
- Review data timing, look-ahead bias, survivorship bias, and corporate actions.
- Evaluate transaction costs, slippage, and liquidity assumptions where relevant.
- Use out-of-sample testing and avoid presenting historical results as guaranteed future performance.

## 7. Suggested acceptance criteria
Before describing the pipeline as operationally robust, define measurable criteria for successful strategy coverage, dataset freshness, transfer integrity, recovery from interruption, dashboard availability, and traceable error reporting.
