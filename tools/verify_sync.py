"""Check that every click sound lands on its click picture.

python -I tools/verify_sync.py [video]   (default film/assets/screen_track.mp4, which runs on comp time)

1. Runs the ripple detector over the video (comp time) and lists every ripple onset.
2. Reads build/sfx_plan.json (the mixer's own placement) and pairs each mouse-click sound with the nearest ripple.
3. Writes notes/sync_check.jpg: for each planned click, the frames 2 before .. 3 after the sound, so a click whose
   ripple is invisible (yellow, white or purple buttons) is still checked by eye.
Pass rule: the sound is 0..2 frames after the ripple's first frame (light first, then sound).
"""
import json, os, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import detect_clicks as dc
from PIL import Image, ImageDraw

ROOT = dc.ROOT
VID = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, 'film', 'assets', 'screen_track.mp4')
plan = json.load(open(os.path.join(ROOT, 'build', 'sfx_plan.json')))
clicks = [t for t, f in plan if 'mouse' in f]
dur = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', VID],
                           capture_output=True, text=True).stdout)
dc.REC = lambda r: VID
rip = [c[0] for c in dc.scan('x', 0, dur)]
print('ripples in video:', len(rip), ' planned click sounds:', len(clicks))
bad = 0
for t in clicks:
    near = min(rip, key=lambda r: abs(r - t)) if rip else None
    d = None if near is None else round((t - near) * 30, 1)   # frames, + = sound after picture
    ok = d is not None and -0.5 <= d <= 2.5 and abs(near - t) < 0.3
    flag = 'OK ' if ok else ('-- ' if d is None or abs(near - t) >= 0.3 else 'BAD')
    bad += flag == 'BAD'
    print(f'{flag} sound {t:7.3f}  ripple {near if near is not None and abs(near - t) < 0.3 else "none":>7}  '
          f'{"" if not ok and (d is None or abs(near - t) >= 0.3) else f"{d:+.1f} fr"}')

# eye check strip: per click, frames -2..+3 around the sound, cropped to the brightest-change area is hard; use full frame
rows = []
for t in clicks:
    cells = []
    for k in range(-2, 4):
        ts = max(t + k / 30, 0)
        raw = subprocess.run(['ffmpeg', '-v', 'error', '-ss', f'{ts:.4f}', '-i', VID, '-frames:v', '1', '-vf', 'scale=240:-1',
                              '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], capture_output=True).stdout
        im = Image.frombytes('RGB', (240, 135), raw[:240 * 135 * 3]) if len(raw) >= 240 * 135 * 3 else Image.new('RGB', (240, 135))
        d = ImageDraw.Draw(im)
        d.text((4, 4), f'{t:.2f} {k:+d}', fill=(255, 255, 0))
        if k == 0:
            d.rectangle((0, 0, 239, 134), outline=(255, 60, 60), width=2)
        cells.append(im)
    rows.append(cells)
sheet = Image.new('RGB', (240 * 6, 135 * len(rows)))
for i, cells in enumerate(rows):
    for j, im in enumerate(cells):
        sheet.paste(im, (j * 240, i * 135))
sheet.save(os.path.join(ROOT, 'notes', 'sync_check.jpg'), quality=85)
print('BAD:', bad, '  sheet: notes/sync_check.jpg')
