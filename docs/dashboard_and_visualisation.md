# Dashboard and Visualisation

## 1. Purpose

The web dashboard provides an interactive interface to inspect strategy outputs produced by the separate local processing service. The dashboard is designed for exploration of precomputed analytical results rather than recalculation of the entire ticker universe on every page interaction.

## 2. Strategy selection

The public README describes selectors for:
- Daily versus weekly analysis
- Swing-trading versus positioning datasets

These choices allow the user to inspect each of the four strategy categories independently.

## 3. Analytical tables

Processed combined datasets can be loaded into interactive tables. The README describes sorting and inspection of analytical records, supporting comparison across instruments and review of strategy conditions and signals.

## 4. Instrument-level charts

The dashboard can select an individual instrument for detailed chart analysis. Documented visual elements include:
- Historical price action
- Candlestick charts
- Technical indicators
- Moving averages
- Trading-signal markers
- Dynamic stop-loss levels

The per-ticker `incl_plot` pickle files preserve the plotting information used by this charting workflow.

## 5. Separation from strategy processing

The dashboard reads generated datasets. The strategy calculations are performed by the local processing service and imported strategy-definition modules. This separation reduces the need to rerun the entire analytical pipeline when a user changes the dashboard selection.

## 6. Hosting

The repository includes Render deployment configuration (`Procfile`, `render.yaml`, and `runtime.txt`) and a Python application entry point (`trading_data_plot.py`). The supplied document identifies the deployed dashboard URL:

https://trading-uptrend-tec.onrender.com/

## 7. Scope of this description

The detailed component behaviour is described from the repository README and supplied service document. Exact callback logic, layout structure, table-column definitions, and chart interactions should be checked against the current application source before being documented at a lower level.
