from os import PathLike
from pathlib import Path

from muxtools import AudioFile, AudioTrack, Eac3to, FFMpeg, FLAC, GlobSearch, ParsedFile, TrackType

__all__ = ['handle_audio']

def handle_audio(
        src_file: PathLike | GlobSearch,
        tracks: int | list[int],
        delay: int | list[int] = 0,
        transcode_all: bool = False,
        commentary_tracks: list[int] = None,
        name_scheme: str = "$language$ $ch$"
) -> list[AudioTrack]:
    if isinstance(src_file, GlobSearch):
        if len(src_file.paths) < 1:
            raise Exception("GlobSearch returned no results!")
        src_path = src_file.paths[0]
    else:
        src_path = Path(src_file)
    if src_path.suffix.lower() != ".mkv" and src_path.suffix.lower() != ".m2ts":
        raise Exception("Unsupported source file format!")
    if src_path.suffix.lower() != ".m2ts" and commentary_tracks is not None:
        raise Exception("Only BDMV source can have commentary tracks!")
    
    track_list = []
    if isinstance(tracks, int):
        if tracks == -1:
            # TODO: allow all tracks 
            pass
        else:
            track_list.append(tracks)
    else:
        track_list = tracks

    audio_tracks = []
    for i, track_num in enumerate(track_list):
        if isinstance(delay, int):
            d = delay
        else:
            d = delay[i]
        
        if d > 0:
            audio_file = Eac3to(track_num, append=f"+{d}ms -log=NUL").extract_audio(src_path)
        else:
            audio_file = FFMpeg.Extractor(track_num).extract_audio(src_path)
            audio_file.container_delay = d
        
        if commentary_tracks is not None and track_num in commentary_tracks:
            is_commentary = True
        else:
            is_commentary = False
        trackinfo = audio_file.get_trackinfo()
        audio_format = trackinfo.get_audio_format()
        if not audio_format:
            raise Exception(f"Unable to retrieve audio format for track {track_num}!")
        if audio_format.display_name.lower() == "pcm" or (transcode_all and not audio_format.should_not_transcode()):
            audio_track = _create_audio_track(FLAC(preprocess=None).encode_audio(audio_file), name_scheme, src_path, is_commentary, track_num)
            audio_tracks.append(audio_track)
        else:
            audio_track = _create_audio_track(audio_file, name_scheme, src_path, is_commentary, track_num)
            audio_tracks.append(audio_track)
    return audio_tracks

def _create_audio_track(
        audio_file: AudioFile,
        track_name: str = "$language$ $ch$",
        src_path: Path = None,
        commentary: bool = False,
        track_num: int = -1
) -> AudioTrack:
    trackinfo = audio_file.get_trackinfo()
    lang_tag = trackinfo.sanitized_lang.to_tag()
    if lang_tag.lower() == "und" and src_path:
        src_tracks = ParsedFile.from_file(src_path).tracks
        for src_track in src_tracks:
            if src_track.type == TrackType.AUDIO and src_track.relative_index == track_num:
                lang_tag = src_track.sanitized_lang.language
                break
    audio_track = audio_file.to_track(track_name, lang_tag, default=False if commentary else True, forced=False, args=[f"--commentary-flag {track_num}"] if commentary else None)
    return audio_track