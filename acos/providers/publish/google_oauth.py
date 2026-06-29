"""Google OAuth yardimcisi — refresh token'dan access token uretir.

Hem YouTube yukleme hem de YouTube analytics ayni mekanizmayi paylasir.
Gerekli kimlikler (kanal bazli olabilir):
  YT_CLIENT_ID, YT_CLIENT_SECRET, YT_REFRESH_TOKEN
"""
from ...credentials import require
from ...errors import PublishError
from ...logging_utils import get_logger
from ...retry import retry

log = get_logger("google.oauth")
TOKEN_URL = "https://oauth2.googleapis.com/token"


@retry(times=3, base_delay=2.0, exceptions=(PublishError,))
def access_token(channel: str = "") -> str:
    import requests  # lazy

    data = {
        "client_id": require("YT_CLIENT_ID", channel),
        "client_secret": require("YT_CLIENT_SECRET", channel),
        "refresh_token": require("YT_REFRESH_TOKEN", channel),
        "grant_type": "refresh_token",
    }
    r = requests.post(TOKEN_URL, data=data, timeout=30)
    if r.status_code != 200:
        raise PublishError(f"Google token yenileme hatasi {r.status_code}: {r.text[:200]}")
    return r.json()["access_token"]
