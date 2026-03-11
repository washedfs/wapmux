from os import PathLike
from datetime import timedelta

from muxtools import SubFile, edit_style, get_complimenting_styles, DEFAULT_DIALOGUE_STYLES, gandhi_default
from ass import Dialogue, Comment

__all__ = ['create_signs_track', 'restyle_dialogue', 'set_layoutres', 'add_line', 'add_syncpoint']

def create_signs_track(
        sub_file: SubFile,
        dialogue_styles: list[str] | None = DEFAULT_DIALOGUE_STYLES
) -> SubFile:
    return sub_file.copy().separate_signs(dialogue_styles)

def restyle_dialogue(
        sub_file: SubFile,
        dialogue_styles: list[str] | None = ["main", "default", "narrator", "narration", "bottomcenter"],
        top_styles: list[str] | None = ["top"],
        italics_styles: list[str] | None = ["italics", "internal"],
        alt_styles: list[str] | None = None
) -> SubFile:
    gjm_main = edit_style(gandhi_default, "Default", margin_l=225, margin_r=225, margin_v=60)
    gjm_overlap = get_complimenting_styles(gjm_main)[1]
    sub_file.unfuck_cr(keep_flashback=False, dialogue_styles=dialogue_styles, top_styles=top_styles, italics_styles=italics_styles, alt_styles=alt_styles).restyle([gjm_main, gjm_overlap])
    return sub_file

def set_layoutres(sub_file: SubFile) -> SubFile:
    doc = sub_file._read_doc()
    playresx = doc.info.get("PlayResX")
    playresy = doc.info.get("PlayResY")
    layoutresx = doc.info.get("LayoutResX")
    layoutresy = doc.info.get("LayoutResY")

    if layoutresx is None:
        sub_file.set_header("LayoutResX", playresx)
    if layoutresy is None:
        sub_file.set_header("LayoutResY", playresy)

    return sub_file

def add_line(
        sub_file: SubFile,
        line: Dialogue,
        line_num: int = 0
) -> SubFile:
    sub_file.manipulate_lines(lambda lines: lines.insert(line, line_num-1) if line_num != 0 else lines.append(line))
    return sub_file

def add_syncpoint(
        sub_file: SubFile,
        sync_name: str,
        frame_num: int,
        fps: float = 24000/1001
) -> SubFile:
    sync_line = Comment(start=timedelta(seconds=frame_num/fps), end=timedelta(seconds=frame_num/fps), effect=sync_name, text="{SYNC}")
    sub_file.manipulate_lines(lambda lines: lines.insert(0, sync_line))
    return sub_file

def snap_to_keyframes(
        sub_file: SubFile,
        keyframes_file: PathLike
) -> SubFile:
    return sub_file