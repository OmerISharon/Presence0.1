# Creator_RedNBlack.py - Argument Reference & Example

## Command-Line Arguments

| Argument                    | Type   | Required | Default                        | Description |
|-----------------------------|--------|----------|--------------------------------|-------------|
| `--text`                    | str    | Yes      | —                              | Input text content to animate.
| `--output_path`             | str    | Yes      | —                              | Full output path for the generated video file.
| `--fore_color`              | str    | No       | `"255,0,0"`                    | Foreground (text) color as R,G,B.
| `--bg_color`                | str    | No       | `"0,0,0"`                      | Background color as R,G,B. 
| `--text_remover_style`      | str    | No       | `"backspace"`                  | Style to remove text: `"backspace"` or `"fadeout"`.
| `--typing_sounds_dir`       | str    | No       | `None`                         | Folder with typing sound `.mp3` files (optional).
| `--background_audio_path`   | str    | No       | `None`                         | Path for background audio file.
| `--typing_sound_volume`     | float  | No       | `1.0`                          | Volume for typing audio.
| `--background_audio_volume` | float  | No       | `1.0`                          | Volume for background sounds.
| `--font_path`               | str    | No       | `"C:\Windows\Fonts\ariblk.ttf"`| Path to `.ttf` font file.
| `--font_size`               | int    | No       | `40`                           | Font size in pixels.
| `--is_short`                | bool   | No       | `True`                         | Set to `False` for landscape (1920x1080).
| `--fps`                     | int    | No       | `30`                           | Frames per second for the output video.
| `--pause_time`              | int    | No       | `2.0`                          | Pause time (in seconds) before starting backspace/fade for each text segment.
| `--typing_speed`            | int    | No       | `0.05`                         | Typing speed (delay per character in seconds).
| `--media_paths`             | list   | No       | `None`                         | List of video or image paths for background. They will replace the color background.
| `--font_effect`             | str    | No       | `""`                           | Comma‑separated font effects: 'stroke', 'shadow', 'transparent_overlay'
---

```bash
matrix_style
py matrix_v1.py --text "In order to do this, man must pass from the competitive to the creative mind; otherwise he cannot be in harmony with the Formless Intelligence, which is always creative and never competitive in spirit." --fore_color "0,255,128" --bg_color "10,10,10" --output_path "outputs/video_test.mp4" --typing_sounds_dir "D:\2025\Projects\Presence\Presence0.1\Creator\Channels\RedNBlack\Resources\Audio\Typing_Sounds" --font_size 48

videos_list_style
py matrix_v1.py --text "In order to do this, man must pass from the competitive to the creative mind; otherwise he cannot be in harmony with the Formless Intelligence, which is always creative and never competitive in spirit." --output_path "outputs/video_test.mp4" --fore_color "0,0,0" --typing_sounds_dir "D:\2025\Projects\Presence\Presence0.1\Creator\Channels\RedNBlack\Resources\Audio\Typing_Sounds" --typing_sounds_volume "0.2" --background_audio_path "D:\2025\Projects\Presence\Presence0.1\Resources\Media_Resources\Audio\Background_Audio\Inspirational\Amazing Grace - Casa Rosa.mp3" --background_audio_volume "2.0" --font_size 48 --media_paths "D:\2025\Projects\Presence\Presence0.1\Resources\Media_Resources\Video\1080x1920\Nature\2186967-hd_1080_1350_25fps\2186967-hd_1080_1350_25fps.mp4", "D:\2025\Projects\Presence\Presence0.1\Resources\Media_Resources\Video\1080x1920\Nature\2797545-hd_1080_1920_30fps\2797545-hd_1080_1920_30fps.mp4", "D:\2025\Projects\Presence\Presence0.1\Resources\Media_Resources\Video\1080x1920\Nature\3059046-hd_1080_1920_24fps\3059046-hd_1080_1920_24fps.mp4", "D:\2025\Projects\Presence\Presence0.1\Resources\Media_Resources\Video\1080x1920\Nature\4169233-hd_720_1280_30fps\4169233-hd_720_1280_30fps.mp4", "D:\2025\Projects\Presence\Presence0.1\Resources\Media_Resources\Video\1080x1920\Nature\4434286-hd_1080_1920_30fps\4434286-hd_1080_1920_30fps.mp4" --font_effect "transparent_overlay"
```
---

## Example Usage

```bash
python matrix_v1.py ^
  --text "Dream big. Work smart! Smile often?" ^
  --fore_color "0,255,128" ^
  --bg_color "10,10,10" ^
  --output_path "outputs/video_test.mp4" ^
  --text_remover_style "fade" ^
  --typing_sounds_dir "assets/typing_sounds" ^
  --font_path "C:\Windows\Fonts\arial.ttf" ^
  --font_size 48 ^
  --short true ^
  --fps 60
```