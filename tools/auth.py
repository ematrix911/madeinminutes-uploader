"""Sign in to a YouTube channel once and save its token locally.

Usage:
  python tools/auth.py --channel main     # opens browser; pick the channel to connect
  python tools/auth.py --list             # show connected channels and their stats

Each Google account can own several channels (brand accounts). Google asks which
channel to use during sign-in, so run this once per channel with a different --channel name.
"""
import argparse
from common import CLIENT_SECRET, TOKENS, SCOPES, get_youtube


def connect(name: str):
    from google_auth_oauthlib.flow import InstalledAppFlow

    if not CLIENT_SECRET.exists():
        raise SystemExit(f"Missing {CLIENT_SECRET}. See SETUP in README.md.")
    flow = InstalledAppFlow.from_client_secrets_file(str(CLIENT_SECRET), SCOPES)
    creds = flow.run_local_server(port=0, prompt="consent", access_type="offline")
    TOKENS.mkdir(parents=True, exist_ok=True)
    (TOKENS / f"{name}.json").write_text(creds.to_json())
    show(name)


def show(name: str):
    yt = get_youtube(name)
    res = yt.channels().list(part="snippet,statistics", mine=True).execute()
    for ch in res.get("items", []):
        s = ch["statistics"]
        print(f"[{name}] {ch['snippet']['title']}  id={ch['id']}  "
              f"subs={s.get('subscriberCount', '?')}  videos={s.get('videoCount')}  views={s.get('viewCount')}")
    if not res.get("items"):
        print(f"[{name}] signed in, but this Google identity has no YouTube channel.")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--channel", help="short local name for the channel, e.g. main")
    p.add_argument("--list", action="store_true")
    a = p.parse_args()
    if a.list:
        for f in sorted(TOKENS.glob("*.json")):
            show(f.stem)
    elif a.channel:
        connect(a.channel)
    else:
        p.print_help()
