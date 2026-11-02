"""captions.json と index.html（<audio id="el-vo-XX" data-start=…>）から SRT を書き出す。
使い方: python3 export_srt.py <voice_dir> index.html renders/<name>.ja.srt"""
import json, re, sys
if len(sys.argv) < 4: print(__doc__); sys.exit(1)
vd, index, out = sys.argv[1].rstrip("/"), sys.argv[2], sys.argv[3]
caps = json.load(open(f"{vd}/captions.json")); html = open(index, encoding="utf-8").read()
starts = {m.group(1): float(m.group(2)) for m in re.finditer(r'id="el-vo-([A-Za-z0-9_-]+)"[^>]*data-start="([0-9.]+)"', html)}
def ts(t):
    h = int(t // 3600); m = int(t % 3600 // 60); s = t % 60
    return f"{h:02d}:{m:02d}:{int(s):02d},{int(round((s - int(s)) * 1000)):03d}"
rows, n = [], 0
for vid in sorted(starts, key=lambda v: starts[v]):
    for c in caps.get(vid, []):
        n += 1; rows.append(f"{n}\n{ts(starts[vid] + c['start'])} --> {ts(starts[vid] + c['end'])}\n{c['text']}\n")
open(out, "w", encoding="utf-8").write("\n".join(rows)); print(n, "cues ->", out)
