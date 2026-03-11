"""
Organizes sources for remuxing. Assumes default AnimeTosho batch structure for subs.
"""
import os
import re
import shutil

from pathlib import Path

tosho_dir = r"somedir"
src_dirs = [r"somedirwithmkvs"]
skip_rename = False

tosho_dir = Path(tosho_dir)
if not skip_rename:
    for item in tosho_dir.iterdir():
        if item.is_dir():
            ep_str = re.search(r'S\d\dE(\d\d)', item.name).group(1)
            item.rename(ep_str)

for src_dir in src_dirs:
    src_dir = Path(src_dir)
    for item in src_dir.iterdir():
        if item.is_file() and item.suffix.lower() == ".mkv":
            ep_str = re.search(r'S\d\dE(\d\d)', item.name).group(1)
            shutil.move(item, os.path.join(tosho_dir, ep_str))