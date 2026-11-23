"""Find every click in a Cap recording from the fake cursor's violet click ripple (tools/pw_lib.inc.js).

The ripple is unmistakable in time: a violet ring ~14 px wide appears, stays centred, grows to ~44 px
over ~0.35 s and fades by ~0.45 s. Static purple UI (badges, buttons, banners) never grows like that.

python -I tools/detect_clicks.py [rec ...]   -> build/clicks.json  {rec: [[t, x, y], ...]}
t = recording seconds of the first ripple frame (the mousedown), x/y = recording pixels of its centre.
"""
import collections, json, os, subprocess, sys
import cv2
import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
REC = lambda r: os.path.join(ROOT, 'rec', f'{r}_cfr.mp4')
RANGES = {'r1': [(14, 31)], 'r1b': [(10, 34)], 'r1c': [(10, 22)], 'r1d': [(14, 32), (95, 127)],
          'r2': [(10, 100)], 'r3': [(8, 38)], 'r2b': [(10, 22)]}
FPS, S = 60, 2
W, H = 1920 // S, 1080 // S
OUT = os.path.join(ROOT, 'build', 'clicks.json')
AHEAD = 22                      # frames of future needed to verify (~0.37 s)


def violet_mask(f):
    f = f.astype(np.int16)                      # BGR
    return (f[..., 0] - (f[..., 1] + f[..., 2]) // 2) > 12


def box_in(m, cx, cy, r=30):
    x0, y0 = max(cx - r, 0), max(cy - r, 0)
    ys, xs = np.nonzero(m[y0:cy + r, x0:cx + r])
    if len(xs) < 4:
        return None
    return xs.min() + x0, ys.min() + y0, xs.max() + x0, ys.max() + y0, len(xs)


def scan(rec, a, b):
    cmd = ['ffmpeg', '-v', 'error', '-ss', str(a), '-t', str(b - a), '-i', REC(rec), '-vf', f'fps={FPS},scale={W}:{H}',
           '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-']
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    buf = collections.deque()          # (index, mask)
    cands, clicks, i, last = [], [], 0, -1e9
    kernel = np.ones((5, 5), np.uint8)
    while True:
        raw = p.stdout.read(W * H * 3)
        if len(raw) < W * H * 3:
            break
        m = violet_mask(np.frombuffer(raw, np.uint8).reshape(H, W, 3))
        if buf:
            prev = buf[-1][1]
            new = m & ~cv2.dilate(prev.astype(np.uint8), kernel).astype(bool)
            n, lab, st, cen = cv2.connectedComponentsWithStats(new.astype(np.uint8), 8)
            for k in range(1, n):
                x, y, w, h, area = st[k]
                if 3 <= w <= 14 and 3 <= h <= 14 and area >= 6:
                    cands.append((i, int(cen[k][0]), int(cen[k][1]), max(w, h)))
        buf.append((i, m))
        while len(buf) > AHEAD + 2:
            buf.popleft()
        # verify candidates that now have enough future frames
        keep = []
        for (ci, cx, cy, s0) in cands:
            if i - ci < AHEAD:
                keep.append((ci, cx, cy, s0)); continue
            frames = {j: mm for j, mm in buf}
            b6, b18 = box_in(frames.get(ci + 6, m), cx, cy), box_in(frames.get(ci + 18, m), cx, cy)
            ok = False
            if b6 and b18:
                s6 = max(b6[2] - b6[0], b6[3] - b6[1]); s18 = max(b18[2] - b18[0], b18[3] - b18[1])
                c18 = ((b18[0] + b18[2]) / 2, (b18[1] + b18[3]) / 2)
                ok = s6 >= s0 + 3 and s18 >= s6 + 3 and abs(c18[0] - cx) < 6 and abs(c18[1] - cy) < 6
            if ok and ci - last > 0.3 * FPS:
                clicks.append([round(a + ci / FPS, 3), cx * S, cy * S]); last = ci
        cands = keep
        i += 1
    p.wait()
    return clicks


if __name__ == '__main__':
    res = json.load(open(OUT)) if os.path.exists(OUT) else {}
    for rec in (sys.argv[1:] or RANGES):
        res[rec] = [c for a, b in RANGES[rec] for c in scan(rec, a, b)]
        print(rec, res[rec])
    json.dump(res, open(OUT, 'w'), indent=1)
