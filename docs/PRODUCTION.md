# Production notes

## Pipeline

| Step | Tool | Output |
|---|---|---|
| Transcribe the talking head | faster-whisper `small.en` (word timestamps) | `notes/topview_words.json` |
| Tighten pauses | `tools/th_cut.py` | `build/th_cut.mp4`, `build/vo.wav`, `build/words_cut.json`, `build/cutmap.json` |
| Record Topview | Playwright MCP (Chromium, fullscreen) + Cap CLI `record start --screen … --detach` | `rec/*.cap` |
| Constant frame rate | `ffmpeg -vf fps=60` | `rec/*_cfr.mp4` |
| Find clicks | `tools/detect_clicks.py`, `tools/clipstrip.py` | `build/clicks.json`, crop strips |
| Build | `tools/build.py assets screen audio html` | `film/assets/*`, `film/index.html` |
| Check | `npx hyperframes check`, `snapshot`, `tools/verify_sync.py` | 0 errors; per-click before/after frames |
| Render | `npx hyperframes render --quality delivery --fps 30` | `renders/*.mp4` |

All edit times in `tools/build.py` are **voice times** on the tightened talking head; comp time = voice time + 1.0 s
(the cold open).

## Recording the tool

- The browser is driven by scripts (`tools/steps_*.js`, wrapped with the helpers in `tools/pw_lib.inc.js` by
  `tools/build_run.sh`). Moves are eased (cubic in/out), each click waits ~0.3 s on target first, typing runs at a
  readable pace.
- The account owner signed in by hand; the scripts never touch credentials or account settings.
- Each take: an unrecorded pre-roll clears pop-ups (Topview shows several promos on every Home load), then
  `tools/focus_win.ps1` brings the window to the front and Cap starts. Redirect Cap's detached `record start` output to a
  file, or the command waits on the open pipe.
- Topview's canvas page triggers Chrome's Google Translate bubble; the build covers it with a clean crop of the top bar,
  and later takes block it with a `notranslate` meta tag injected at document start.
- Credits used: 22 for the Topview T1 clip (10 s, 1080p, 16:9) and about 12.5 for the AI Marketer ad.

## Click sync

v1 of this edit had clicks and click sounds out of step by up to 1.5 s. The causes and the fix:

1. **Variable frame rate.** Cap only writes a frame when the screen changes. `ffmpeg -ss` into a static stretch starts
   counting from the next real frame, so contact sheets, detection and the cut itself drifted by up to 0.7 s. Fix: convert
   every recording to constant 60 fps before any seek.
2. **Estimated click times.** Clicks had been read off 1-second contact sheets. Fix: measure them. The injected ripple
   is a violet ring that appears small, stays centred and grows for ~0.35 s, which static purple UI never does;
   `detect_clicks.py` looks for exactly that. Clicks on yellow, white or purple buttons hide the ripple, so those were
   measured from 20 fps crop strips or from pixel change under the cursor tip.
3. **Anchoring.** Each segment is defined by `at=(source second, voice second)`: the measured click lands on the word
   that names it, and the speed fills the rest. The click sound goes one frame after the ripple's first frame.
4. **Verification.** Before/after comp snapshots at every click, and the click transients in the final mix measured
   against their planned frames (14 of 17 within 2 ms; the other three are masked by a neighbouring pop-up or music hit).

## Sound choices

- Clicks: a real recorded mouse press (single press sliced from a Mixkit recording; a double-click recording for the
  canvas double-click).
- Pop-ups: one dry UI family (uisfx "studio": `select` for pills and chips, `expand` for cards, `press` for the address
  bar's Enter). No water-drop or bubble pops.
- Scene changes: short swishes only (0.2–0.45 s), quiet.
- End card: a deep cinematic drum hit (high-passed at 45 Hz).
- Music ducked under the voice with a sidechain compressor; mix normalised to −14 LUFS, −1.5 dBTP.

## Gotchas

- Typing into Topview's prompt flips the aspect ratio back to 9:16; set 16:9 after the prompt is in.
- In one take a click meant for the prompt box hit the aspect row under the open settings popover; that moment is not
  used.
- The HyperFrames render of v2 came out 9.6 dB under the mix (sample-aligned); the master has the mix remuxed in.
