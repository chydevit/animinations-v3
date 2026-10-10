"""Download map data into <project>/geo/ (cached in the skill's geo_cache/ so later films reuse it).

  Natural Earth (public domain): land, rivers, lakes, countries
  Elevation: AWS terrarium tiles (SRTM-derived) saved as dem_sea.npz (wide view) and dem_delta.npz (close view)

usage: fetch_geo.py <project> [--sea lon0 lat0 lon1 lat1 z] [--local lon0 lat0 lon1 lat1 z]
Defaults cover mainland Southeast Asia (sea) and all of Cambodia + the Mekong delta (local).
maps.py shows dem_delta when the map view is narrower than 9 degrees."""
import argparse
import io
import math
import os
import shutil
import urllib.request
import zipfile

import numpy as np
from PIL import Image

SK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(SK, "geo_cache")
NE = ["10m/physical/ne_10m_land", "10m/physical/ne_10m_rivers_lake_centerlines", "50m/physical/ne_50m_land",
      "50m/physical/ne_50m_lakes", "50m/physical/ne_50m_rivers_lake_centerlines",
      "50m/cultural/ne_50m_admin_0_countries"]
UA = {"User-Agent": "khmer-history-doc/1.0"}


def get(url):
    return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120).read()


def natural_earth():
    for p in NE:
        name = os.path.basename(p)
        d = os.path.join(CACHE, name)
        if os.path.isdir(d):
            continue
        print("  natural earth", name, flush=True)
        zipfile.ZipFile(io.BytesIO(get("https://naciscdn.org/naturalearth/%s.zip" % p))).extractall(d)


def tile_xy(lon, lat, z):
    n = 2 ** z
    x = (lon + 180) / 360 * n
    y = (1 - math.log(math.tan(math.radians(lat)) + 1 / math.cos(math.radians(lat))) / math.pi) / 2 * n
    return x, y


def dem(name, lon0, lat0, lon1, lat1, z):
    out = os.path.join(CACHE, "%s_%g_%g_%g_%g_%d.npz" % (name, lon0, lat0, lon1, lat1, z))
    if not os.path.exists(out):
        x0, y0 = [int(v) for v in tile_xy(lon0, lat1, z)]
        x1, y1 = [int(v) for v in tile_xy(lon1, lat0, z)]
        print("  elevation %s: %d tiles" % (name, (x1 - x0 + 1) * (y1 - y0 + 1)), flush=True)
        rows = []
        for ty in range(y0, y1 + 1):
            row = []
            for tx in range(x0, x1 + 1):
                url = "https://s3.amazonaws.com/elevation-tiles-prod/terrarium/%d/%d/%d.png" % (z, tx, ty)
                im = np.asarray(Image.open(io.BytesIO(get(url))).convert("RGB")).astype(np.float32)
                row.append(im[..., 0] * 256 + im[..., 1] + im[..., 2] / 256 - 32768)
            rows.append(np.hstack(row))
        np.savez_compressed(out, dem=np.vstack(rows).astype(np.float32), z=z, x0=x0, y0=y0)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("project")
    ap.add_argument("--sea", nargs=5, type=float, default=[66.0, -12.0, 126.0, 34.0, 5])
    ap.add_argument("--local", nargs=5, type=float, default=[102.0, 8.4, 108.0, 15.0, 8])
    a = ap.parse_args()
    os.makedirs(CACHE, exist_ok=True)
    geo = os.path.join(os.path.abspath(a.project), "geo")
    os.makedirs(geo, exist_ok=True)
    natural_earth()
    for p in NE:
        n = os.path.basename(p)
        if not os.path.isdir(os.path.join(geo, n)):
            shutil.copytree(os.path.join(CACHE, n), os.path.join(geo, n))
    for name, box in (("dem_sea", a.sea), ("dem_delta", a.local)):
        shutil.copy(dem(name, *box[:4], int(box[4])), os.path.join(geo, name + ".npz"))
    for name in ("dem_sea", "dem_delta"):   # paper-terrain renders cached by maps.py
        p = os.path.join(a.project, "build", "cache", "paper_%s.png" % name)
        if os.path.exists(p):
            os.remove(p)
    print("geo ready:", geo)


if __name__ == "__main__":
    main()
