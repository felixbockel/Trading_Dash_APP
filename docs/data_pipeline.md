# Data Pipeline and Storage

## 1. Processing sequence

The local service performs the following sequence:

1. Start a scheduled task and record its start time.
2. Establish local output and Dropbox directory paths.
3. Ensure the four per-ticker output folders exist.
4. Iterate over the configured ticker universe.
5. Execute each of the four strategy functions for each ticker.
6. Save per-ticker plotting payloads when the expected columns are present.
7. Accumulate strategy records without the `plot_dict` column.
8. Concatenate accumulated records into one combined pickle per strategy.
9. Run garbage collection.
10. Transfer generated outputs to Dropbox and log elapsed time.

## 2. Two output forms

### Per-ticker plotting datasets
The `save_incl_plot` function writes a pickle under a strategy-specific folder, using the ticker as the filename. It saves the `Ticker` and `plot_dict` columns when both are present.

These instrument-level files preserve chart-related information for later visualisation.

### Combined analytical datasets
For aggregation, the service drops `plot_dict` from each result and appends the remaining data to a strategy-specific list. At the end of the ticker loop, records are concatenated and written as one combined pickle per strategy.

This creates a separation between chart payloads and consolidated analytical records.

## 3. Representative Dropbox layout

The supplied Word document lists four combined pickle files and four corresponding instrument-level folders:

```text
Dropbox/
├── all_daily_swing_excl_plot.pkl
├── all_weekly_swing_excl_plot.pkl
├── all_daily_positioning_excl_plot.pkl
├── all_weekly_positioning_excl_plot.pkl
├── all_daily_swing_incl_plot/
├── all_weekly_swing_incl_plot/
├── all_daily_positioning_incl_plot/
└── all_weekly_positioning_incl_plot/
```

The screenshot on page 13 shows the same four combined files and four per-strategy folders. The screenshot and code excerpts use slightly different capitalisation in some names; the actual paths must match exactly across producer and consumer environments.

## 4. Transfer safeguards

For each per-ticker folder, the service:
- Copies each source file to a destination temporary filename ending in `.tmp`.
- Uses `os.replace` to replace the destination file.
- Removes temporary files and destination files that no longer exist in the source folder.
- Waits until a snapshot of file paths, sizes, and modification times remains unchanged for the configured stable period.
- Removes the local source folder after the wait completes.

The stability wait checks every five seconds, uses a 30-second stable period by default, and has a 900-second timeout.

For each combined pickle, the service copies to a temporary destination, replaces the destination, and removes the local source file after the copy operation.

These safeguards improve transfer discipline but do not provide a full transactional distributed-storage protocol. Interrupted syncs, cloud client errors, and process termination still need explicit recovery testing.

## 5. Scheduling details

The service uses the Python `schedule` package. The supplied code registers runs at 11:00 for Monday through Friday and also registers Saturday at 11:00. The adjacent comment describes Monday-to-Friday scheduling, so the Saturday registration should be treated as an explicit implementation detail to review rather than silently omitted.

The scheduler checks for pending work every 30 seconds. The code does not show an explicit timezone argument for the schedule; the machine's local clock and configuration therefore matter.

## 6. Data-format considerations

Pickle preserves Python objects and is convenient for storing pandas objects and plotting dictionaries. It is Python-specific and should only be loaded from trusted sources. For long-term interchange, schema versioning and a more portable tabular format may be worth considering.

## 7. Pipeline risks to review

- Confirm folder and filename case is consistent between Windows, Dropbox, and Render.
- Verify that a failed strategy does not leave a misleadingly stale per-ticker output from an earlier run.
- Confirm combined files are not read while being updated.
- Test interrupted copies, Dropbox delays, and timeout behaviour.
- Confirm the local source is retained when a transfer is incomplete.
- Define data versioning and retention.
- Validate ticker-level coverage and report missing or failed instruments.
