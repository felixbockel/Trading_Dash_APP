# Quantitative Strategy Framework

## 1. Strategy families

The platform processes four separate strategy categories, each operating on its designated timeframe.

| Strategy family | Daily variant | Weekly variant |
|---|---|---|
| Swing trading | Daily Swing Trading | Weekly Swing Trading |
| Positioning | Daily Positioning | Weekly Positioning |

The local processing service invokes each category independently for every ticker in its configured universe.

## 2. Swing-trading framework

The swing-trading strategy definitions are named around:
- Commodity Channel Index (CCI)
- 20-period moving average (MA20)
- 40-period moving average (MA40)
- Daily or weekly data intervals

The repository README also describes analysis of moving-average trend and relative positioning, price action and trend conditions, entry and exit signals, dynamic stop-loss calculations, trailing stop-loss mechanisms, and earnings-related warnings.

The exact formulas, thresholds, sequencing, and decision rules belong to the strategy-definition modules. They are intentionally not reproduced in this architecture document.

## 3. Positioning framework

The daily and weekly positioning strategies provide separate timeframe-specific analytical outputs. Their results are stored independently from swing-trading outputs so they can be selected and examined separately in the dashboard.

The supplied materials do not provide enough detail to specify the positioning calculations or signal rules. This document therefore describes their role and output separation without inventing their methodology.

## 4. Batch execution

For each ticker, the service attempts all four strategy functions in sequence. Each strategy call has its own exception handler. A failure for one ticker/strategy is logged and the service continues with the next strategy call.

This supports broad-universe batch processing, although the service's overall completion and data coverage still depend on the quality and availability of market data and the behaviour of each strategy function.

## 5. Interpretation and validation

Generated strategy outputs are analytical signals and historical records. They should not be treated as evidence of future performance. A separate validation process would be required to assess methodology, data quality, look-ahead bias, transaction costs, slippage, survivorship bias, and out-of-sample behaviour.

The supplied documentation does not provide verified performance statistics, so none are asserted here.
