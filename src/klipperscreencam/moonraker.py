import json
import os
from urllib.parse import urljoin, urlsplit
from urllib.request import Request, urlopen


def normalize(entries, base_url):
    result = []
    for entry in entries:
        if not entry.get("enabled", True) or not entry.get("stream_url"):
            continue
        url = urljoin(base_url.rstrip("/") + "/", entry["stream_url"])
        parsed = urlsplit(url)
        uid = str(entry.get("uid") or entry.get("name", ""))
        if not uid:
            continue
        service = str(entry.get("service", "mjpegstreamer"))
        result.append({
            "uid": uid, "name": str(entry.get("name") or uid), "url": url,
            "supported": (parsed.scheme in ("http", "https")
                          and bool(parsed.hostname)
                          and service in ("mjpegstreamer", "mjpegstreamer-adaptive", "ipstream")),
            "flip_horizontal": bool(entry.get("flip_horizontal", False)),
            "flip_vertical": bool(entry.get("flip_vertical", False)),
            "rotation": int(entry.get("rotation", 0)) % 360,
        })
    return result


def list_cameras(settings):
    headers = {}
    api_key = os.environ.get("MOONRAKER_API_KEY")
    if api_key:
        headers["X-Api-Key"] = api_key
    request = Request(settings.moonraker_url + "/server/webcams/list", headers=headers)
    with urlopen(request, timeout=settings.request_timeout) as response:
        data = json.load(response)
    return normalize(data["result"]["webcams"], settings.web_url)


def startup_camera(cameras, configured):
    if not cameras:
        return None
    return next((camera["uid"] for camera in cameras
                 if camera["uid"] == configured), None) or next(
        (camera["uid"] for camera in cameras if camera["name"] == configured),
        cameras[0]["uid"])
