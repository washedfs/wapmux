from os import PathLike
from pathlib import Path

from muxtools import AudioFile, AudioTrack, Eac3to, FFMpeg, FLAC, GlobSearch

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
        src_file = src_file.paths[0]
    else:
        src_path = Path(src_file)
    if src_path.suffix.lower() != ".mkv" and src_path.suffix.lower() != ".m2ts":
        raise Exception("Unsupported source file format!")
    
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
            audio_file = Eac3to(track_num, append=f"+{d}ms").extract_audio(src_path)
        else:
            audio_file = FFMpeg.Extractor(track_num).extract_audio(src_path)
            audio_file.container_delay = d
        
        trackinfo = audio_file.get_trackinfo()
        audio_format = trackinfo.get_audio_format()
        if not audio_format:
            raise Exception(f"Unable to retrieve audio format for track {track_num}!")
        if audio_format.should_not_transcode():
            audio_track = create_audio_track(audio_file, name_scheme)
            audio_tracks.append(audio_track)
        else:
            if audio_format.display_name.lower() == "pcm" or transcode_all:
                audio_track = create_audio_track(FLAC(preprocess=None).encode_audio(audio_file), name_scheme)
                audio_tracks.append(audio_track)
    return audio_tracks

def create_audio_track(
        audio_file: AudioFile,
        track_name: str = "$language$ $ch$"
) -> AudioTrack:
    trackinfo = audio_file.get_trackinfo()
    lang_tag = trackinfo.sanitized_lang.to_tag()
    audio_track = audio_file.to_track(track_name, lang_tag, default=True, forced=False)
    return audio_track