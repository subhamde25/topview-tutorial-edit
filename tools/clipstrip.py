# usage: python -I tools/clipstrip.py <rec> <start> <dur> <x> <y> <w> <h> <out.jpg>  — 20 fps timestamped crop strip
import subprocess, sys
rec, a, d, x, y, w, h, out = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), *map(int, sys.argv[4:8]), sys.argv[8]
src = f'rec/{rec}_cfr.mp4'
n = int(d * 20); cols = 8; rows = (n + cols - 1) // cols
vf = (f"fps=20,crop={w}:{h}:{x}:{y},scale=-1:150,drawtext=fontfile='C\\:/Windows/Fonts/arialbd.ttf':text='%{{pts\\:flt\\:{a}}}':"
      f"x=4:y=4:fontsize=18:fontcolor=yellow:box=1:boxcolor=black@0.7,tile={cols}x{rows}")
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', str(a), '-t', str(d), '-i', src, '-vf', vf, '-frames:v', '1', out], check=True)
