# dropbox_utils.py
import os
import io
import dropbox
import pandas as pd

DROPBOX_APP_NAME = "trading_data_plot"

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

def read_pickle_from_dropbox(path: str) -> pd.DataFrame:
    """Download and load a pickle file directly from Dropbox."""
    dbx = get_dropbox_client()
    try:
        _, res = dbx.files_download(path)
        print(f"✅ Successfully downloaded {path} from {DROPBOX_APP_NAME}")
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
    print(f"✅ Successfully uploaded {path} to {DROPBOX_APP_NAME}")
