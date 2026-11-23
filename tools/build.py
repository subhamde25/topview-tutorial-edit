"""Marcus AI Tool Hunt / Topview test edit (Malva AI style).

python -I tools/build.py [assets] [screen] [audio] [html]   (run from marcus-ai-test/, no args = all)

- assets: background plate, translate-bubble patch, copies of media into film/assets/
- screen: build/screen_track.mp4, the Cap recordings cut and speed-fitted to the voice timeline
- audio:  film/assets/mix.wav, voice + ducked music + SFX, -14 LUFS
- html:   film/index.html, the HyperFrames comp (card, bubble, zooms, glow boxes, pop-ups, logo)
All edit times below are VOICE times (v) on the tightened talking head; comp time = v + L.
"""
import json, os, shutil, subprocess, sys
from PIL import Image, ImageDraw, ImageFilter

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
B = os.path.join(ROOT, 'build'); FA = os.path.join(ROOT, 'film', 'assets')
REC = lambda r: os.path.join(ROOT, 'rec', f'{r}_cfr.mp4')   # constant-60 fps copies: Cap writes VFR, seeks into gaps drift
SFXW = 'C:/Users/deysu/Downloads/New folder/drive-download-20261018T195157Z-1-001/wick-tutorial/assets/audio/sfx/'
SFXM = os.path.expanduser('~/SFX-Library/mixkit/')
MUSIC = 'C:/Users/deysu/Downloads/New folder/drive-download-20261018T195157Z-1-001/wick-tutorial/audio/music.mp3'
WM = 'C:/Users/deysu/Downloads/New folder/drive-download-20261018T195157Z-1-001/wick-tutorial/assets/SD_watermark_white.png'
FPS = 30
L = 1.0                       # cold open before the voice starts
CUT = json.load(open(os.path.join(B, 'cutmap.json')))
VO_LEN = CUT['total']
TAIL = 1.7
TOTAL = round(L + VO_LEN + TAIL, 3)
WORDS = json.load(open(os.path.join(B, 'words_cut.json')))
os.makedirs(FA, exist_ok=True)


def W(prefix, after=0.0):
    """Voice time of the first word starting with prefix at or after `after`."""
    p = prefix.lower()
    for w in WORDS:
        if w['s'] >= after - 1e-3 and w['w'].lower().strip('.,!?"').startswith(p):
            return w['s']
    raise KeyError(prefix)


def q(t):  # snap to the frame grid
    return round(round(t * FPS) / FPS, 4)


# ---------------------------------------------------------------- the cut ----
# Every segment is anchored on a click measured frame-exactly in the constant-fps recordings
# (tools/detect_clicks.py + notes/strips): `at=(source second, voice second)` puts that source moment
# on that word. Speed `sp` = source seconds per voice second. Zoom keys (v, scale, fx, fy) are recording px.
# clicks: (source second, 'click'|'dbl') get a mouse sound one frame after the picture.
# cur: synthetic cursor waypoints (source second, x, y) for Topview's canvas page, which hides the real one.
def seg(id, r, t0, t1, sp, at=None, a=None, z=(), clicks=(), cur=None, patch=False):
    t0, t1 = q(t0), q(t1)
    if at:
        a = at[0] - (at[1] - t0) * sp
    return dict(id=id, r=r, t0=t0, t1=t1, sp=sp, a=round(a, 4), b=round(a + (t1 - t0) * sp, 4), z=list(z),
                clicks=list(clicks), cur=cur, patch=patch)


SEG = [
    # 1 Open topview.ai (home)
    seg('home', 'r1', 1.6, 3.43, 1.0, a=1.0, z=[(1.6, 1.0, 960, 540), (3.43, 1.07, 760, 420)]),
    # 2 Dashboard -> Canvas in the sidebar (click lands on "Canvas" 4.70)
    seg('canvas', 'r1', 3.43, 6.30, 1.2, at=(17.767, 4.75), clicks=[(17.767, 'click')],
        z=[(3.43, 1.0, 960, 540), (3.95, 2.1, 330, 260), (5.5, 2.1, 330, 260), (6.05, 1.0, 960, 540)]),
    # 3 Canvas landing (scroll to My Projects), then Create New Project
    seg('landA', 'r1', 6.30, 9.17, 1.28, a=19.62, z=[(6.3, 1.0, 960, 540)]),
    seg('landB', 'r1', 9.17, 10.60, 1.3, at=(30.82, 10.58), clicks=[(30.82, 'click')],
        z=[(9.17, 1.0, 960, 540), (9.9, 1.75, 700, 640)]),
    # 4 Double-click the canvas -> node menu (lands on "plus icon")
    seg('menu', 'r1b', 10.60, 12.86, 1.0, at=(14.0, 11.15), clicks=[(14.0, 'dbl')], patch=True,
        cur=[(13.0, 1125, 750), (13.62, 700, 412)], z=[(10.6, 1.25, 840, 560), (11.2, 1.7, 840, 640)]),
    # 5 Select Video (lands on "Text to Video")
    seg('video', 'r1b', 12.86, 14.55, 1.5, at=(18.05, 13.55), clicks=[(18.05, 'click')], patch=True,
        cur=[(17.015, 700, 412), (17.75, 712, 518)], z=[(12.86, 1.7, 840, 640), (14.0, 1.7, 840, 640), (14.5, 1.25, 900, 640)]),
    # 6 Settings chip on "Model dropdown", the model list on "choose Topview T1"
    seg('model1', 'r1b', 14.55, 16.30, 1.99, at=(22.5, 14.92), clicks=[(22.5, 'click')], patch=True,
        cur=[(21.76, 712, 560), (22.2, 560, 890), (22.6, 560, 890), (25.0, 612, 418)],
        z=[(14.55, 1.25, 800, 700), (15.1, 1.25, 800, 700), (15.8, 1.85, 720, 300)]),
    seg('model2', 'r1b', 16.30, 17.70, 0.8, a=25.24, clicks=[(25.25, 'click')], patch=True,
        cur=[(25.24, 612, 418)], z=[(16.3, 1.85, 720, 300)]),
    # 7-9 "Now paste this prompt": the prompt types in from the first word (the 17.25 s click in this take hit the
    #     aspect row under the popover, not the prompt box, so it is not shown)
    seg('typing', 'r1d', 17.70, 30.66, 0.78, a=19.85, patch=True, cur=[(19.85, 1250, 1010)],
        z=[(17.7, 1.3, 900, 760), (18.4, 1.7, 900, 930), (30.66, 1.8, 900, 930)]),
    # 10 settings: 16:9 on "16", duration drag on "duration", 1080p on "1080p", quantity
    seg('aspect', 'r1d', 30.66, 32.95, 1.3, at=(106.55, 32.15), clicks=[(106.55, 'click')], patch=True,
        cur=[(104.62, 700, 1000), (106.25, 990, 958)], z=[(30.66, 1.6, 900, 760), (31.3, 2.0, 930, 900)]),
    seg('duration', 'r1c', 32.95, 34.75, 1.0, at=(12.35, 33.40), clicks=[(12.35, 'click')], patch=True,
        cur=[(11.9, 1000, 700), (12.1, 1102, 666), (12.36, 1102, 666), (13.25, 679, 666)], z=[(32.95, 1.9, 830, 640)]),
    seg('res', 'r1b', 34.75, 36.60, 2.5, at=(28.55, 34.85), clicks=[(28.55, 'click'), (30.80, 'click')], patch=True,
        cur=[(28.3, 640, 540), (28.45, 662, 512), (30.5, 680, 468)], z=[(34.75, 2.0, 700, 500)]),
    seg('qty', 'r1d', 36.60, 37.86, 1.0, a=118.0, patch=True, cur=[(118.0, 990, 958)],
        z=[(36.6, 1.7, 1060, 860), (37.0, 2.1, 1150, 900)]),
    # 11 Hit Generate (lands on "Generate")
    seg('gen', 'r1d', 37.86, 38.95, 1.0, at=(123.65, 38.2), clicks=[(123.65, 'click')], patch=True,
        cur=[(123.31, 1260, 918)], z=[(37.86, 2.1, 1200, 900), (38.45, 2.1, 1200, 900), (38.95, 1.3, 960, 600)]),
    # 13 AI Marketer in the sidebar (lands on "Marketer"; ends before the new tab flashes white)
    seg('mkt', 'r2', 41.10, 42.30, 1.0, at=(15.283, 41.9), clicks=[(15.283, 'click')],
        z=[(41.1, 1.6, 500, 420), (41.5, 2.1, 330, 360)]),
    # 14 URL to Video, paste a product link, Start creating
    seg('u2v', 'r2', 42.30, 44.50, 1.0, at=(25.05, 43.45), clicks=[(25.05, 'click')],
        z=[(42.3, 1.0, 960, 540), (42.8, 1.45, 760, 470), (44.0, 1.45, 760, 470), (44.5, 1.2, 800, 500)]),
    seg('url', 'r2', 44.50, 45.45, 1.6, at=(29.8, 44.65), clicks=[(29.8, 'click')], z=[(44.5, 1.9, 600, 360)]),
    seg('start', 'r2', 45.45, 45.87, 1.0, at=(94.867, 45.65), clicks=[(94.867, 'click')], z=[(45.45, 1.7, 1350, 950)]),
    seg('chat', 'r2', 45.87, 46.95, 1.3, a=97.0, z=[(45.87, 1.0, 960, 540), (46.95, 1.1, 1100, 420)]),
    # 16 back to Canvas, the finished node
    seg('back', 'r3', 50.20, 51.90, 1.0, a=9.2, cur=[(9.2, 1300, 760), (10.9, 1150, 680)],
        z=[(50.2, 1.0, 960, 540), (51.9, 1.35, 960, 560)]),
    # 18 play (lands on "play")
    seg('play', 'r3', 53.80, 55.45, 1.0, at=(15.10, 54.2), clicks=[(15.10, 'click')],
        cur=[(14.7, 1120, 640), (14.85, 960, 540), (15.5, 960, 540), (16.35, 1120, 800)],
        z=[(53.8, 1.35, 960, 560), (54.3, 1.75, 960, 540)]),
    # 19 download (lands on "download")
    seg('dl', 'r3', 55.45, 57.35, 1.5, at=(29.017, 56.6), clicks=[(29.017, 'click')],
        cur=[(27.29, 1260, 360), (28.4, 1348, 306)], z=[(55.45, 1.3, 960, 450), (56.0, 2.2, 1250, 320)]),
    # 20 regenerate (hover, no click: it would spend credits)
    seg('regen', 'r3', 57.35, 60.00, 1.0, a=35.45, cur=[(35.45, 1100, 307), (35.9, 346, 307)],
        z=[(57.35, 2.2, 1250, 320), (58.1, 2.2, 520, 320)]),
]


