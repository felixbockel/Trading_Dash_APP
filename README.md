# Automated Quantitative Trading & Market Analysis Platform

## Project Overview

A personal quantitative trading and financial-market analysis platform developed in Python to systematically analyse financial instruments, identify potential trading opportunities, evaluate market conditions, and automate the generation and storage of strategy results.

The platform implements multiple algorithmic trading strategies across daily and weekly timeframes, processes a large universe of financial instruments, calculates technical indicators, generates trading signals, and stores structured historical results for further analysis.

The system combines quantitative analysis, automated data processing, strategy execution, data management, visualisation, and cloud deployment into an integrated workflow.

## Core Capabilities

- Automated analysis of a large universe of financial instruments.
- Multiple independent algorithmic trading strategies.
- Daily and weekly market analysis.
- Technical-indicator calculations and signal generation.
- Automated processing and storage of strategy results.
- Historical strategy data and chart generation.
- Interactive data exploration and visualisation.
- Automated execution through a background service.
- Cloud-based data synchronisation and dashboard deployment.
- Logging, error handling, and recovery mechanisms.

## Quantitative Trading Strategies

The platform currently incorporates four primary strategy categories:

- Daily Swing Trading
- Weekly Swing Trading
- Daily Positioning
- Weekly Positioning

Each strategy operates independently and uses timeframe-specific market data and analytical calculations to identify and evaluate trading opportunities.

### Swing Trading

The swing-trading framework incorporates technical analysis including:

- Commodity Channel Index (CCI)
- 20-period moving average (MA20)
- 40-period moving average (MA40)
- Moving-average trend and relative positioning
- Price action and trend conditions
- Entry and exit signals
- Dynamic stop-loss calculations
- Trailing stop-loss mechanisms
- Earnings-related warnings

The system calculates and tracks strategy conditions, entry signals, exit signals, and relevant market information for subsequent analysis and visualisation.

### Positioning Strategies

Separate daily and weekly positioning strategies provide an additional systematic approach to market analysis.

These strategies generate timeframe-specific analytical outputs and trading information, allowing positioning signals and historical results to be examined independently from swing-trading strategies.

## Data Processing & Automation Architecture

The platform uses an automated Python processing pipeline to execute strategy calculations across the instrument universe.

The pipeline:

1. Retrieves financial market data.
2. Processes instruments through individual strategy modules.
3. Calculates technical indicators and strategy-specific conditions.
4. Generates analytical outputs and trading signals.
5. Creates instrument-level datasets containing charting information.
6. Aggregates results into consolidated datasets.
7. Serialises outputs for efficient storage and retrieval.
8. Synchronises generated datasets with cloud storage.
9. Makes processed data available to the interactive dashboard.

The processing framework is designed to handle large batches of instruments while maintaining separate outputs for individual instruments and consolidated strategy datasets.

## Data Engineering & Storage

The platform uses structured Python datasets and serialisation to preserve both analytical results and underlying chart data.

Data outputs include:

- Individual instrument datasets.
- Consolidated strategy datasets.
- Historical strategy records.
- Technical-indicator data.
- Trading signals and strategy metadata.
- Charting datasets used by the visualisation application.

Pickle-based storage is used to preserve Python data structures, including datasets containing plotting information, allowing analytical results to be loaded without recalculating the underlying strategy.

Dropbox is integrated into the data pipeline for synchronisation and storage of generated datasets.

The synchronisation process incorporates file-management safeguards, sequential transfers, atomic file replacement, error handling, and logging to improve data integrity and reliability.

## Automated Execution & Infrastructure

The strategy-processing system operates through an automated background service running on Windows.

Infrastructure components include:

- Windows service execution.
- Automated task scheduling.
- Batch processing of multiple strategy modules.
- Logging and error monitoring.
- Exception handling and troubleshooting.
- Automated file management.
- Cloud-storage synchronisation.
- Execution-time monitoring.
- Recovery and reliability improvements.

The automation is designed to execute without requiring manual intervention during normal operation.

## Interactive Analytics Dashboard

A web-based dashboard provides access to generated strategy datasets and facilitates historical analysis.

The dashboard enables users to:

- Select between daily and weekly strategies.
- Select swing-trading or positioning datasets.
- Load processed datasets into interactive tables.
- Sort and inspect analytical results.
- Select individual instruments for detailed chart analysis.
- Visualise historical price action and technical indicators.
- Examine trading signals and strategy conditions.
- Analyse individual instruments without rerunning the entire strategy pipeline.

The charting functionality includes interactive financial charts, candlestick visualisation, technical indicators, moving averages, signal markers, and dynamic stop-loss levels.

The dashboard is developed using Python, Dash, Plotly and related libraries.

## Cloud Deployment & Integration

The interactive dashboard is deployed as a web application using Render.

The system integrates multiple components across the workflow:

- Local Python processing environment.
- Automated Windows execution service.
- Dropbox cloud storage.
- GitHub source-code management.
- Render-hosted web dashboard.

This architecture separates strategy execution and data generation from the web-based analytical interface.

## Technology Stack

**Programming & Data Analysis**
- Python
- Pandas
- NumPy

**Financial Data**
- yfinance
- Historical market data processing

**Quantitative Analysis**
- Technical indicators
- Systematic trading signals
- Trend analysis
- Moving averages
- CCI

**Visualisation & Web Applications**
- Plotly
- Plotly Graph Objects
- Dash
- Dash Bootstrap Components

**Automation & Infrastructure**
- Windows Services
- Python scheduling
- Logging
- Exception handling
- Automated file processing

**Data Storage & Integration**
- Pickle serialisation
- Dropbox API / cloud synchronisation

**Deployment & Development**
- GitHub
- Render
- JupyterLab
- Python development environment

## Engineering Challenges

Development has involved addressing practical challenges associated with automated financial-data processing and production-style Python applications, including:

- Handling inconsistent or incomplete market-data responses.
- Managing large-scale multi-instrument processing.
- Improving automated execution reliability.
- Implementing structured logging for background services.
- Preventing incomplete or conflicting cloud synchronisation.
- Preserving complex analytical datasets during storage and transfer.
- Improving dashboard stability when processing missing or malformed datasets.
- Separating analytical computation from data visualisation.
- Building reusable strategy-processing and data-handling workflows.

## Project Objective

The long-term objective is to develop a scalable quantitative analysis platform capable of systematically evaluating financial markets, maintaining historical strategy data, supporting the development and assessment of trading systems, and providing an accessible analytical interface for reviewing trading opportunities and market behaviour.
