# wapmux
Automation tools for remuxing BDMVs. Anime-focused.

## Installation

```
git clone https://github.com/washedfs/wapmux.git
cd wapmux
pip install -r requirements.txt
```

You'll need Python installed, duh. You'll also need the binaries for FFmpeg, eac3to, mkvmerge and libFLAC, as well as Aegisub installed on your device. The [muxtools documentation](https://muxtools.vodes.pw/guide/external-dependencies/) should have the links to all of these. Any Python dependencies should be installed with `requirements.txt`.

## Usage

`main.py` should be good enough for most use cases. Just make sure to modify the values for each show/episode. To run:
```
python main.py
```
**Please** check before and after the mux whether everything's how you want it to be. This includes episode number, source paths, track numbers, delay/shift values, and chapter names.

For more advanced muxers, perhaps you'd gain some benefit from the functions implemented in `wapfunc`. Or maybe not.
