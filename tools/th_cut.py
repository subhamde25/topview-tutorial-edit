"""Tighten the Topview talking head: every pause over 0.28 s becomes ~0.2 s.

python -I tools/th_cut.py   (run from marcus-ai-test/)
Writes build/th_cut.mp4 (1080p30, keyframe every 1 s), build/vo.wav, build/cutmap.json, build/words_cut.json.
"""
import json, os, re, subprocess

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
SRC = os.path.join(ROOT, 'raw', 'topview_th.mp4')
B = os.path.join(ROOT, 'build')
PAD = 0.10   # kept on each side of speech, so a cut pause ends up 2*PAD long
os.makedirs(B, exist_ok=True)

dur = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', SRC],
                           capture_output=True, text=True).stdout)
log = subprocess.run(['ffmpeg', '-hide_banner', '-i', SRC, '-af', 'silencedetect=n=-38dB:d=0.28', '-f', 'null', '-'],
                     capture_output=True, text=True).stderr
starts = [float(x) for x in re.findall(r'silence_start: ([\d.]+)', log)]
ends = [float(x) for x in re.findall(r'silence_end: ([\d.]+)', log)]
sil = list(zip(starts, ends))

# keep = speech regions with padding
keep, cur = [], 0.0
for s, e in sil:
    a, b = cur, min(s + PAD, dur)
    if b - a > 0.05:
        keep.append([round(a, 3), round(b, 3)])
    cur = max(e - PAD, b)
if dur - cur > 0.05:
    keep.append([round(cur, 3), round(dur, 3)])

segs, t = [], 0.0
for a, b in keep:
    segs.append({'src': [a, b], 'dst': round(t, 3)})
    t += b - a
total = round(t, 3)

fc, cat = [], ''
for i, (a, b) in enumerate(keep):
    d = b - a
    fc.append(f'[0:v]trim={a}:{b},setpts=PTS-STARTPTS,fps=30[v{i}]')
    fc.append(f'[0:a]atrim={a}:{b},asetpts=PTS-STARTPTS,afade=t=in:d=0.012,afade=t=out:st={max(d - 0.012, 0):.3f}:d=0.012[a{i}]')
    cat += f'[v{i}][a{i}]'
fc.append(f'{cat}concat=n={len(keep)}:v=1:a=1[v][a]')
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', SRC, '-filter_complex', ';'.join(fc), '-map', '[v]', '-map', '[a]',
                '-c:v', 'libx264', '-preset', 'medium', '-crf', '16', '-g', '30', '-pix_fmt', 'yuv420p',
                '-c:a', 'aac', '-b:a', '256k', os.path.join(B, 'th_cut.mp4')], check=True)
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', os.path.join(B, 'th_cut.mp4'), '-vn', '-ac', '2', '-ar', '48000',
                os.path.join(B, 'vo.wav')], check=True)


def remap(x):
    for s in segs:
        a, b = s['src']
        if a - 1e-3 <= x <= b + 1e-3:
            return round(s['dst'] + min(max(x, a), b) - a, 3)
    # inside a removed pause: snap to the next kept segment start
    nxt = [s for s in segs if s['src'][0] > x]
    return nxt[0]['dst'] if nxt else total


words = json.load(open(os.path.join(ROOT, 'notes', 'topview_words.json')))
wc = [{'w': w['w'], 's': remap(w['s']), 'e': remap(w['e'])} for w in words]
json.dump({'total': total, 'segs': segs}, open(os.path.join(B, 'cutmap.json'), 'w'), indent=1)
json.dump(wc, open(os.path.join(B, 'words_cut.json'), 'w'), indent=0)

# sentence table on the new timeline
out, buf, st = [], [], None
for w in wc:
    st = w['s'] if st is None else st
    buf.append(w['w'])
    if w['w'].endswith(('.', '?', '!')):
        out.append((st, w['e'], ' '.join(buf))); buf, st = [], None
for a, b, s in out:
    print(f'{a:6.2f}-{b:6.2f}  {s}')
print('segments', len(keep), 'total', total, 'from', round(dur, 2))
assert all(wc[i]['s'] <= wc[i + 1]['s'] for i in range(len(wc) - 1)), 'word times not monotonic'
