"""Shared paths and helpers for the YouTube automation tools."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SECRETS = ROOT / "secrets"
TOKENS = SECRETS / "tokens"
CLIENT_SECRET = SECRETS / "client_secret.json"
OUTPUT = ROOT / "output"

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.readonly",
]


def ffmpeg_exe() -> str:
    """ffmpeg bundled with imageio-ffmpeg (the system install is blocked by policy here)."""
    import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()


def get_youtube(channel: str):
    """Return an authorized YouTube API client for a saved channel token."""
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build

    token_file = TOKENS / f"{channel}.json"
    if not token_file.exists():
        raise SystemExit(f"No token for '{channel}'. Run: python tools/auth.py --channel {channel}")
    creds = Credentials.from_authorized_user_file(str(token_file), SCOPES)
    if not creds.valid:
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            token_file.write_text(creds.to_json())
        else:
            raise SystemExit(f"Token for '{channel}' is invalid. Re-run auth.py --channel {channel}")
    return build("youtube", "v3", credentials=creds)
