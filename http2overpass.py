from urllib.parse import urlencode
import requests, sys

def get_query(bbox: str):
    q = f"""
        [out:json][timeout:25];
        (
        way["indoor"="room"]({bbox});
        )->.rooms;
        .rooms > ->.nodes;
        .nodes < ->.all;
        .all out meta;
        .all > ->.nodes;
        .nodes out skel qt;
    """.strip().replace('  ', '')
    return q

def download(file: str, bbox: str):
    qstring = {
        "data": get_query(bbox)
    }
    q = urlencode(qstring)
    url = f"https://overpass-api.de/api/interpreter?{q}"
    req = requests.get(url)
    data = req.content
    with open(file, 'wb') as f:
        f.write(data)


if __name__ == "__main__":
    download(sys.argv[1], sys.argv[2])