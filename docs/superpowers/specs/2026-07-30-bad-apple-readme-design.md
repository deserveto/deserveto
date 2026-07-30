# Bad Apple Lua-Style README Design

Replace the visible root README with one full-width, silent, looping GIF. The GIF is pre-rendered because GitHub Markdown cannot execute Lua. A real Lua renderer consumes downscaled grayscale frames and converts brightness into fixed 5×7 terminal glyphs before FFmpeg assembles the final animation. The source MP4 is never committed. Output is 480×360, full-length, infinitely looping, and below 100 MiB.
