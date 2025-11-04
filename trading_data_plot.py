#! /usr/bin/python
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import math
import re
import os
import json
import dropbox
import io

from dash import dash_table, callback, Dash, dcc, html, Input, Output, State, ctx, dash_table
import dash_bootstrap_components as dbc
from dropbox_utils import read_pickle_from_dropbox


app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server
app.title = "Pickle Plotter"

# === Dropbox File Map (new naming) ===
FILE_MAP = {
    "load-daily-swing": "/all_daily_swing_incl_plot.pkl",
    "load-weekly-swing": "/all_weekly_swing_incl_plot.pkl",
    "load-daily-positioning": "/all_daily_positioning_incl_plot.pkl",
    "load-weekly-positioning": "/all_weekly_positioning_incl_plot.pkl",
}

# === Utility Functions ===
def clean_plot_dict_string(s):
    s = re.sub(r"Timestamp\('([^']+)'\)", r"'\1'", s)
    s = re.sub(r"Timestamp\(\"([^\"]+)\"\)", r'"\1"', s)
    return s

def safe_literal_eval(val):
    try:
        if isinstance(val, str):
            cleaned = clean_plot_dict_string(val)
            return eval(cleaned, {"__builtins__": {}, "nan": math.nan})
        return val
    except Exception as e:
        print(f"Eval error: {e}")
        return None


# === Layout ===
app.layout = dbc.Container([
    html.H2("📈 Pickle Viewer & Strategy Plotter"),

    dbc.Row([
        dbc.Col(dbc.Button("📅 Daily Swing Strategy", id="load-daily-swing", color="primary", className="me-2")),
        dbc.Col(dbc.Button("🗓️ Weekly Swing Strategy", id="load-weekly-swing", color="secondary", className="me-2")),
        dbc.Col(dbc.Button("📅 Daily Positioning Strategy", id="load-daily-positioning", color="success", className="me-2")),
        dbc.Col(dbc.Button("🗓️ Weekly Positioning Strategy", id="load-weekly-positioning", color="warning", className="me-2")),
    ], className="mb-3"),

    html.Div(id='filename-display', style={"color": "gray", "marginBottom": "10px"}),

    dash_table.DataTable(
        id='data-table',
        page_size=10,
        row_selectable='single',
        cell_selectable=True,
        active_cell=None,
        selected_rows=[],
        filter_action='native',
        sort_action='native',
        sort_mode='multi',
        style_data_conditional=[],
        style_table={
            'height': 'auto',
            'overflowX': 'auto',
            'maxHeight': '600px',
        },
        style_cell={
            'fontSize': '12px',
            'minWidth': '100px',
            'width': '100px',
            'maxWidth': '120px',
            'whiteSpace': 'normal',
        },
        style_header={
            'fontSize': '10px',
            'fontWeight': 'bold',
            'backgroundColor': '#f8f9fa',
            'border': '1px solid #dee2e6'
        },
    ),

    html.Br(),
    html.Button("Plot Selected Row", id='plot-button', n_clicks=0),
    html.Div(id='plot-output'),
    dcc.Store(id='strategy-type'),
    dcc.Store(id='last-loaded-file-key')
])

uploaded_df = pd.DataFrame()

# === Sync cell click to row selection ===
@app.callback(
    Output('data-table', 'selected_rows'),
    Input('data-table', 'active_cell'),
)
def select_row_on_cell_click(active_cell):
    if active_cell:
        return [active_cell['row']]
    return []

# === Highlight sorted columns ===
@app.callback(
    Output('data-table', 'style_data_conditional'),
    Input('data-table', 'sort_by')
)
def update_sorted_column_highlight(sort_by):
    style = []
    if sort_by:
        for item in sort_by:
            direction = item.get('direction', 'asc')
            color = '#d1e7dd' if direction == 'asc' else '#f8d7da'
            style.append({
                'if': {'column_id': item['column_id']},
                'backgroundColor': color,
                'fontWeight': 'bold'
            })

    style += [
        {
            'if': {'filter_query': '{Entry_Days} >= 0 && {Entry_Days} <= 5', 'column_id': 'Entry_Days'},
            'color': 'green', 'fontWeight': 'bold'
        },
        {
            'if': {'filter_query': '{Entry2_Days} >= 0 && {Entry2_Days} <= 5', 'column_id': 'Entry2_Days'},
            'color': 'green', 'fontWeight': 'bold'
        },
        {
            'if': {'filter_query': '{Sell_Days} >= 0 && {Sell_Days} <= 5', 'column_id': 'Sell_Days'},
            'color': 'red', 'fontWeight': 'bold'
        }
    ]
    return style