def src2v(seg_id, src_t):
    s = next(x for x in SEG if x['id'] == seg_id)
    return s['t0'] + (src_t - s['a']) / s['sp']


# Full-frame talking head (voice times) and full-frame result footage.
TH_FULL = [(0.0, 1.6), (38.95, 41.10), (60.00, VO_LEN + TAIL)]
BROLL = [
    dict(id='coldopen', src='t1_matcha.mp4', ms=2.2, t0=-L, t1=0.0),
    dict(id='adfull', src='marketer_ad.mp4', ms=2.0, t0=46.95, t1=50.20),
    dict(id='matchafull', src='t1_matcha.mp4', ms=0.4, t0=51.90, t1=53.80),
]


def CV(sid, k=0):
    """Voice time of a segment's k-th measured click."""
    return src2v(sid, next(x for x in SEG if x['id'] == sid)['clicks'][k][0])


# Glow boxes (recording px), on/off in voice time, tied to the measured clicks.
HL = [
    dict(seg='canvas', box=(15, 132, 274, 40), on=CV('canvas') - 0.45, off=CV('canvas') + 0.6),
    dict(seg='landB', box=(566, 652, 234, 46), on=9.95, off=10.60),
    dict(seg='video', box=(718, 500, 244, 36), on=13.0, off=CV('video') + 0.35),
    dict(seg='model2', box=(544, 92, 362, 36), on=16.42, off=17.70),
    dict(seg='typing', box=(520, 905, 840, 70), on=18.0, off=19.4),
    dict(seg='aspect', box=(958, 940, 66, 50), on=CV('aspect') - 0.45, off=32.95),
    dict(seg='duration', box=(530, 648, 600, 46), on=CV('duration') - 0.1, off=34.75),
    dict(seg='res', box=(536, 502, 288, 46), on=34.78, off=CV('res', 1) - 0.25),
    dict(seg='res', box=(550, 452, 262, 34), on=CV('res', 1) - 0.25, off=36.60),
    dict(seg='qty', box=(1136, 898, 48, 40), on=36.75, off=37.86),
    dict(seg='gen', box=(1188, 898, 154, 42), on=CV('gen') - 0.3, off=38.75),
    dict(seg='mkt', box=(15, 301, 274, 40), on=CV('mkt') - 0.45, off=42.30),
    dict(seg='u2v', box=(590, 354, 330, 212), on=CV('u2v') - 0.45, off=CV('u2v') + 0.3),
    dict(seg='url', box=(214, 302, 710, 64), on=44.50, off=45.45),
    dict(seg='start', box=(974, 934, 756, 62), on=45.45, off=45.87),
    dict(seg='play', box=(918, 498, 84, 84), on=CV('play') - 0.3, off=CV('play') + 0.45, round=True),
    dict(seg='dl', box=(1328, 286, 44, 42), on=CV('dl') - 0.45, off=57.20, round=True),
    dict(seg='regen', box=(324, 286, 44, 42), on=W('regenerate', 57.4) - 0.2, off=60.0, round=True),
]

# Every measured click -> (voice time, kind). The sound lands one frame after the picture.
CLICKS = [(src2v(s['id'], t), k) for s in SEG for t, k in s['clicks']]


def speeds():
    for s in SEG:
        cl = ' '.join(f'{src2v(s["id"], t):.2f}' for t, _ in s['clicks'])
        print(f"{s['id']:9s} {s['r']:4s} src {s['a']:7.2f}-{s['b']:7.2f}  v {s['t0']:6.2f}-{s['t1']:6.2f}  x{s['sp']:.2f}  clicks@v {cl}")


