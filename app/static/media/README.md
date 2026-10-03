# Local media setup

The application currently contains no downloaded stock video or photo assets.
The CSS gradients are intentional fallbacks. Add rights-verified files to
`app/static/media/`; the hero and interior-page scene loader will use them
automatically. Do not hotlink remote stock assets at runtime.

## Scene assets

For each scene, supply the following desktop files:

| Basename | Suggested subject |
| --- | --- |
| `hero-sunrise-mountains` | Misty forested hills at sunrise |
| `hero-day-clouds` | Moving clouds over green mountain ridges |
| `hero-rain-forest` | Rain over a tropical forest canopy |
| `hero-waterfall` | Waterfall in a forested valley |
| `hero-sunset-hills` | Sunset over layered green hills |

For every basename above, add:

- `<basename>.mp4` — H.264 video
- `<basename>.webm` — VP9 or AV1 video
- `<basename>.jpg` — still poster frame, under 200 KB

Optional mobile encodes use the same basename with `-mobile` before the
extension, for example `hero-day-clouds-mobile.mp4` and
`hero-day-clouds-mobile.webm`. These should be 720p or smaller.

Keep video clips 10–20 seconds, seamless, muted, 1080p maximum, and preferably
2–5 MB. Strip audio. Add each file's creator, source URL, licence, and download
date to `CREDITS.md`. Do not describe a clip as royalty-free until its specific
licence has been checked.

## Destination photography

Place photos in `app/static/images/places/`. The rendered destination slug is
the lowercase destination name with spaces changed to hyphens, followed by
`.jpg` (for example `jog-falls.jpg`). Keep each file locally served, optimized
for web, and include its creator, source URL, and licence in
`app/static/images/places/CREDITS.md`.

Until the photos are supplied, destination image areas display a designed
gradient instead of a broken-image icon.
