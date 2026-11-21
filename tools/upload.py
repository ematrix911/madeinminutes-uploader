"""Upload a video to a connected YouTube channel.

  python tools/upload.py --channel main --file output/x/01-clip.mp4 \
      --title "Claude Code built this in 60s" --description "..." --tags ai,coding \
      --privacy private --publish-at 2026-11-25T15:00:00Z --short

Notes:
- --publish-at schedules a public release (the video stays private until then).
- Until the Google Cloud project passes YouTube's API audit, every API upload is
  locked to PRIVATE by YouTube regardless of these settings.
- Each upload costs ~1,600 of the default 10,000 daily API quota (about 6/day).
"""
import argparse
from common import get_youtube


def upload(a):
    from googleapiclient.http import MediaFileUpload

    title = a.title
    if a.short and "#shorts" not in title.lower() and len(title) <= 90:
        title += " #shorts"
    body = {
        "snippet": {
            "title": title[:100],
            "description": a.description,
            "tags": [t.strip() for t in a.tags.split(",") if t.strip()],
            "categoryId": a.category,
        },
        "status": {
            "privacyStatus": "private" if a.publish_at else a.privacy,
            "selfDeclaredMadeForKids": False,
        },
    }
    if a.publish_at:
        body["status"]["publishAt"] = a.publish_at
    if a.synthetic:
        body["status"]["containsSyntheticMedia"] = True

    yt = get_youtube(a.channel)
    media = MediaFileUpload(a.file, chunksize=8 * 1024 * 1024, resumable=True)
    req = yt.videos().insert(part="snippet,status", body=body, media_body=media)
    resp = None
    while resp is None:
        status, resp = req.next_chunk()
        if status:
            print(f"  {int(status.progress() * 100)}%")
    print(f"Uploaded: https://youtu.be/{resp['id']}  status={resp['status']['privacyStatus']}")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--channel", required=True)
    p.add_argument("--file", required=True)
    p.add_argument("--title", required=True)
    p.add_argument("--description", default="")
    p.add_argument("--tags", default="")
    p.add_argument("--category", default="28", help="28 = Science & Technology, 27 = Education")
    p.add_argument("--privacy", default="private", choices=["private", "unlisted", "public"])
    p.add_argument("--publish-at", help="ISO 8601 UTC time, e.g. 2026-11-25T15:00:00Z")
    p.add_argument("--short", action="store_true", help="append #shorts to the title")
    p.add_argument("--synthetic", action="store_true",
                   help="declare realistic AI-generated/altered content (e.g. AI voice clone)")
    upload(p.parse_args())