# ------------------------------------------------------------- assets ----
def build_assets():
    # Malva-style plate: deep navy, bright blue light rising from the bottom edge.
    w, h = 1920, 1080
    im = Image.new('RGB', (w, h), (4, 6, 16))
    g = Image.new('RGB', (w, h), (0, 0, 0)); d = ImageDraw.Draw(g)
    d.ellipse((-200, 760, 2120, 1700), fill=(30, 90, 255))
    d.ellipse((300, 880, 1620, 1500), fill=(120, 190, 255))
    g = g.filter(ImageFilter.GaussianBlur(160))
    im = Image.blend(im, g, 0.85)
    t = Image.new('RGB', (w, h), (0, 0, 0)); d = ImageDraw.Draw(t)
    d.ellipse((600, -500, 1900, 400), fill=(28, 24, 70))
    im = Image.blend(im, Image.blend(im, t.filter(ImageFilter.GaussianBlur(200)), 0.5), 0.6)
    im.save(os.path.join(FA, 'bg.jpg'), quality=94)
    # Clean top-right of the canvas (Plugin / credits / Agent) to cover Chrome's translate bubble.
    p = Image.open(os.path.join(ROOT, 'notes', 'sc_r1c.jpg')).convert('RGB').crop((1176, 0, 1536, 99.2))
    p.resize((450, 124), Image.LANCZOS).save(os.path.join(B, 'patch.png'))
    for src, dst in [('build/th_cut.mp4', 'th_cut.mp4'), ('raw/marketer_ad.mp4', 'marketer_ad.mp4'),
                     ('raw/logos/Horizontal_White.png', 'logo_h_white.png'), ('raw/logos/Symbol_White.png', 'logo_sym_white.png'),
                     ('raw/logos/Symbol_Purple.png', 'logo_sym_purple.png')]:
        shutil.copyfile(os.path.join(ROOT, src), os.path.join(FA, dst))
    shutil.copyfile(WM, os.path.join(FA, 'sd_watermark.png'))
    # Re-encode generated clips with a keyframe every second so seeking never freezes.
    for src in ['t1_matcha.mp4']:
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', os.path.join(ROOT, 'raw', src), '-an', '-r', '30', '-g', '30',
                        '-c:v', 'libx264', '-crf', '15', '-pix_fmt', 'yuv420p', os.path.join(FA, src)], check=True)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', os.path.join(ROOT, 'raw', 'marketer_ad.mp4'), '-an', '-r', '30', '-g', '30',
                    '-vf', 'scale=1920:1080:flags=lanczos', '-c:v', 'libx264', '-crf', '15', '-pix_fmt', 'yuv420p',
                    os.path.join(FA, 'marketer_ad.mp4')], check=True)
    print('assets ok')


# ------------------------------------------------------------- screen ----
def build_screen():
    sd = os.path.join(B, 'seg'); os.makedirs(sd, exist_ok=True)
    enc = ['-c:v', 'libx264', '-preset', 'medium', '-crf', '17', '-g', '30', '-pix_fmt', 'yuv420p', '-r', str(FPS), '-an']
    parts, cur = [], 0.0   # cur in comp time
    patch = os.path.join(B, 'patch.png')

    def black(n, name):
        out = os.path.join(sd, name)
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'lavfi', '-i', f'color=c=black:s=1920x1080:r={FPS}',
                        '-frames:v', str(n)] + enc + [out], check=True)
        parts.append(out)

    for i, s in enumerate(SEG):
        c0, c1 = q(s['t0'] + L), q(s['t1'] + L)
        gap = round((c0 - cur) * FPS)
        if gap > 0:
            black(gap, f'gap{i:02d}.mp4')
        n = round((c1 - c0) * FPS)
        sp = (s['b'] - s['a']) / (s['t1'] - s['t0'])
        vf = f'[0:v]setpts=(PTS-STARTPTS)/{sp:.6f},fps={FPS}'
        cmd = ['ffmpeg', '-v', 'error', '-y', '-ss', f"{s['a']:.3f}", '-t', f"{s['b'] - s['a'] + 0.5:.3f}", '-i', REC(s['r'])]
        if s.get('patch'):
            cmd += ['-i', patch]; vf += '[v];[v][1:v]overlay=1470:0'
        vf += '[o]'
        out = os.path.join(sd, f"{i:02d}_{s['id']}.mp4")
        subprocess.run(cmd + ['-filter_complex', vf, '-map', '[o]', '-frames:v', str(n)] + enc + [out], check=True)
        parts.append(out); cur = c1
    tail = round((TOTAL - cur) * FPS)
    if tail > 0:
        black(tail, 'gapz.mp4')
    lst = os.path.join(sd, 'list.txt')
    open(lst, 'w').write(''.join(f"file '{p}'\n" for p in parts))
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', lst, '-c', 'copy',
                    os.path.join(FA, 'screen_track.mp4')], check=True)
    d = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0',
                              os.path.join(FA, 'screen_track.mp4')], capture_output=True, text=True).stdout)
    print('screen_track', round(d, 3), 'expected', TOTAL)
    assert abs(d - TOTAL) < 0.1, 'screen track length drifted'


# -------------------------------------------------------------- audio ----
def peak_offset(path):
    """Seconds from file start to its loudest moment in the first 0.6 s (so hits land on the picture)."""
    import array
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', path, '-t', '0.6', '-ac', '1', '-ar', '8000', '-f', 's16le', '-'],
                         capture_output=True).stdout
    a = array.array('h', raw)
    if not a:
        return 0.0
    i = max(range(len(a)), key=lambda k: abs(a[k]))
    return i / 8000


UISFX = os.path.expanduser('~/.claude/skills/real-sfx/vendor/node_modules/uisfx/sounds/studio/')
CLICK = dict(f=SFXM + 'click/clear_mouse_clicks_2997.mp3', slice=(0.19, 0.11), onset=0.016)        # real mouse, press only
DBL = dict(f=SFXM + 'click/fast_double_click_on_mouse_275.mp3', slice=(0.10, 0.22), onset=0.012)    # real double press
FRAME = 1 / FPS


def sfx_events():
    """(comp time the sound must hit, file, gain, options). User notes on v1: no water-drop pops, no long airy
    whooshes, no twinkle on the end card, clicks frame-true. So: one studio UI family for pop-ups, short swishes
    (<= 0.45 s) only on real scene changes, a deep drum hit on the logo, a real mouse press on every measured click."""
    ev = []
    for v, kind in CLICKS:                      # one frame after the ripple's first frame
        d = DBL if kind == 'dbl' else CLICK
        ev.append((v + L + FRAME, d['f'], 0.5, dict(slice=d['slice'], onset=d['onset'])))
    swish = [dict(f=SFXW + 'push-whoosh.mp3'),
             dict(f=SFXM + 'transition/air_zoom_vacuum_2608.mp3', slice=(0.0, 0.45)),
             dict(f=SFXM + 'game/explainer_video_game_alert_sweep_236.mp3')]
    cuts = [1.6, 38.95, 41.10, 46.95, 50.20, 51.90, 53.80, 60.0]   # talking head <-> screen, full-frame results
    for i, v in enumerate(cuts):
        w = swish[i % 3]
        ev.append((v + L, w['f'], 0.22, dict(slice=w.get('slice'))))
    for v in POP_TIMES:
        ev.append((v + L + FRAME, UISFX + 'select.mp3', 0.30, {}))
    for v in CARD_TIMES:
        ev.append((v + L + FRAME, UISFX + 'expand.mp3', 0.34, {}))
    ev.append((URL_ON + L + FRAME, UISFX + 'expand.mp3', 0.30, {}))     # address bar opens
    ev.append((URL_ENTER + L + FRAME, UISFX + 'press.mp3', 0.36, {}))   # address bar "enter"
    ev.append((0.12, SFXW + 'rise-into-logo.mp3', 0.55, {}))             # cold-open logo
    ev.append((ROOF_T + 0.12 + L, SFXM + 'cinematic/drum_deep_impact_563.mp3', 0.42, dict(hp=45)))   # end lockup
    return ev


