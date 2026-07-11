#!/usr/bin/env python3
"""Verify profile repository safety, privacy, and required artifacts."""
from __future__ import annotations
from pathlib import Path
import sys
import xml.etree.ElementTree as ET

REQUIRED_FILES=("README.md","avi-ascii.svg","info-card.svg","contrib-heatmap.svg","data/contributions.json")
FORBIDDEN_NAMES=("source-photo.jpg","source-photo.jpeg","source-photo.png","source-prepped.png",".env","id_rsa","id_ed25519")
README_FORBIDDEN_TEXT=("YOUR_NAME","YOURHANDLE","yoursite.com","Avi Vashishta")

def verify_svg(path: Path) -> list[str]:
    errors=[]
    try: root=ET.fromstring(path.read_text(encoding="utf-8"))
    except ET.ParseError as exc: return [f"{path}: invalid XML: {exc}"]
    for element in root.iter():
        local_tag=element.tag.split("}")[-1].lower()
        if local_tag=="script": errors.append(f"{path}: script elements are forbidden")
        if local_tag=="foreignobject": errors.append(f"{path}: foreignObject is forbidden")
        for attribute,value in element.attrib.items():
            local_attribute=attribute.split("}")[-1].lower()
            if local_attribute.startswith("on"):
                errors.append(f"{path}: event-handler attribute {attribute} is forbidden")
            if local_attribute in {"href","src"} and value.startswith(("http://","https://","//")):
                errors.append(f"{path}: remote href/src is forbidden")
    return errors

def verify_repository(root: Path) -> list[str]:
    errors=[]
    for relative in REQUIRED_FILES:
        if not (root/relative).is_file(): errors.append(f"Missing required file: {relative}")
    for path in root.rglob("*"):
        if path.is_file() and path.name in FORBIDDEN_NAMES:
            errors.append(f"Forbidden private file: {path.relative_to(root)}")
    readme=root/"README.md"
    if readme.is_file():
        text=readme.read_text(encoding="utf-8")
        for forbidden in README_FORBIDDEN_TEXT:
            if forbidden in text: errors.append(f"README.md contains template text: {forbidden}")
    for name in ("avi-ascii.svg","info-card.svg","contrib-heatmap.svg"):
        path=root/name
        if path.is_file(): errors.extend(verify_svg(path))
    return errors

def main() -> int:
    errors=verify_repository(Path.cwd())
    if errors:
        for error in errors: print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("Profile repository verification passed."); return 0
if __name__=="__main__": raise SystemExit(main())
