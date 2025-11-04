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
        plot_dict = read_pickle_from_dropbox(ticker_file)
    except Exception as e:
        return html.Div(f"❌ Failed to load '{ticker}.pkl' from Dropbox: {e}")
    
    # --- Convert plot_dict to DataFrame ---
    try:
        if isinstance(plot_dict, str):
            plot_dict = json.loads(plot_dict)
        elif not isinstance(plot_dict, dict):
            return html.Div("❌ 'plot_dict' is not a valid dictionary.")
    
        data = pd.DataFrame(plot_dict)
    
        # --- Timeline logic (keep this!) ---
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
    if strategy_type == 'swing':
        # --- Plot for Swing Strategies ---
        fig = make_subplots(
            rows=2, cols=1, shared_xaxes=True,
            vertical_spacing=0.1, row_heights=[0.7, 0.3],
            subplot_titles=subplot_titles
        )

        # --- Candlestick ---
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

        # --- MA lines ---
        if 'MA20' in data.columns:
            fig.add_trace(go.Scatter(
                x=data.index, y=data['MA20'], mode='lines',
                name='MA 20', line=dict(color='red', width=1.5)
            ), row=1, col=1)

        if 'MA40' in data.columns:
            fig.add_trace(go.Scatter(
                x=data.index, y=data['MA40'], mode='lines',
                name='MA 40', line=dict(color='blue', width=1.5)
            ), row=1, col=1)

        # --- Dynamic SLs ---
        sl_lines = {
            'SL 1x Lower': 'Dyn_SL_1x_Lower',
            'SL 2x Lower': 'Dyn_SL_2x_Lower',
            'SL 1x Upper': 'Dyn_SL_1x_Upper',
            'SL 2x Upper': 'Dyn_SL_2x_Upper',
            'Trailing SL 1x': 'Dyn_Trail_SL_1x',
            'Trailing SL 2x': 'Dyn_Trail_SL_2x'
        }

        for name, col in sl_lines.items():
            if col in data.columns:
                fig.add_trace(go.Scatter(
                    x=data.index, y=data[col], mode='lines',
                    name=name, line=dict(color='grey', width=1),
                    visible='legendonly'
                ), row=1, col=1)

        # --- Entry Signals ---
        entry_signals = {
            'Entry_Buy_Signal': ('Entry_Buy_Price', 'green'),
            'Entry_Buy_Signal2': ('Entry_Buy_Price2', 'purple')
        }
        for name, (price_col, color) in entry_signals.items():
            if price_col in data.columns and name in data.columns:
                fig.add_trace(go.Scatter(
                    x=data.index[data[name]],
                    y=data[price_col][data[name]],
                    mode='markers',
                    marker=dict(symbol='triangle-up', color=color, size=10),
                    name=name
                ), row=1, col=1)

        # --- Trigger Sell Signal ---
        if 'Trigger_Sell_Signal' in data.columns and 'Trigger_Sell_Price' in data.columns:
            fig.add_trace(go.Scatter(
                x=data.index[data['Trigger_Sell_Signal']],
                y=data['Trigger_Sell_Price'][data['Trigger_Sell_Signal']],
                mode='markers',
                marker=dict(symbol='triangle-down', color='red', size=10),
                name='Trigger_Sell_Signal'
            ), row=1, col=1)

        # --- CCI ---
        if 'CCI' in data.columns:
            fig.add_trace(go.Scatter(
                x=data.index, y=data['CCI'], mode='lines',
                name='CCI (6)', line=dict(color='blue')
            ), row=2, col=1)

        if 'CCI_MA' in data.columns:
            fig.add_trace(go.Scatter(
                x=data.index, y=data['CCI_MA'], mode='lines',
                name='CCI MA (1)', line=dict(color='orange', dash='dot'),
                visible='legendonly'
            ), row=2, col=1)

        # --- Reference Lines ---
        fig.add_hline(y=100, line_dash='dash', line_color='green', row=2, col=1)
        fig.add_hline(y=0, line_color='black', row=2, col=1)
        fig.add_hline(y=-100, line_dash='dash', line_color='red', row=2, col=1)

        # --- Earnings ---
        if 'is_earnings_date' in data.columns:
            fig.add_trace(go.Scatter(
                x=data.index[data['is_earnings_date']],
                y=data['High'][data['is_earnings_date']] * 1.01,
                mode='markers+text',
                name='Earnings',
                text=['E'] * data['is_earnings_date'].sum(),
                textposition='top center',
                marker=dict(symbol='star', size=12, color='purple')
            ), row=1, col=1)

        if 'is_earnings_warning' in data.columns:
            fig.add_trace(go.Scatter(
                x=data.index[data['is_earnings_warning']],
                y=data['High'][data['is_earnings_warning']] * 1.02,
                mode='markers+text',
                name='Earnings Ahead',
                text=['⚠️'] * data['is_earnings_warning'].sum(),
                textposition='top center',
                marker=dict(symbol='diamond', size=10, color='orange')
            ), row=1, col=1)

        # --- Layout ---
        fig.update_layout(
            height=750, width=1000,
            title_text=f"📊 {timeframe} {plot_mode} Strategy — {ticker}",
            xaxis_rangeslider_visible=False,
            template='plotly_white',
        )

    else:
        # --- Positioning Plot ---
        fig = make_subplots(
            rows=2, cols=1, shared_xaxes=True,
            vertical_spacing=0.1, row_heights=[0.5, 0.3],
            subplot_titles=subplot_titles
        )

        # --- Context Candles ---
        fig.add_trace(go.Candlestick(
            x=data[data['signal_type'] == 'buy'].index,
            open=data[data['signal_type'] == 'buy']['Open'],
            high=data[data['signal_type'] == 'buy']['High'],
            low=data[data['signal_type'] == 'buy']['Low'],
            close=data[data['signal_type'] == 'buy']['Close'],
            increasing_line_color='blue',
            decreasing_line_color='blue',
            name='Buy Context'
        ), row=1, col=1)

        fig.add_trace(go.Candlestick(
            x=data[data['signal_type'] == 'sell'].index,
            open=data[data['signal_type'] == 'sell']['Open'],
            high=data[data['signal_type'] == 'sell']['High'],
            low=data[data['signal_type'] == 'sell']['Low'],
            close=data[data['signal_type'] == 'sell']['Close'],
            increasing_line_color='red',
            decreasing_line_color='red',
            name='Sell Context'
        ), row=1, col=1)

        # --- SMA ---
        if 'SMA' in data.columns:
            fig.add_trace(go.Scatter(
                x=data.index, y=data['SMA'], mode='lines',
                line=dict(color='orange', width=1), name='SMA 40'
            ), row=1, col=1)

        # --- Entry / Sell Signals ---
        if 'entry_buy_signal' in data.columns:
            fig.add_trace(go.Scatter(
                x=data.index[data['entry_buy_signal']],
                y=data['Low'][data['entry_buy_signal']] * 0.995,
                mode='markers',
                marker=dict(color='green', size=10, symbol='triangle-up'),
                name='Entry Buy Signal'
            ), row=1, col=1)

        if 'entry_buy_signal2' in data.columns:
            fig.add_trace(go.Scatter(
                x=data.index[data['entry_buy_signal2']],
                y=data['Low'][data['entry_buy_signal2']] * 0.995,
                mode='markers',
                marker=dict(color='purple', size=10, symbol='triangle-up'),
                name='Entry Buy Signal 2'
            ), row=1, col=1)

        if 'trigger_sell_signal' in data.columns:
            fig.add_trace(go.Scatter(
                x=data.index[data['trigger_sell_signal']],
                y=data['High'][data['trigger_sell_signal']] * 1.005,
                mode='markers',
                marker=dict(color='red', size=10, symbol='triangle-down'),
                name='Trigger Sell Signal'
            ), row=1, col=1)

        # --- TIF ---
        if 'TIF' in data.columns and 'TIF_color' in data.columns:
            fig.add_trace(go.Bar(
                x=data.index, y=data['TIF'], marker_color=data['TIF_color'], name='TIF'
            ), row=2, col=1)

        # --- Earnings ---
        if 'is_earnings_date' in data.columns:
            fig.add_trace(go.Scatter(
                x=data.index[data['is_earnings_date']],
                y=data['High'][data['is_earnings_date']] * 1.01,
                mode='markers+text',
                name='Earnings',
                text=['E'] * data['is_earnings_date'].sum(),
                textposition='top center',
                marker=dict(symbol='star', size=12, color='purple')
            ), row=1, col=1)

        if 'is_earnings_warning' in data.columns:
            fig.add_trace(go.Scatter(
                x=data.index[data['is_earnings_warning']],
                y=data['High'][data['is_earnings_warning']] * 1.02,
                mode='markers+text',
                name='Earnings Ahead',
                text=['⚠️'] * data['is_earnings_warning'].sum(),
                textposition='top center',
                marker=dict(symbol='diamond', size=10, color='orange')
            ), row=1, col=1)

        # --- Layout ---
        fig.update_layout(
            height=900,
            title=f"📊 {timeframe} {plot_mode} Strategy — {ticker}",
            xaxis_rangeslider_visible=False,
            template='plotly_white',
        )

    return dcc.Graph(figure=fig)

# === Run App ===
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get("PORT", 8050)))