def build_audio():
    ev = sfx_events()
    ins = ['-i', os.path.join(B, 'vo.wav'), '-i', MUSIC]
    fc = [f'[0:a]adelay={int(L * 1000)}|{int(L * 1000)},apad=whole_dur={TOTAL}[vo]',
          '[vo]asplit=2[vo1][key]',
          f'[1:a]atrim=0:{TOTAL},asetpts=PTS-STARTPTS,volume=0.30,afade=t=in:d=0.4,afade=t=out:st={TOTAL - 2.2}:d=2.2[mus]',
          '[mus][key]sidechaincompress=threshold=0.025:ratio=6:attack=25:release=350:makeup=1[duck]']
    mix = ['[vo1]', '[duck]']
    # typing bed under the prompt read
    ins += ['-i', SFXM + 'keyboard/keyboard_typing_1386.mp3']
    k = 2
    ty0, ty1 = src2v('typing', 20.05) + L, src2v('typing', 29.9) + L   # follows the on-screen typing
    fc.append(f'[{k}:a]atrim=0:{ty1 - ty0},asetpts=PTS-STARTPTS,volume=0.10,afade=t=in:d=0.2,afade=t=out:st={ty1 - ty0 - 0.4}:d=0.4,'
              f'adelay={int(ty0 * 1000)}|{int(ty0 * 1000)}[ty]')
    mix.append('[ty]'); k += 1
    # address-bar typing: a short real keyboard burst under "topview .ai"
    ins += ['-i', SFXM + 'keyboard/keyboard_typing_1386.mp3']
    u0, u1 = URL_TYPE[0] + L, URL_TYPE[1] + L
    fc.append(f'[{k}:a]atrim=0:{u1 - u0:.3f},asetpts=PTS-STARTPTS,volume=0.08,afade=t=out:st={u1 - u0 - 0.12:.3f}:d=0.12,'
              f'adelay={int(u0 * 1000)}|{int(u0 * 1000)}[ut]')
    mix.append('[ut]'); k += 1
    for j, (t, f, gain, o) in enumerate(ev):
        chain = 'aformat=channel_layouts=stereo'
        if o.get('slice'):
            s0, sd = o['slice']
            chain += f',atrim={s0}:{s0 + sd},asetpts=PTS-STARTPTS,afade=t=out:st={max(sd - 0.04, 0):.3f}:d=0.04'
            lead = o['onset'] if 'onset' in o else peak_offset(f) - s0
        else:
            lead = peak_offset(f)
        if o.get('hp'):
            chain += f",highpass=f={o['hp']}"
        start = max(t - max(lead, 0), 0)
        ins += ['-i', f]
        fc.append(f'[{k}:a]{chain},volume={gain},adelay={int(round(start * 1000))}|{int(round(start * 1000))}[s{j}]')
        mix.append(f'[s{j}]'); k += 1
    json.dump([[round(t, 4), os.path.basename(f)] for t, f, _, _ in ev], open(os.path.join(B, 'sfx_plan.json'), 'w'), indent=0)
    fc.append(f"{''.join(mix)}amix=inputs={len(mix)}:normalize=0:duration=first,atrim=0:{TOTAL}[pre]")
    pre = os.path.join(B, 'mix_pre.wav')
    subprocess.run(['ffmpeg', '-v', 'error', '-y'] + ins + ['-filter_complex', ';'.join(fc), '-map', '[pre]',
                    '-ar', '48000', '-ac', '2', pre], check=True)
    # two-pass loudnorm to -14 LUFS, -1.5 dBTP
    m = subprocess.run(['ffmpeg', '-hide_banner', '-i', pre, '-af', 'loudnorm=I=-14:TP=-1.5:LRA=9:print_format=json', '-f', 'null', '-'],
                       capture_output=True, text=True).stderr
    j = json.loads(m[m.rindex('{'):m.rindex('}') + 1])
    ln = (f"loudnorm=I=-14:TP=-1.5:LRA=9:measured_I={j['input_i']}:measured_TP={j['input_tp']}:measured_LRA={j['input_lra']}"
          f":measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true")
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', pre, '-af', ln, '-ar', '48000', os.path.join(FA, 'mix.wav')], check=True)
    print('audio ok, events', len(ev), 'pre-I', j['input_i'])


# --------------------------------------------------------------- html ----
CARD = dict(x=160, y=62, w=1600, h=900)
K = CARD['w'] / 1920


def zstate(s, fx, fy):
    sc = K * s
    x = CARD['w'] / 2 - fx * sc
    y = CARD['h'] / 2 - fy * sc
    x = min(0, max(CARD['w'] - 1920 * sc, x))
    y = min(0, max(CARD['h'] - 1080 * sc, y))
    return round(sc, 4), round(x, 1), round(y, 1)


# Pop-ups: (id, voice on, voice off, html, css position)
POPS = [
    ('p_canvas', 6.45, 8.85, 'Canvas <span class="dim">= custom workflows</span>', 'left:210px;top:110px;'),
    ('p_menu', 10.65, 12.8, 'Double-click <span class="dim">→ add a node</span>', 'left:210px;top:110px;'),
    ('p_t2v', 12.95, 14.5, 'Video <span class="dim">= text to video</span>', 'left:210px;top:110px;'),
    ('p_t1', 16.35, 17.7, '<img src="assets/logo_sym_white.png" class="ic"/>Topview T1', 'left:210px;top:110px;'),
    ('p_render', 39.15, 41.0, '<span class="spin"></span>Rendering · about 7 min', 'left:1210px;top:150px;'),
    ('p_u2v', 43.1, 45.4, 'URL <span class="dim">→</span> video ad', 'left:1230px;top:110px;'),
    ('p_fast', W('fastest', 46.9) - 0.1, 50.1, '⚡ Fastest for e-commerce', 'left:120px;top:880px;'),
    ('p_admeta', 47.0, 50.1, 'AI Marketer · 8 s ad · 16:9', 'left:120px;top:96px;'),
    ('p_ready', 52.05, 53.75, '✓ Topview T1 · 10 s · 1080p', 'left:120px;top:880px;'),
    ('p_play', 54.0, 55.4, 'Preview', 'left:210px;top:110px;'),
    ('p_dl', W('download', 55.4), 57.3, '⬇ Download', 'left:210px;top:110px;'),
    ('p_regen', W('regenerate', 57.4), 59.95, '↻ Regenerate · same settings', 'left:210px;top:110px;'),
    ('p_core', 60.15, 62.3, 'THE CORE WORKFLOW', 'left:120px;top:150px;'),
]
MODELS = ['Topview T1', 'Seedance 2.5', 'Kling 4.0', 'Wan 3.0', 'Nano Banana 2.1', 'Midjourney 8.2']
MODEL_T = W('workflows', 6.5) + 0.25
CHIPS = [('16:9', W('16', 30.7)), ('10s', W('10', 32.0)), ('1080p', W('1080', 34.0)), ('×1', W('1', 36.6))]
GEN_T = 38.2
SUM = [('Canvas', 'full control', W('canvas', 62.3)), ('AI Marketer', 'speed', W('ai', 63.5)),
       ('12+ models', 'one place', W('dozen', 64.5) - 0.2)]
