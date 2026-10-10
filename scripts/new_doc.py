"""Create a new documentary project from the template.

usage: new_doc.py <project_dir> [--name slug] [--title-en "..."] [--title-km "..."] [--no-geo] [--example funan]

Copies engine/ into the project (so every film is self-contained and can be patched freely), adds the template
(narration.py, script_src.py, make.py, project.json, docs/, archive/), links .venv to the skill's render
environment, and downloads map data.  --example funan starts from the full Funan film instead of the sample."""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys

SK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("project")
    ap.add_argument("--name")
    ap.add_argument("--title-en")
    ap.add_argument("--title-km")
    ap.add_argument("--no-geo", action="store_true")
    ap.add_argument("--example", choices=["funan"])
    a = ap.parse_args()
    dst = os.path.abspath(os.path.expanduser(a.project))
    if os.path.exists(os.path.join(dst, "script_src.py")):
        sys.exit("%s already has a script_src.py: not overwriting" % dst)
    os.makedirs(dst, exist_ok=True)
    ign = shutil.ignore_patterns("__pycache__", "*.pyc", ".DS_Store")
    shutil.copytree(os.path.join(SK, "engine"), os.path.join(dst, "engine"), ignore=ign, dirs_exist_ok=True)
    shutil.copytree(os.path.join(SK, "template"), dst, ignore=ign, dirs_exist_ok=True)
    if a.example:
        ex = os.path.join(SK, "examples", a.example)
        for f in ("narration.py", "script_src.py"):
            shutil.copy(os.path.join(ex, f), os.path.join(dst, f))
        shutil.copytree(os.path.join(ex, "docs"), os.path.join(dst, "docs"), dirs_exist_ok=True)
        shutil.copy(os.path.join(ex, "archive", "manifest.json"), os.path.join(dst, "archive", "manifest.json"))
    for d in ("audio/voices", "audio/narr", "build", "film", "subtitles", "source", "archive/img", "geo"):
        os.makedirs(os.path.join(dst, d), exist_ok=True)

    pj = os.path.join(dst, "project.json")
    p = json.load(open(pj))
    name = a.name or re.sub(r"[^a-z0-9]+", "_", os.path.basename(dst).lower()).strip("_")
    p.update(name=name)
    if a.example == "funan":
        p.update(name=a.name or "funan_kingdom_of_the_mountain", title_km="ហ្វូណន · នគរភ្នំ",
                 title_en="Funan – Kingdom of the Mountain", end_target=900)
    if a.title_en:
        p["title_en"] = a.title_en
    if a.title_km:
        p["title_km"] = a.title_km
    json.dump(p, open(pj, "w"), ensure_ascii=False, indent=2)

    venv = os.path.join(dst, ".venv")
    if not os.path.exists(venv) and os.path.isdir(os.path.join(SK, ".venv")):
        os.symlink(os.path.join(SK, ".venv"), venv)
    py = os.path.join(venv, "bin", "python")
    if not a.no_geo:
        subprocess.run([py if os.path.exists(py) else sys.executable, os.path.join(SK, "scripts", "fetch_geo.py"), dst],
                       check=True)
    print("project ready: %s\n  cd %s && .venv/bin/python make.py info" % (dst, dst))


if __name__ == "__main__":
    main()
