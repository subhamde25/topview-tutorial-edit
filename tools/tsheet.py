# usage: python -I tools/tsheet.py <video> <out.jpg> <start> <end> [step=1]  — timestamped contact sheet
import subprocess, sys
v, out, a, b = sys.argv[1], sys.argv[2], float(sys.argv[3]), float(sys.argv[4])
step = float(sys.argv[5]) if len(sys.argv) > 5 else 1.0
n = int((b - a) / step) + 1
cols = 6; rows = (n + cols - 1) // cols
vf = (f"fps=1/{step},scale=360:-1,drawtext=fontfile='C\:/Windows/Fonts/arialbd.ttf':text='%{{pts\:hms\:{a}}}':"
      f"x=6:y=6:fontsize=22:fontcolor=yellow:box=1:boxcolor=black@0.7,tile={cols}x{rows}")
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', str(a), '-t', str(b - a), '-i', v, '-vf', vf, '-frames:v', '1', out], check=True)
