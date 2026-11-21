# MadeInMinutes Uploader

Private, single-user command-line tool used only by the owner of the
[MadeInMinutes](https://www.youtube.com/channel/UC3sHURsDNkBRSjdfVJxBHWQ) YouTube channel to upload and
schedule the owner's own videos. Uses YouTube API Services.

- Site: https://ematrix911.github.io/madeinminutes-uploader/
- Privacy Policy: https://ematrix911.github.io/madeinminutes-uploader/privacy.html
- Terms of Service: https://ematrix911.github.io/madeinminutes-uploader/terms.html

## Complete upload flow (full, working source in `tools/`)

```
pip install -r requirements.txt
# put the Desktop OAuth client JSON at secrets/client_secret.json (never committed)
python tools/auth.py --channel main        # one-time Google sign-in + consent (youtube.upload, youtube.readonly)
python tools/upload.py --channel main --file video.mp4 --title "My video" \
    --description "..." --tags ai,coding --publish-at 2026-11-25T15:00:00Z
```

| File | Purpose |
|---|---|
| `tools/common.py` | Paths, scopes, loads/refreshes the locally stored OAuth token, builds the API client |
| `tools/auth.py` | OAuth 2.0 installed-app flow; saves the token only on the owner's computer; shows channel stats |
| `tools/upload.py` | Resumable `videos.insert` upload with title/description/tags, privacy, optional `publishAt` scheduling |

API methods used: `videos.insert`, `channels.list`, `playlistItems.list`, `videos.list`.
No data from other users is accessed. Tokens never leave the owner's computer.
