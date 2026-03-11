"""
Basic mux script. Customize as necessary.
"""
import os
from pathlib import Path

from vsmuxtools import Setup, Chapters, GlobSearch, SubFile, VideoFile, src_file, mux
from wapfunc import handle_audio, create_signs_track, restyle_dialogue

episode = 1
src = r"somefile.m2ts"

setup = Setup(f"{episode:02d}")
src_dir = Path(setup.config_file).parent
ep_dir = Path(os.path.join(src_dir, f"{episode:02d}"))

video_track = VideoFile(src).to_track(lang="und", args=["--no-global-tags", "--no-date"])

jp_audio = handle_audio(src, 0)
en_audio = handle_audio(GlobSearch(f"*E{episode:02d}*.mkv", dir=ep_dir, recursive=False), 1, delay=1000)

base_subs_path = GlobSearch(f"*E{episode:02d}*.ass", dir=ep_dir, recursive=False)
base_subs = SubFile(base_subs_path).clean_garbage().clean_styles().shift(24).shift_0()
full_subs = restyle_dialogue(base_subs).to_track("Full Subtitles")
signs_and_songs = create_signs_track(base_subs).to_track("Signs and Songs", default=False, forced=True)

chapters = Chapters(src_file(src)).set_names(["Intro", "OP", "Part A", "Part B", "ED", "Preview"])

fonts = full_subs.collect_fonts(additional_fonts=[os.path.join(ep_dir, "attachments")])

mux(
    video_track,
    *jp_audio,
    *en_audio,
    full_subs,
    signs_and_songs,
    chapters,
    *fonts
)