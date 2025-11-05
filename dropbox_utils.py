import os
import io
import dropbox
import pandas as pd
import json
import ast

DROPBOX_APP_NAME = "trading_data_plot"


# === Connection ===
def get_dropbox_client():
    """Initialize a Dropbox client using long-term refresh token authentication."""
    app_key = os.environ.get("DROPBOX_APP_KEY")
    app_secret = os.environ.get("DROPBOX_APP_SECRET")
    refresh_token = os.environ.get("DROPBOX_REFRESH_TOKEN")

    if not all([app_key, app_secret, refresh_token]):
        raise EnvironmentError(
            f"Dropbox credentials not set for {DROPBOX_APP_NAME}. "
            "Please define DROPBOX_APP_KEY, DROPBOX_APP_SECRET, and DROPBOX_REFRESH_TOKEN in environment variables."
        )

    print(f"✅ Initializing Dropbox client for app: {DROPBOX_APP_NAME}")
    return dropbox.Dropbox(
        oauth2_refresh_token=refresh_token,
        app_key=app_key,
        app_secret=app_secret
    )


# === Core helpers ===
def read_pickle_from_dropbox(path: str) -> pd.DataFrame:
    """Download and load a pickle file directly from Dropbox (full path required)."""
    dbx = get_dropbox_client()
    try:
        _, res = dbx.files_download(path)
        print(f"✅ Downloaded {path} from {DROPBOX_APP_NAME}")
        df = pd.read_pickle(io.BytesIO(res.content))
        return df
    except dropbox.exceptions.ApiError as e:
        raise RuntimeError(f"Dropbox API error in {DROPBOX_APP_NAME}: {e}")


def upload_pickle_to_dropbox(df: pd.DataFrame, path: str):
    """Upload a pandas DataFrame as a pickle file to Dropbox."""
    dbx = get_dropbox_client()
    buf = io.BytesIO()
    df.to_pickle(buf)
    buf.seek(0)
    dbx.files_upload(buf.read(), path, mode=dropbox.files.WriteMode("overwrite"))
    print(f"✅ Uploaded {path} to {DROPBOX_APP_NAME}")


# === New convenience functions ===
def list_files_in_dropbox_folder(folder_path: str):
    """
    List all files in a Dropbox folder (e.g. /all_daily_positioning_incl_plot).
    Returns a list of filenames (not full paths).
    """
    dbx = get_dropbox_client()
    try:
        res = dbx.files_list_folder(folder_path)
        files = [entry.name for entry in res.entries if isinstance(entry, dropbox.files.FileMetadata)]
        print(f"📁 Found {len(files)} files in {folder_path}")
        return files
    except dropbox.exceptions.ApiError as e:
        raise RuntimeError(f"Dropbox folder listing failed in {DROPBOX_APP_NAME}: {e}")


def read_ticker_pickle(strategy_folder: str, ticker: str) -> pd.DataFrame:
    """
    Read a single per-ticker pickle from Dropbox.

    Example:
        read_ticker_pickle('/all_daily_positioning_incl_plot', 'AAPL')
    """
    path = f"{strategy_folder}/{ticker}.pkl"
    return read_pickle_from_dropbox(path)


def read_all_tickers_from_folder(strategy_folder: str) -> dict:
    """
    Read all ticker pickle files from a strategy folder into a dictionary.

    Example:
        data_dict = read_all_tickers_from_folder('/all_daily_positioning_incl_plot')
        AAPL_df = data_dict['AAPL']
    """
    tickers_data = {}
    file_names = list_files_in_dropbox_folder(strategy_folder)
    for file_name in file_names:
        if file_name.endswith(".pkl"):
            ticker = file_name.replace(".pkl", "")
            try:
                df = read_ticker_pickle(strategy_folder, ticker)
                tickers_data[ticker] = df
            except Exception as e:
                print(f"⚠️ Failed to load {ticker}: {e}")
    print(f"✅ Loaded {len(tickers_data)} ticker pickles from {strategy_folder}")
    return tickers_data

def read_and_unpack_ticker_pickle(path: str) -> pd.DataFrame:
    """
    Read a single per-ticker pickle from Dropbox and unpack the 'plot_dict' JSON if present.

    Handles these cases:
    1. DataFrame with a 'plot_dict' column (1 row per ticker)
    2. Direct dict (already a JSON-like structure)
    3. DataFrame already containing time series data

    Returns
    -------
    pd.DataFrame
        Cleaned DataFrame ready for plotting (should contain a 'Date' column or datetime index)
    """
    df = read_pickle_from_dropbox(path)

    # --- Case 1: DataFrame with 'plot_dict' column ---
    if isinstance(df, pd.DataFrame) and 'plot_dict' in df.columns:
        try:
            raw_plot_dict = df.loc[0, 'plot_dict']
            if isinstance(raw_plot_dict, str):
                try:
                    plot_data = json.loads(raw_plot_dict)
                except json.JSONDecodeError:
                    # Fallback to ast.literal_eval if JSON fails
                    plot_data = ast.literal_eval(raw_plot_dict)
            elif isinstance(raw_plot_dict, dict):
                plot_data = raw_plot_dict
            else:
                raise TypeError(f"Unexpected plot_dict type: {type(raw_plot_dict)}")

            unpacked_df = pd.DataFrame(plot_data)
            print(f"✅ Unpacked 'plot_dict' from {path} → shape {unpacked_df.shape}")
            return unpacked_df

        except Exception as e:
            raise RuntimeError(f"Failed to unpack 'plot_dict' in {path}: {e}")

    # --- Case 2: Direct dictionary ---
    elif isinstance(df, dict):
        unpacked_df = pd.DataFrame(df)
        print(f"✅ Converted dict pickle from {path} → shape {unpacked_df.shape}")
        return unpacked_df

    # --- Case 3: Already a DataFrame with time series ---
    elif isinstance(df, pd.DataFrame):
        print(f"✅ Loaded time-series DataFrame from {path} → shape {df.shape}")
        return df

    else:
        raise TypeError(f"Unexpected pickle content type: {type(df)}")
