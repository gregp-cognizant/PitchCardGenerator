# Making Videos for this Repo

## Mac Instructions

Record the screen
* Command+Shift+5 to launch screen recorder
* Use record area or record full screen as needed
* Command+Shift+5 to open screen recorder and click stop

Follow this guide to convert the .mov which mac screen recorder to .webp, which is much smaller and suitable for markdown: <https://gist.github.com/witmin/1edf926c2886d5c8d9b264d70baf7379>

Example command
```
ffmpeg -i Basic-Use-of-Jupyter.mov -vcodec libwebp -filter:v fps=fps=10 -lossless 0  -compression_level 3 -q:v 70 -loop 1 -an -vsync 0 -s 800:600 -quality 50 Basic-Use-of-Jupyter.webp
```