# === Load Pickle on Button Click ===
@app.callback(
    Output('filename-display', 'children'),
    Output('data-table', 'columns'),
    Output('data-table', 'data'),
    Output('strategy-type', 'data'),
    Output('last-loaded-file-key', 'data'),
    Input("load-daily-swing", "n_clicks"),
    Input("load-weekly-swing", "n_clicks"),
    Input("load-daily-positioning", "n_clicks"),
    Input("load-weekly-positioning", "n_clicks"),
)
def load_pickle_from_button(n1, n2, n3, n4):
    global uploaded_df
    triggered_id = ctx.triggered_id
    if not triggered_id:
        return "", [], [], "", ""

    # === Use excl_plot files ===
    FILE_MAP = {
        "load-daily-swing": "/all_daily_swing_excl_plot.pkl",
        "load-weekly-swing": "/all_weekly_swing_excl_plot.pkl",
        "load-daily-positioning": "/all_daily_positioning_excl_plot.pkl",
        "load-weekly-positioning": "/all_weekly_positioning_excl_plot.pkl",
    }

    file_path = FILE_MAP.get(triggered_id)
    if not file_path:
        return "❌ No Dropbox file path configured.", [], [], "", ""

    print(f"Triggered ID: {triggered_id}")
    print(f"Trying to read: {file_path}")

    
    try:
        df = read_pickle_from_dropbox(file_path)
        uploaded_df = df.copy()
    except Exception as e:
        return f"❌ Failed to load Pickle from Dropbox: {e}", [], [], "", ""

    display_df = df.copy()

    # Show all columns
    visible_columns = list(display_df.columns)
    columns = [{"name": col, "id": col} for col in visible_columns]

    strategy_type = 'swing' if 'swing' in triggered_id else 'positioning'
    filename = os.path.basename(file_path)

    return (
        f"✅ Loaded: {filename}",
        columns,
        display_df.to_dict('records'),
        strategy_type,
        triggered_id  # 👈 store which button was pressed
    )

# === Plot Callback ===
@app.callback(
    Output('plot-output', 'children'),
    Input('plot-button', 'n_clicks'),
    State('data-table', 'selected_rows'),
    State('strategy-type', 'data'),
    State('last-loaded-file-key', 'data'),
)
def plot_selected_row(n_clicks, selected_rows, strategy_type, last_loaded_key):
    global uploaded_df
    if not n_clicks or not selected_rows or uploaded_df.empty:
        return html.Div("❗ Select a row to plot after loading data.")

    # --- Get selected ticker ---
    row = uploaded_df.iloc[selected_rows[0]]
    ticker = row.get('Ticker')
    if not ticker:
        return html.Div("❌ Could not find 'Ticker' in selected row.")

    # --- Determine folder based on last_loaded_key ---
    incl_folder_map = {
        "load-daily-swing": "/all_daily_swing_incl_plot/",
        "load-weekly-swing": "/all_weekly_swing_incl_plot/",
        "load-daily-positioning": "/all_daily_positioning_incl_plot/",
        "load-weekly-positioning": "/all_weekly_positioning_incl_plot/",
    }
    
    incl_folder = incl_folder_map.get(last_loaded_key)
    if not incl_folder:
        return html.Div("❌ Could not determine which incl_plot folder to load.")
    
    # --- Build the ticker-specific file path ---
    ticker_file = f"{incl_folder}{ticker}.pkl"
    
    # --- Load ticker pickle from Dropbox ---
    try:
        plot_dict = read_pickle_from_dropbox(ticker_file)  # this returns a DataFrame or dict
    except Exception as e:
        return html.Div(f"❌ Failed to load '{ticker}.pkl' from Dropbox: {e}")
    
    # --- Convert to DataFrame if needed ---
    try:
        if isinstance(plot_dict, pd.DataFrame):
            data = plot_dict.copy()
        else:
            data = pd.DataFrame(plot_dict)
    
        # --- Timeline logic ---
        if 'Date' in data.columns:
            data['Date'] = pd.to_datetime(data['Date'], errors='coerce')
            data = data.dropna(subset=['Date']).sort_values('Date')
            data.set_index('Date', inplace=True)
    
    except Exception as e:
        return html.Div(f"❌ Failed to parse plot_dict for ticker '{ticker}': {e}")

    # Normalize possible signal columns
    for col in ['entry_buy_signal', 'entry_buy_signal2', 'trigger_sell_signal',
                'is_earnings_date', 'is_earnings_warning']:
        if col in data.columns:
            data[col] = data[col].astype(bool)

    # --- Labels ---
    plot_mode = "Swing" if strategy_type == "swing" else "Positioning"
    timeframe_label = "Daily" if "daily" in last_loaded_key else "Weekly"
    timeframe = timeframe_label  # for title text consistency

    subplot_titles = (
        [f"{timeframe_label} {plot_mode} - {ticker}: Candlestick + MA(20/40) + Dynamic SLs",
         f"{timeframe_label} {plot_mode} - {ticker}: CCI (6) + MA(1)"]
        if plot_mode == "Swing"
        else [f"{timeframe_label} {plot_mode} - {ticker}: Candlestick Chart with Signals",
              f"{timeframe_label} {plot_mode} - {ticker}: TIF"]
    )

    
    # === PLOT LOGIC ===
