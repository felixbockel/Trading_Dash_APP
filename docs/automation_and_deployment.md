# Automation and Deployment

## 1. Local Windows service

The processing service runs in a local Windows Python environment. The supplied document identifies a service working directory of `C:\\TradingService`, a Python script named `execution_analysis_of_trading_strategies.py`, and a log file named `service.log`.

The code excerpt configures file logging, creates the log directory if required, removes existing root logger handlers, and appends timestamped log records to the service log.

Personal machine paths in the source document are examples and should be replaced by environment-specific configuration. They should not be copied into public repository documentation as universal paths.

## 2. Scheduler

The script uses the `schedule` package to register a task at 11:00 on weekdays and also Saturday. The scheduler polls every 30 seconds.

The code comment says Monday to Friday, while an additional Saturday registration is present. Confirm the intended schedule and the machine's local timezone before relying on it.

## 3. Dropbox handoff

The service writes files locally, copies them to a Dropbox-synchronised directory, and removes local source files after the relevant transfer path completes. Per-ticker folders include a destination stability wait; combined pickle files use temporary-copy and replace.

Dropbox is therefore part of the data-delivery path between the Windows processor and the hosted dashboard.

## 4. Render dashboard deployment

The GitHub repository includes:
- `trading_data_plot.py`
- `dropbox_utils.py`
- `requirements.txt`
- `runtime.txt`
- `Procfile`
- `render.yaml`

These files support the Python dashboard application and its Render deployment configuration. The exact service settings and secret names should be verified against the current Render configuration rather than reproduced from assumptions.

## 5. Configuration and secrets

Keep Dropbox tokens, API credentials, local user paths, and other secrets out of source control. Use environment variables or the hosting provider's secret-management settings where applicable. The public documentation intentionally does not include credentials or personal paths.

## 6. Operational hardening

Recommended areas for further validation include:
- Service startup after Windows reboot
- Duplicate scheduler execution prevention
- Explicit timezone configuration
- Log rotation and retention
- Dropbox sync timeout and interrupted-transfer recovery
- Dataset freshness indicators in the dashboard
- Render restart and missing-file behaviour
- Monitoring and alerting for failed strategy runs or incomplete data delivery
