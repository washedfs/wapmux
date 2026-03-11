"""
Experimental functions for handling Aniplus subtitles.
"""
import re

from muxtools import SubFile
from ass import Dialogue

__all__ = ['handle_signs', 'fix_dashes']

def handle_signs(
        sub_file: SubFile
) -> tuple[SubFile, SubFile]:
    def remove_signs(lines):
        new_lines = []
        for line in lines:
            tag_regex = re.compile(r"{.*?}")
            line_text = tag_regex.sub("", line.text)
            new_line = _remove_quoted(line_text)
            for tag in tag_regex.findall(line.text):
                new_line = tag + new_line
            new_lines.append(Dialogue(start=line.start, end=line.end, style=line.style, text=new_line))
        return new_lines

    def remove_dialogue(lines):
        new_lines = []
        for line in lines:
            line_text = re.sub(r"{.*?}", "", line.text)
            new_line = "{\\an8}" + _keep_quoted(line_text).replace('"', "")
            new_lines.append(Dialogue(start=line.start, end=line.end, style=line.style, text=new_line))
        return new_lines
    
    dialogue = sub_file.copy().manipulate_lines(remove_signs)
    signs = sub_file.copy().manipulate_lines(remove_dialogue)

    return dialogue, signs

# currently very unreliable
def fix_dashes(
        sub_file: SubFile,
        honorifics: list[str] = ["san", "kun", "chan", "sensei"]
) -> SubFile:
    def _fix_dashes(lines):
        for line in lines:
            for honorific in honorifics:
                line.text = line.text.replace("–"+honorific, "-"+honorific)
            line.text = line.text.replace("–", "—")

    sub_file.manipulate_lines(_fix_dashes)
    return sub_file

_REMOVE_QUOTED_RE = re.compile(r'(?<!\w)"([^"]*)"(?:\\N)?')

def _remove_quoted(text: str) -> str:
    def _repl(m: re.Match) -> str:
        content = m.group(1)
        full = m.group(0)
        if content and content[-1] in '.!,?:;':
            return full
        if full.endswith('\\N') or m.end() == len(text):
            return ''
        return full

    return _REMOVE_QUOTED_RE.sub(_repl, text)

_KEEP_QUOTED_RE = re.compile(r'(?<!\w)("([^\"]*[^\.!,\?:;\s])")(?=\\N|\Z)')

def _keep_quoted(text: str) -> str:
        matches = [m.group(1) for m in _KEEP_QUOTED_RE.finditer(text)]
        return ''.join(matches)