@app.callback(
    Output('plot-output', 'children'),
    Input('plot-button', 'n_clicks'),
    State('data-table', 'selected_rows'),
    State('strategy-type', 'data'),
    State('last-loaded-file-key', 'data'),
)
def plot_selected_row_safe(n_clicks, selected_rows, strategy_type, last_loaded_key):
    global uploaded_df

    if not n_clicks or not selected_rows or uploaded_df.empty:
        return html.Div("❗ Select a row to plot after loading data.")

    # --- Get selected ticker ---
    row = uploaded_df.iloc[selected_rows[0]]
    ticker = row.get('Ticker')
    if not ticker:
        return html.Div("❌ Could not find 'Ticker' in selected row.")

    # --- Determine incl_plot folder ---
    incl_folder_map = {
        "load-daily-swing": "/all_daily_swing_incl_plot/",
        "load-weekly-swing": "/all_weekly_swing_incl_plot/",
        "load-daily-positioning": "/all_daily_positioning_incl_plot/",
        "load-weekly-positioning": "/all_weekly_positioning_incl_plot/",
    }
    incl_folder = incl_folder_map.get(last_loaded_key)
    if not incl_folder:
        return html.Div("❌ Could not determine incl_plot folder.")

    ticker_file = f"{incl_folder}{ticker}.pkl"

    # --- Load ticker pickle ---
    try:
        plot_data = read_pickle_from_dropbox(ticker_file)
    except Exception as e:
        return html.Div(f"❌ Failed to load '{ticker}.pkl': {e}")

    # --- Convert to DataFrame if needed ---
    if isinstance(plot_data, pd.DataFrame):
        data = plot_data.copy()
    elif isinstance(plot_data, dict):
        try:
            data = pd.DataFrame(plot_data)
        except Exception as e:
            return html.Div(f"❌ Failed to convert dict to DataFrame: {e}")
    else:
        return html.Div(f"❌ Unsupported plot data type: {type(plot_data)}")

    # --- Normalize Date index ---
    if 'Date' in data.columns:
        data['Date'] = pd.to_datetime(data['Date'], errors='coerce')
        data = data.dropna(subset=['Date']).sort_values('Date')
        data.set_index('Date', inplace=True)

    # --- Convert optional boolean signals ---
    for col in ['entry_buy_signal', 'entry_buy_signal2', 'trigger_sell_signal',
                'Entry_Buy_Signal', 'Entry_Buy_Signal2', 'Trigger_Sell_Signal',
                'is_earnings_date', 'is_earnings_warning']:
        if col in data.columns:
            data[col] = data[col].astype(bool)

    # --- Labels ---
    plot_mode = "Swing" if strategy_type == "swing" else "Positioning"
    timeframe_label = "Daily" if "daily" in last_loaded_key else "Weekly"

    # --- Subplot titles ---
    if plot_mode == "Swing":
        subplot_titles = [
            f"{timeframe_label} Swing - {ticker}: Candlestick + MA + Dynamic SLs",
            f"{timeframe_label} Swing - {ticker}: CCI + MA"
        ]
        row_heights = [0.7, 0.3]
    else:
        subplot_titles = [
            f"{timeframe_label} Positioning - {ticker}: Candlestick + Signals",
            f"{timeframe_label} Positioning - {ticker}: TIF"
        ]
        row_heights = [0.5, 0.3]

    fig = make_subplots(
        rows=2, cols=1, shared_xaxes=True,
        vertical_spacing=0.1, row_heights=row_heights,
        subplot_titles=subplot_titles
    )

    # --- Candlestick (always present) ---
    if all(c in data.columns for c in ['Open', 'High', 'Low', 'Close']):
        fig.add_trace(go.Candlestick(
            x=data.index,
            open=data['Open'],
            high=data['High'],
            low=data['Low'],
            close=data['Close'],
            name='Candlestick',
            increasing_line_color='grey',
            decreasing_line_color='black'
        ), row=1, col=1)
    else:
        return html.Div("❌ Missing OHLC columns for candlestick plot.")

    # --- Swing branch ---
    if plot_mode == "Swing":
        # MA lines
        for ma_col, color in [('MA20', 'red'), ('MA40', 'blue')]:
            if ma_col in data.columns:
                fig.add_trace(go.Scatter(
                    x=data.index, y=data[ma_col], mode='lines',
                    name=ma_col, line=dict(color=color, width=1.5)
                ), row=1, col=1)

        # Dynamic SLs
        sl_cols = {
            'Dyn_SL_1x_Lower': 'SL 1x Lower',
            'Dyn_SL_2x_Lower': 'SL 2x Lower',
            'Dyn_SL_1x_Upper': 'SL 1x Upper',
            'Dyn_SL_2x_Upper': 'SL 2x Upper',
            'Dyn_Trail_SL_1x': 'Trailing SL 1x',
            'Dyn_Trail_SL_2x': 'Trailing SL 2x'
        }
        for col, name in sl_cols.items():
            if col in data.columns:
                fig.add_trace(go.Scatter(
                    x=data.index, y=data[col], mode='lines',
                    name=name, line=dict(color='grey', width=1),
                    visible='legendonly'
                ), row=1, col=1)

        # Entry / Sell Signals
        signal_cols = [
            ('Entry_Buy_Signal', 'Entry_Buy_Price', 'green'),
            ('Entry_Buy_Signal2', 'Entry_Buy_Price2', 'purple'),
            ('Trigger_Sell_Signal', 'Trigger_Sell_Price', 'red')
        ]
        for sig_col, price_col, color in signal_cols:
            if sig_col in data.columns and price_col in data.columns and data[sig_col].any():
                fig.add_trace(go.Scatter(
                    x=data.index[data[sig_col]],
                    y=data[price_col][data[sig_col]],
                    mode='markers',
                    marker=dict(symbol='triangle-up' if 'Entry' in sig_col else 'triangle-down', color=color, size=10),
                    name=sig_col
                ), row=1, col=1)

        # CCI
        for col, color, visible in [('CCI', 'blue', True), ('CCI_MA', 'orange', 'legendonly')]:
            if col in data.columns:
                fig.add_trace(go.Scatter(
                    x=data.index, y=data[col], mode='lines',
                    line=dict(color=color, dash='dot' if col.endswith('MA') else None),
                    name=col,
                    visible=visible
                ), row=2, col=1)

        # Reference lines
        fig.add_hline(y=100, line_dash='dash', line_color='green', row=2, col=1)
        fig.add_hline(y=0, line_color='black', row=2, col=1)
        fig.add_hline(y=-100, line_dash='dash', line_color='red', row=2, col=1)

        # Earnings markers
        for col, sym, mult, name in [('is_earnings_date', 'star', 1.01, 'Earnings'),
                                     ('is_earnings_warning', 'diamond', 1.02, 'Earnings Ahead')]:
            if col in data.columns and data[col].any() and 'High' in data.columns:
                fig.add_trace(go.Scatter(
                    x=data.index[data[col]],
                    y=data['High'][data[col]] * mult,
                    mode='markers+text',
                    text=['E' if sym=='star' else '⚠️'] * data[col].sum(),
                    textposition='top center',
                    marker=dict(symbol=sym, size=12, color='purple' if sym=='star' else 'orange'),
                    name=name
                ), row=1, col=1)

    # --- Positioning branch ---
    else:
        # Plot Buy/Sell context candles safely
        for signal_type, color, label in [('buy', 'blue', 'Buy Context'), ('sell', 'red', 'Sell Context')]:
            mask = (data.get('signal_type') == signal_type) if 'signal_type' in data.columns else pd.Series(False, index=data.index)
            if mask.any() and all(c in data.columns for c in ['Open', 'High', 'Low', 'Close']):
                fig.add_trace(go.Candlestick(
                    x=data.index[mask],
                    open=data.loc[mask, 'Open'],
                    high=data.loc[mask, 'High'],
                    low=data.loc[mask, 'Low'],
                    close=data.loc[mask, 'Close'],
                    increasing_line_color=color,
                    decreasing_line_color=color,
                    name=label
                ), row=1, col=1)

        # SMA
        if 'SMA' in data.columns:
            fig.add_trace(go.Scatter(
                x=data.index, y=data['SMA'], mode='lines',
                line=dict(color='orange', width=1), name='SMA'
            ), row=1, col=1)

        # TIF subplot
        if 'TIF' in data.columns:
            fig.add_trace(go.Scatter(
                x=data.index, y=data['TIF'], mode='lines',
                line=dict(color='green', width=1), name='TIF'
            ), row=2, col=1)

    # --- Layout tweaks ---
    fig.update_layout(
        height=700, width=1000,
        title_text=f"{plot_mode} Plot for {ticker}",
        xaxis_rangeslider_visible=False,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    return dcc.Graph(figure=fig)


# === Run App ===
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get("PORT", 8050)))
