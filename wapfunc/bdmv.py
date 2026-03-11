import os
import re
import subprocess

from pathlib import Path

from pyparsebluray import mpls

__all__ = ['m2ts_from_playlist', 'm2ts_from_playlists', 'locate_playlist']
    
def m2ts_from_playlist(
        playlist_file: os.PathLike,
        exclude_first: bool = False,
        exclude_last: bool = True
) -> list[Path]:
    playlist_path = Path(playlist_file)
    if not playlist_path.exists():
        raise Exception("Playlist file not found!")
    if playlist_path.suffix.lower() != ".mpls":
        raise Exception("Did not pass BDMV playlist file!")
    playlist_dir = playlist_path.parent
    stream_dir = Path(os.path.join(playlist_dir.parent, "STREAM"))
    if playlist_dir.name.lower() != "playlist" or not stream_dir.exists():
        raise Exception("Incorrect BDMV structure!")
    
    with playlist_path.open("rb") as pf:
        playlist = mpls.load_playlist(pf)
        if not playlist.play_items:
            return None
    m2ts_paths = []
    for i, playitem in enumerate(playlist.play_items):
        if not playitem.clip_information_filename:
            continue
        if i == 0 and exclude_first:
            continue
        if i == len(playlist.play_items) - 1 and exclude_last:
            continue
        m2ts_path = Path(os.path.join(stream_dir, playitem.clip_information_filename))
        m2ts_paths.append(m2ts_path)
    return m2ts_paths

def m2ts_from_playlists(
        playlist_files: list[os.PathLike],
        exclude_first: bool = False,
        exclude_last: bool = True
) -> list[Path]:
    m2ts_paths = []
    for playlist_file in playlist_files:
        from_playlist = m2ts_from_playlist(playlist_file, exclude_first, exclude_last)
        m2ts_paths.extend(from_playlist)
    return m2ts_paths

# ===Legacy code===
# TODO: clean up/replace unreliable legacy functions

def locate_playlist(
        bdmv_dir: str,
        count: int,
        exclude_first: bool = False,
        exclude_last: bool = True
) -> Path:
    command = [
        'eac3to', bdmv_dir
    ]

    result = subprocess.run(command, capture_output=True, text=True)
    lines = result.stdout.split('\n')
    potential = []
    for m in re.findall(r"\d+\.mpls", result.stdout):
        for line in lines:
            if m in line:
                potential.append(line)

    playlist_file = ""

    for playlist_data in potential:
        episode_list = re.findall(r"\d+\.m2ts", playlist_data)
        if len(episode_list) == 0:
            break
        true_length = len(episode_list)

        if exclude_first:
            episode_list.pop(0)
            true_length -= 1
        if exclude_last:
            episode_list.pop()
            true_length -= 1

        if len(episode_list) == count:
            playlist_file = os.path.join(bdmv_dir, 'PLAYLIST', re.search(r"\d+\.mpls", playlist_data).group())
            break

    if not playlist_file:
        for p in re.findall(r"\[([0-9\+]+)\]\.m2ts", result.stdout):
            episode_list = [f"000{int(ep):02d}.m2ts" for ep in p.split("+")]
            true_length = len(episode_list)

            if exclude_first:
                episode_list.pop(0)
                true_length -= 1
            if exclude_last:
                episode_list.pop()
                true_length -= 1

            if true_length == count:
                for i, line in enumerate(lines):
                    if p in line:
                        break

                playlist_file = os.path.join(bdmv_dir, 'PLAYLIST', re.search(r"\d+\.mpls", lines[i-1]).group())
                break
    
    return Path(playlist_file)