ROOF_T = W('roof', 67.0) - 0.4
URL_ON, URL_TYPE, URL_ENTER, URL_OFF = 0.10, (0.42, 1.18), 1.26, 1.58   # address bar under "Open topview .ai"
CARD_TIMES = [19.2] + [t for *_, t in SUM]                                 # prompt card, summary cards
POP_TIMES = [p[1] for p in POPS] + [MODEL_T + i * 0.09 for i in range(0, len(MODELS), 2)] + [t for _, t in CHIPS] + [GEN_T]


def build_html():
    c = lambda v: round(v + L, 3)   # voice -> comp
    el, js = [], []
    ti = [10]

    def track():
        ti[0] += 1; return ti[0]

    # talking head, full frame (one timed video; its wrapper fades and punches in)
    el.append(f'<div id="thwrap"><video id="thv" class="clip" src="assets/th_cut.mp4" muted playsinline '
              f'data-start="{L}" data-duration="{VO_LEN}" data-track-index="2"></video></div>')
    js.append('tl.set("#thwrap", {opacity: 0}, 0);')
    punch = [1.0, 1.12, 1.0]
    for i, (a, b) in enumerate(TH_FULL):
        js.append(f'tl.set("#thwrap", {{opacity: 1, scale: {punch[i]}}}, {c(a)});')
        if b < VO_LEN:
            js.append(f'tl.set("#thwrap", {{opacity: 0}}, {c(b)});')
    js.append(f'tl.set("#thwrap", {{scale: 1.1}}, {c(62.45)});')   # punch-in on the summary line

    # screen card
    hl_html = []
    for i, h in enumerate(HL):
        x, y, w, hh = h['box']
        cls = 'hl round' if h.get('round') else ('hl soft' if h.get('soft') else 'hl')
        hl_html.append(f'<div id="hl{i}" class="clip {cls}" style="left:{x - 8}px;top:{y - 8}px;width:{w + 16}px;height:{hh + 16}px" '
                       f'data-start="{c(h["on"])}" data-duration="{round(h["off"] - h["on"], 3)}" data-track-index="{track()}"><i></i></div>')
        js.append(f'tl.fromTo("#hl{i} i", {{opacity: 0, scale: 1.25}}, {{opacity: 1, scale: 1, duration: 0.28, ease: "expo.out"}}, {c(h["on"])});')
    el.append(f'<div id="card"><div id="zoom" data-layout-allow-overflow><video id="scr" class="clip" src="assets/screen_track.mp4" muted playsinline '
              f'data-start="0" data-duration="{TOTAL}" data-track-index="3"></video>{"".join(hl_html)}__VCUR__</div></div>')
    # card visibility: contiguous runs of screen segments
    runs, cur = [], None
    for s in SEG:
        if cur and abs(s['t0'] - cur[1]) < 0.05:
            cur[1] = s['t1']
        else:
            cur = [s['t0'], s['t1']]; runs.append(cur)
    js.append('tl.set("#card", {opacity: 0}, 0);')
    for a, b in runs:
        js.append(f'tl.fromTo("#card", {{opacity: 0, scale: 0.94, y: 20}}, {{opacity: 1, scale: 1, y: 0, duration: 0.38, ease: "expo.out"}}, {c(a)});')
        js.append(f'tl.to("#card", {{opacity: 0, scale: 0.97, duration: 0.16, ease: "power3.in"}}, {c(b) - 0.16});')
    for s in SEG:
        zs = s['z']
        st = zstate(zs[0][1], zs[0][2], zs[0][3])
        if len(zs) == 1:
            js.append(f'tl.set("#zoom", {{scale: {st[0]}, x: {st[1]}, y: {st[2]}}}, {c(s["t0"])});')
        for k, ((v0, *_), (v1, s1, fx1, fy1)) in enumerate(zip(zs, zs[1:])):
            sc, x, y = zstate(s1, fx1, fy1)
            d = max(round(v1 - v0, 3), 0.1)
            ease = 'power2.inOut' if d < 1.5 else 'sine.inOut'
            if k == 0:  # the cut lands on the segment's first framing, then moves
                js.append(f'tl.fromTo("#zoom", {{scale: {st[0]}, x: {st[1]}, y: {st[2]}}}, {{scale: {sc}, x: {x}, y: {y}, duration: {d}, ease: "{ease}", immediateRender: false}}, {c(v0)});')
            else:
                js.append(f'tl.to("#zoom", {{scale: {sc}, x: {x}, y: {y}, duration: {d}, ease: "{ease}"}}, {c(v0)});')

    # facecam bubble over every screen run
    el.append(f'<div id="bubble"><div class="ring"></div><div class="mask"><video id="thb" class="clip" data-layout-allow-overflow src="assets/th_cut.mp4" muted playsinline '
              f'data-start="{L}" data-duration="{VO_LEN}" data-track-index="4"></video></div></div>')
    js.append('tl.set("#bubble", {scale: 0, opacity: 0}, 0);')
    for a, b in runs:
        js.append(f'tl.to("#bubble", {{scale: 1, opacity: 1, duration: 0.45, ease: "back.out(1.6)"}}, {c(a) + 0.08});')
        js.append(f'tl.to("#bubble", {{scale: 0.6, opacity: 0, duration: 0.18, ease: "power3.in"}}, {c(b) - 0.18});')

    # full-frame result footage
    for bdef in BROLL:
        a, b = c(bdef['t0']), c(bdef['t1'])
        el.append(f'<div id="{bdef["id"]}w" class="ffw"><video id="{bdef["id"]}" class="clip" src="assets/{bdef["src"]}" muted playsinline '
                  f'data-start="{a}" data-duration="{round(b - a, 3)}" data-media-start="{bdef["ms"]}" data-track-index="{track()}"></video></div>')
        js.append(f'tl.fromTo("#{bdef["id"]}w", {{scale: 1.08}}, {{scale: 1.0, duration: {round(b - a, 3)}, ease: "none"}}, {a});')

    # address bar: morphs open from the logo, types "topview.ai" with the voice, presses enter, leaves with the cut
    chars = 'topview.ai'
    el.append(f'<div id="urlbar" class="clip" data-start="{c(URL_ON)}" data-duration="{round(URL_OFF - URL_ON, 3)}" data-track-index="{track()}">'
              f'<div class="ubw"><div class="ubbg"></div><div class="ubshine"></div>'
              f'<div class="ubin"><span class="ubicon"><img src="assets/logo_sym_white.png"/></span>'
              f'<span class="ublock">https://</span><span class="ubtxt">{chars}</span><b class="ubcaret"></b></div>'
              f'<span class="ubgo">&#8629;</span></div></div>')
    js.append(f'tl.fromTo("#urlbar .ubbg", {{scaleX: 0.16, opacity: 0}}, {{scaleX: 1, opacity: 1, duration: 0.5, ease: "expo.out"}}, {c(URL_ON)});')
    js.append(f'tl.fromTo("#urlbar .ubicon", {{scale: 0, rotation: -40}}, {{scale: 1, rotation: 0, duration: 0.45, ease: "back.out(2)"}}, {c(URL_ON)});')
    js.append(f'tl.fromTo("#urlbar .ublock", {{opacity: 0, x: -10}}, {{opacity: 0.55, x: 0, duration: 0.3, ease: "expo.out"}}, {c(URL_ON) + 0.18});')
    js.append(f'tl.fromTo("#urlbar .ubtxt", {{clipPath: "inset(0 100% 0 0)"}}, {{clipPath: "inset(0 0% 0 0)", duration: {URL_TYPE[1] - URL_TYPE[0]:.3f}, ease: "steps({len(chars)})"}}, {c(URL_TYPE[0])});')
    js.append(f'tl.fromTo("#urlbar .ubcaret", {{opacity: 0}}, {{opacity: 1, duration: 0.05, ease: "none"}}, {c(URL_TYPE[1])});')
    js.append(f'tl.fromTo("#urlbar .ubgo", {{opacity: 0, scale: 0.6}}, {{opacity: 1, scale: 1, duration: 0.3, ease: "back.out(2)"}}, {c(URL_TYPE[1]) - 0.42});')
    js.append(f'tl.to("#urlbar .ubgo", {{scale: 0.82, duration: 0.07, ease: "power2.in"}}, {c(URL_ENTER)});')
    js.append(f'tl.to("#urlbar .ubgo", {{scale: 1, backgroundColor: "#8a4dff", duration: 0.25, ease: "back.out(3)"}}, {c(URL_ENTER) + 0.07});')
    js.append(f'tl.fromTo("#urlbar .ubshine", {{x: -220, opacity: 0}}, {{x: 640, opacity: 1, duration: 0.42, ease: "power2.inOut"}}, {c(URL_ENTER)});')
    js.append(f'tl.to("#urlbar .ubw", {{opacity: 0, scale: 0.96, filter: "blur(8px)", duration: 0.15, ease: "power2.in"}}, {c(URL_OFF) - 0.15});')

    # synthetic cursor for Topview's canvas page (it hides ours): glides between the measured click points
    vcur_html = ('<div id="vcur" data-layout-allow-overflow><svg width="38" height="38" viewBox="0 0 24 24">'
                 '<path d="M4 2 L4 19 L8.5 14.8 L11.6 21.6 L14.4 20.4 L11.4 13.7 L17.5 13.7 Z" fill="#fff" stroke="#111" '
                 'stroke-width="1.3" stroke-linejoin="round"/></svg></div>')
    el = [e.replace('__VCUR__', vcur_html) for e in el]
    TIPX, TIPY = 6.3, 3.2
    js.append('tl.set("#vcur", {opacity: 0}, 0);')
    for i, s_ in enumerate(SEG):
        if not s_['cur']:
            js.append(f'tl.set("#vcur", {{opacity: 0}}, {c(s_["t0"])});')
            continue
        wp = [(src2v(s_['id'], t), x, y) for t, x, y in s_['cur']]
        x0, y0 = wp[0][1], wp[0][2]
        for (va, xa, ya), (vb, xb, yb) in zip(wp, wp[1:]):
            if va <= s_['t0'] <= vb:
                f_ = (s_['t0'] - va) / max(vb - va, 1e-6)
                x0, y0 = xa + (xb - xa) * f_, ya + (yb - ya) * f_
            elif s_['t0'] > vb:
                x0, y0 = xb, yb
        js.append(f'tl.set("#vcur", {{opacity: 1, x: {x0 - TIPX:.1f}, y: {y0 - TIPY:.1f}}}, {c(s_["t0"])});')
        for (va, xa, ya), (vb, xb, yb) in zip(wp, wp[1:]):
            if vb <= s_['t0'] or va >= s_['t1']:
                continue
            st = max(va, s_['t0'])
            d = min(vb, s_['t1']) - st
            if d > 0.02:
                js.append(f'tl.to("#vcur", {{x: {xb - TIPX:.1f}, y: {yb - TIPY:.1f}, duration: {d:.3f}, ease: "power2.inOut"}}, {c(st)});')
        nxt = SEG[i + 1] if i + 1 < len(SEG) else None
        if not nxt or not nxt['cur'] or abs(nxt['t0'] - s_['t1']) > 0.05:
            js.append(f'tl.set("#vcur", {{opacity: 0}}, {c(s_["t1"])});')

    # cold-open logo
    el.append(f'<div id="logo0" class="clip" data-start="0.05" data-duration="{L - 0.07}" data-track-index="{track()}">'
              f'<img src="assets/logo_h_white.png"/></div>')
    js.append('tl.fromTo("#logo0 img", {opacity: 0, scale: 0.82, filter: "blur(14px)"}, {opacity: 1, scale: 1, filter: "blur(0px)", duration: 0.45, ease: "expo.out"}, 0.1);')
    js.append(f'tl.to("#logo0 img", {{opacity: 0, scale: 1.08, filter: "blur(10px)", duration: 0.2, ease: "power3.in"}}, {L - 0.28});')

    # pop-up pills
    for pid, on, off, inner, pos in POPS:
        el.append(f'<div id="{pid}" class="clip popw" style="{pos}" data-start="{c(on)}" data-duration="{round(off - on, 3)}" '
                  f'data-track-index="{track()}"><div class="pill">{inner}</div></div>')
        js.append(f'tl.fromTo("#{pid} .pill", {{opacity: 0, y: 14, filter: "blur(6px)"}}, {{opacity: 1, y: 0, filter: "blur(0px)", duration: 0.32, ease: "expo.out"}}, {c(on)});')
        js.append(f'tl.to("#{pid} .pill", {{opacity: 0, filter: "blur(6px)", duration: 0.15, ease: "power2.in"}}, {c(off) - 0.15});')

    # model chips row ("any model Topview offers")
    chips = ''.join(f'<span class="mc" id="mc{i}">{m}</span>' for i, m in enumerate(MODELS))
    el.append(f'<div id="models" class="clip" data-start="{c(MODEL_T)}" data-duration="{round(10.55 - MODEL_T, 3)}" data-track-index="{track()}">{chips}</div>')
    for i in range(len(MODELS)):
        js.append(f'tl.fromTo("#mc{i}", {{opacity: 0, y: 18}}, {{opacity: 1, y: 0, duration: 0.3, ease: "expo.out"}}, {c(MODEL_T) + i * 0.09});')

    # prompt card synced to the voice reading it
    pw = [w for w in WORDS if 19.25 <= w['s'] <= 30.7]
    spans = ''.join(f'<span class="pw" id="pw{i}">{w["w"].replace("Top View", "Topview")} </span>' for i, w in enumerate(pw))
    el.append(f'<div id="prompt" class="clip" data-start="{c(19.2)}" data-duration="{round(30.66 - 19.2, 3)}" data-track-index="{track()}">'
              f'<div class="pc"><div class="ph"><img src="assets/logo_sym_white.png" class="ic"/>PROMPT · Topview T1</div><div class="pt">{spans}<b class="caret"></b></div></div></div>')
    js.append(f'tl.fromTo("#prompt .pc", {{opacity: 0, y: -24, scale: 0.96}}, {{opacity: 1, y: 0, scale: 1, duration: 0.4, ease: "expo.out"}}, {c(19.2)});')
    for i, w in enumerate(pw):
        js.append(f'tl.fromTo("#pw{i}", {{opacity: 0.14}}, {{opacity: 1, duration: 0.12}}, {c(w["s"])});')
    js.append(f'tl.to("#prompt .pc", {{opacity: 0, y: -16, duration: 0.18, ease: "power2.in"}}, {c(30.66) - 0.18});')

    # settings chips accumulate
    chs = ''.join(f'<span class="sc" id="sc{i}">{t}</span>' for i, (t, _) in enumerate(CHIPS))
    el.append(f'<div id="setchips" class="clip" data-start="{c(CHIPS[0][1])}" data-duration="{round(38.95 - CHIPS[0][1], 3)}" data-track-index="{track()}">{chs}</div>')
    for i, (_, t) in enumerate(CHIPS):
        js.append(f'tl.fromTo("#sc{i}", {{opacity: 0, scale: 0.6}}, {{opacity: 1, scale: 1, duration: 0.35, ease: "back.out(2)"}}, {c(t)});')
    el.append(f'<div id="cost" class="clip" data-start="{c(GEN_T)}" data-duration="{round(38.95 - GEN_T, 3)}" data-track-index="{track()}"><div class="pill hot">22 credits</div></div>')
    js.append(f'tl.fromTo("#cost .pill", {{opacity: 0, scale: 0.6}}, {{opacity: 1, scale: 1, duration: 0.3, ease: "back.out(2)"}}, {c(GEN_T)});')

    # summary cards over the talking head, then the lockup
    cards = ''.join(f'<div class="sumc" id="sum{i}"><div class="st">{a}</div><div class="ss">{b}</div></div>' for i, (a, b, _) in enumerate(SUM))
    el.append(f'<div id="summary" class="clip" data-start="{c(SUM[0][2])}" data-duration="{round(ROOF_T - SUM[0][2] + 0.25, 3)}" data-track-index="{track()}">{cards}</div>')
    for i, (*_, t) in enumerate(SUM):
        js.append(f'tl.fromTo("#sum{i}", {{opacity: 0, x: 60, filter: "blur(8px)"}}, {{opacity: 1, x: 0, filter: "blur(0px)", duration: 0.4, ease: "expo.out"}}, {c(t)});')
    js.append(f'tl.to("#summary .sumc", {{opacity: 0, x: -30, duration: 0.2, stagger: 0.04, ease: "power3.in"}}, {c(ROOF_T) - 0.05});')
    end_d = round(TOTAL - c(ROOF_T), 3)
    el.append(f'<div id="lockup" class="clip" data-start="{c(ROOF_T)}" data-duration="{end_d}" data-track-index="{track()}">'
              f'<div class="lk"><img src="assets/logo_h_white.png"/><div class="lks">Canvas · AI Marketer · 12+ models</div></div></div>')
    js.append(f'tl.fromTo("#lockup", {{backgroundColor: "rgba(4,6,16,0)"}}, {{backgroundColor: "rgba(4,6,16,0.72)", duration: 0.35}}, {c(ROOF_T)});')
    js.append(f'tl.fromTo("#lockup img", {{opacity: 0, scale: 0.85, filter: "blur(12px)"}}, {{opacity: 1, scale: 1, filter: "blur(0px)", duration: 0.5, ease: "expo.out"}}, {c(ROOF_T) + 0.1});')
    js.append(f'tl.fromTo("#lockup .lks", {{opacity: 0, y: 12}}, {{opacity: 1, y: 0, duration: 0.4, ease: "expo.out"}}, {c(ROOF_T) + 0.35});')

    el.append(f'<img id="wm" class="clip" src="assets/sd_watermark.png" alt="" data-start="0" data-duration="{TOTAL}" data-track-index="{track()}"/>')
    el.append(f'<audio id="mix" src="assets/mix.wav" data-start="0" data-duration="{TOTAL}" data-track-index="1" data-volume="1"></audio>')

    css = f'''
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ width: 1920px; height: 1080px; overflow: hidden; background: #04060f; }}
      #root {{ position: relative; width: 1920px; height: 1080px; overflow: hidden; background: #04060f; font-family: "Inter", sans-serif; }}
      #bg {{ position: absolute; inset: -40px; width: 2000px; height: 1160px; object-fit: cover; }}
      #thwrap {{ position: absolute; inset: 0; transform-origin: 50% 32%; }}
      #thv {{ position: absolute; inset: 0; width: 1920px; height: 1080px; object-fit: cover; }}
      #card {{ position: absolute; left: {CARD['x']}px; top: {CARD['y']}px; width: {CARD['w']}px; height: {CARD['h']}px;
               border-radius: 22px; overflow: hidden; background: #000;
               box-shadow: 0 0 0 1.5px rgba(150,180,255,.28), 0 30px 90px rgba(0,0,0,.65), 0 0 120px rgba(40,110,255,.25); }}
      #zoom {{ position: absolute; left: 0; top: 0; width: 1920px; height: 1080px; transform-origin: 0 0; }}
      #scr {{ position: absolute; left: 0; top: 0; width: 1920px; height: 1080px; }}
      .hl {{ position: absolute; }}
      .hl i {{ position: absolute; inset: 0; border-radius: 12px; border: 3px solid #8fb2ff;
               box-shadow: 0 0 0 4px rgba(110,140,255,.25), 0 0 26px 6px rgba(90,130,255,.75), inset 0 0 18px rgba(120,150,255,.35);
               background: rgba(110,140,255,.08); }}
      .hl.round i {{ border-radius: 50%; }}
      .hl.soft i {{ border-color: rgba(143,178,255,.6); box-shadow: 0 0 30px 4px rgba(90,130,255,.45); background: transparent; }}
      #bubble {{ position: absolute; left: 1560px; top: 790px; width: 270px; height: 270px; transform-origin: 50% 50%; }}
      #bubble .mask {{ position: absolute; inset: 0; border-radius: 50%; overflow: hidden; background: #0b1020; }}
      #bubble .ring {{ position: absolute; inset: -6px; border-radius: 50%;
                       background: conic-gradient(from 200deg, #3b82ff, #8fb2ff, #6d5cff, #3b82ff);
                       box-shadow: 0 0 40px rgba(70,130,255,.8); }}
      #thb {{ position: absolute; width: 806px; height: 453px; left: -268px; top: -18px; }}
      .ffw {{ position: absolute; inset: 0; }}
      .ffw video {{ position: absolute; inset: 0; width: 1920px; height: 1080px; object-fit: cover; }}
      #logo0 {{ position: absolute; inset: 0; display: flex; align-items: center; justify-content: center;
                background: radial-gradient(ellipse at 50% 55%, rgba(0,0,0,0) 0%, rgba(0,0,0,.55) 75%); }}
      #logo0 img {{ width: 820px; filter: drop-shadow(0 0 40px rgba(140,120,255,.6)); }}
      .popw {{ position: absolute; }}
      .pill {{ display: inline-flex; align-items: center; gap: 14px; padding: 16px 28px; border-radius: 999px;
               background: rgba(12,16,34,.86); border: 1.5px solid rgba(143,178,255,.55);
               box-shadow: 0 10px 40px rgba(0,0,0,.5), 0 0 30px rgba(70,120,255,.35);
               color: #fff; font-weight: 800; font-size: 40px; letter-spacing: -0.5px; white-space: nowrap; }}
      .pill .dim {{ color: #9fb4e8; font-weight: 600; }}
      .pill.hot {{ background: linear-gradient(90deg, #5b5cff, #8a4dff); border-color: rgba(255,255,255,.4); font-size: 34px; padding: 12px 24px; }}
      .ic {{ width: 40px; height: 40px; }}
      .spin {{ width: 26px; height: 26px; border-radius: 50%; border: 4px solid rgba(255,255,255,.25); border-top-color: #8fb2ff; }}
      #p_core .pill {{ font-size: 56px; padding: 18px 34px; letter-spacing: 1px; }}
      #models {{ position: absolute; left: 210px; top: 860px; width: 1300px; display: flex; flex-wrap: wrap; gap: 14px; }}
      .mc {{ padding: 12px 22px; border-radius: 14px; background: rgba(12,16,34,.9); border: 1.5px solid rgba(143,178,255,.45);
             color: #e8eeff; font-weight: 700; font-size: 30px; box-shadow: 0 0 22px rgba(70,120,255,.3); }}
      #mc0 {{ background: linear-gradient(90deg, #5b5cff, #8a4dff); color: #fff; border-color: rgba(255,255,255,.45); }}
      #prompt {{ position: absolute; left: 0; right: 0; top: 96px; display: flex; justify-content: center; }}
      .pc {{ width: 1380px; padding: 26px 36px 30px; border-radius: 26px; background: rgba(10,14,30,.9);
             border: 2px solid rgba(120,150,255,.7); box-shadow: 0 0 0 6px rgba(80,110,255,.18), 0 0 60px rgba(70,120,255,.55), 0 24px 70px rgba(0,0,0,.6); }}
      .ph {{ display: flex; align-items: center; gap: 12px; color: #9fb4e8; font-weight: 700; font-size: 28px; letter-spacing: 2px; margin-bottom: 12px; }}
      .ph .ic {{ width: 30px; height: 30px; }}
      .pt {{ color: #fff; font-weight: 600; font-size: 38px; line-height: 1.32; }}
      .caret {{ display: inline-block; width: 3px; height: 38px; background: #8fb2ff; vertical-align: -6px; }}
      #setchips {{ position: absolute; left: 210px; top: 108px; display: flex; gap: 14px; }}
      .sc {{ padding: 12px 24px; border-radius: 14px; background: rgba(12,16,34,.9); border: 2px solid rgba(143,178,255,.7);
             color: #fff; font-weight: 800; font-size: 36px; box-shadow: 0 0 26px rgba(70,120,255,.45); }}
      #cost {{ position: absolute; left: 1290px; top: 110px; }}
      #summary {{ position: absolute; right: 90px; top: 210px; width: 600px; display: flex; flex-direction: column; gap: 22px; }}
      .sumc {{ padding: 24px 32px; border-radius: 22px; background: rgba(10,14,30,.84); border: 1.5px solid rgba(143,178,255,.5);
               box-shadow: 0 0 40px rgba(70,120,255,.35), 0 20px 60px rgba(0,0,0,.5); }}
      .st {{ color: #fff; font-weight: 800; font-size: 50px; letter-spacing: -1px; }}
      .ss {{ color: #9fb4e8; font-weight: 600; font-size: 32px; margin-top: 2px; }}
      #lockup {{ position: absolute; inset: 0; display: flex; align-items: center; justify-content: center; }}
      .lk {{ display: flex; flex-direction: column; align-items: center; gap: 26px; }}
      .lk img {{ width: 760px; filter: drop-shadow(0 0 40px rgba(140,120,255,.6)); }}
      .lks {{ color: #c9d6ff; font-weight: 700; font-size: 38px; letter-spacing: 1px; }}
      #urlbar {{ position: absolute; left: 84px; top: 420px; }}
      .ubw {{ position: relative; width: 600px; height: 96px; }}
      .ubbg {{ position: absolute; inset: 0; border-radius: 999px; background: rgba(9,12,28,.9); border: 2px solid rgba(143,178,255,.65);
               box-shadow: 0 0 0 6px rgba(80,110,255,.16), 0 0 50px rgba(70,120,255,.5), 0 24px 60px rgba(0,0,0,.55); transform-origin: 48px 50%; }}
      .ubshine {{ position: absolute; top: 6px; left: 0; width: 120px; height: 84px; border-radius: 999px;
                  background: linear-gradient(90deg, rgba(255,255,255,0), rgba(180,200,255,.28), rgba(255,255,255,0)); }}
      .ubin {{ position: absolute; left: 0; top: 0; height: 96px; display: flex; align-items: center; padding-left: 20px; }}
      .ubicon {{ width: 54px; height: 54px; border-radius: 50%; background: linear-gradient(135deg, #5b5cff, #8a4dff);
                 display: flex; align-items: center; justify-content: center; margin-right: 20px; box-shadow: 0 0 24px rgba(120,100,255,.7); }}
      .ubicon img {{ width: 36px; height: 36px; }}
      .ublock {{ color: #9fb4e8; font-weight: 600; font-size: 34px; margin-right: 2px; }}
      .ubtxt {{ color: #fff; font-weight: 800; font-size: 46px; letter-spacing: -1px; }}
      .ubcaret {{ display: inline-block; width: 4px; height: 44px; background: #8fb2ff; margin-left: 4px; }}
      .ubgo {{ position: absolute; right: 20px; top: 20px; width: 56px; height: 56px; border-radius: 16px; background: rgba(110,140,255,.25);
               border: 1.5px solid rgba(143,178,255,.6); color: #fff; font-size: 36px; font-weight: 800; display: flex; align-items: center; justify-content: center; }}
      #vcur {{ position: absolute; left: 0; top: 0; width: 38px; height: 38px; filter: drop-shadow(0 2px 3px rgba(0,0,0,.5)); }}
      #wm {{ position: absolute; left: 34px; bottom: 26px; width: 120px; opacity: .75; }}
    '''
    doc = f'''<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1920, height=1080" />
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
    <style>{css}</style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{TOTAL}" data-width="1920" data-height="1080">
      <img id="bg" class="clip" src="assets/bg.jpg" alt="" data-start="0" data-duration="{TOTAL}" data-track-index="0" />
      {chr(10).join("      " + e for e in el)}
    </div>
    <script>
      window.__timelines = window.__timelines || {{}};
      const tl = gsap.timeline({{ paused: true }});
      tl.fromTo("#bg", {{ x: 0, scale: 1 }}, {{ x: -30, scale: 1.03, duration: {TOTAL}, ease: "none" }}, 0);
      {chr(10).join("      " + j for j in js)}
      tl.set({{}}, {{}}, {TOTAL});
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
'''
    open(os.path.join(ROOT, 'film', 'index.html'), 'w', encoding='utf-8').write(doc)
    print('html ok, total', TOTAL, 'elements', len(el))


if __name__ == '__main__':
    steps = sys.argv[1:] or ['assets', 'screen', 'audio', 'html']
    speeds()
    if 'assets' in steps: build_assets()
    if 'screen' in steps: build_screen()
    if 'audio' in steps: build_audio()
    if 'html' in steps: build_html()
