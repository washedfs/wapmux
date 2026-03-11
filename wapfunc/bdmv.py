import os

from pathlib import Path

from pyparsebluray import mpls

__all__ = ['m2ts_from_playlist', 'm2ts_from_playlists']

def m2ts_from_playlist(
        playlist_file: os.PathLike,
        exclude_first: bool = False,
        exclude_last: bool = False
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
        exclude_last: bool = False
):
    m2ts_paths = []
    for playlist_file in playlist_files:
        from_playlist = m2ts_from_playlist(playlist_file, exclude_first, exclude_last)
        m2ts_paths.extend(from_playlist)
    return m2ts_paths