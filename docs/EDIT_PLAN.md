# Marcus AI Tool Hunt — 1-min editor test (Malva AI style)

Client test: Marcus AI Tool Hunt (YouTube). Due 5 days from receipt.
Deliver: Drive link (anyone with link) or unlisted YouTube + name/city, portfolio, rate/min, videos/month.
Rules: unpaid, use tool credits only for this test, never change password/email/settings.

## Assets (downloaded to raw/)
| File | Spec | Notes |
|---|---|---|
| raw/topview_th.mp4 | 1920x1080 25fps, 77.3s, -23 LUFS | AI-avatar presenter, static medium shot, teal/warm studio. Reads the Topview script word for word. |
| raw/pixverse_th.mp4 | 1920x1080 25fps, 103.2s | Same presenter, PixVerse script. |
| raw/logos/ | Horizontal / Vertical / Symbol x Black / White / Purple, RGBA PNG | Topview brand logos only (none for PixVerse). |
| notes/*_words.json | word timestamps (faster-whisper small.en) | Transcripts match the scripts. |

Pause trim: Topview 77s → ~70s tight (26 gaps > 0.35s). PixVerse 103s → ~98s.

## Malva AI style (from mNsR_KfjZpY, VMA8waKShkw, axBF6zXzsNA)
- **Screen recordings**: browser on a rounded card floating over a dark navy background with a bright blue glow from below. Hard zooms onto the active UI area, real cursor visible.
- **Highlights**: glowing blue/purple outline boxes around the button being clicked; selected text gets a highlight sweep.
- **Facecam**: circular presenter bubble bottom-right with a blue rim glow, on all screen sections. Sometimes it grows into a large circle on the right for emphasis.
- **Talking head**: full-frame between screen sections, with cut punch-ins (100% ↔ ~120%) on sentence changes.
- **Motion graphics**: tool title card (app icon + big white wordmark with reflection), 3D floating cards on purple, a typed prompt bar with glow ("Create a video..."), numbered node diagrams, a pill caption ("Link in the Description").
- **Open**: cold open with a punchy visual before the presenter.
- **Captions**: no full running subtitles in his long-form videos; text appears as key-phrase pop-ups and UI callouts.
- **Audio**: low bed music, whooshes on transitions, clicks on cursor clicks, pops on text.

## Edit plan (Topview, ~60-70s, 16:9 1080p)
| Time (src) | Line | Visual |
|---|---|---|
| 0.0-3.2 | Open topview.ai and log in | Cold open: 1.5s of the generated matcha clip → Topview logo reveal (Symbol pops, wordmark wipes in, glow) → screen card of topview.ai home. Facecam bubble in. |
| 3.8-11.2 | Dashboard → Canvas … any model | Zoom to sidebar, glow box on "Canvas". Pop-up: "CANVAS = custom workflows". |
| 11.8-19.3 | + node → Text to Video → T1 | Zoom-follow the cursor: plus icon, node menu, model dropdown. Highlight on "Topview T1". |
| 19.9-33.7 | Paste prompt | Typed-prompt animation (Malva prompt-bar look) with the prompt text, then the real paste in the UI. |
| 34.3-43.4 | 16:9 / 10s / 1080p / qty 1 → Generate | Quick zooms per setting, each with a small chip pop-up ("16:9", "10s", "1080p", "x1"), click SFX, glow on Generate. |
| 43.9-55.9 | Dashboard → AI Marketer → product link | TH punch-in on "While that renders", then screen: AI Marketer, paste link, generated ad playing. Pop-up "Fastest for e-commerce". |
| 56.4-67.0 | Back to Canvas → preview → download / regenerate | Screen: play the matcha clip big (full-frame for 2s), glow on the download arrow and Regenerate. |
| 67.6-77.0 | Core workflow summary | TH full-frame with a 3-card motion graphic: Canvas / AI Marketer / 12+ Models, Topview logo end lockup. |

Build: Python-generated HyperFrames comp (same pipeline as earlier tests): base cut list → screen cards + facecam bubble + pop-ups + logo animation → music/SFX mix at -14 LUFS → render 1080p.

## Screen recording shot list (Topview)
Record at 1920x1080, browser zoom 110-125%, hide bookmarks bar, slow and deliberate cursor, pause 1s before each click.
1. topview.ai/home logged in (scroll a little).
2. Click Canvas in the left sidebar; let the canvas load.
3. Plus icon → Text to Video → model dropdown → Topview T1.
4. Paste the matcha prompt.
5. Set 16:9, 10s, 1080p, quantity 1; show the credit cost; click Generate.
6. Home → AI Marketer → paste a product link → generate; record until the ad plays.
7. Back to Canvas → play the finished T1 clip → hover the download arrow → hover (don't click) Regenerate.
8. Download the T1 clip and the AI Marketer ad as files (used full-frame in the edit).
