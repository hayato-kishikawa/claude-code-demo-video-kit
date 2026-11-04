"""ジョブ JSON を gpt-image-2.5 系で 10 並列生成する（generate-image スキルの genimg.py を使う）。既存ファイルはスキップ。
使い方: （プロジェクト直下で）set -a && . <repo>/.env && set +a && python3 run_images.py job1.json [job2.json ...]
job JSON: {"out_dir": "...", "size": "2048x1152", "quality": "high", "deployment": "<任意。省略時は IMAGE_DEPLOYMENT>",
           "style": "<接頭辞>", "images": [{"name","prompt","quality"?}]}
出力は <out_dir>/<name>.png。バックグラウンドは setsid nohup で。"""
import json, os, sys, time, importlib.util
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _client
from concurrent.futures import ThreadPoolExecutor, as_completed
GENIMG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "generate-image", "scripts", "genimg.py")
spec = importlib.util.spec_from_file_location("genimg", GENIMG)
g = importlib.util.module_from_spec(spec); spec.loader.exec_module(g)
base, key = g._env()
tasks = []
for fn in sys.argv[1:]:
    job = json.load(open(fn))
    for im in job["images"]:
        out = os.path.join(job["out_dir"], im["name"] + ".png")
        if os.path.exists(out): print("skip", im["name"], flush=True); continue
        tasks.append((im["name"], job["style"] + im["prompt"], job["out_dir"], job["size"], im.get("quality") or job["quality"],
                      job.get("deployment") or _client.image_model()))
print("tasks", len(tasks), flush=True)
def run(t):
    name, prompt, out_dir, size, q, model = t; t0 = time.time()
    try:
        r = g.generate(name, prompt, out_dir, size, model, 0, base, key, quality=q)
        _client.log("image", name=name, model=model, sku=_client.sku("image"), size=size, quality=q,
                    wall_s=round(time.time()-t0, 1), usage=r.get("usage"))
        return f"ok {name} {time.time()-t0:.0f}s"
    except Exception as e:
        return f"FAIL {name} {e!r}"
with ThreadPoolExecutor(max_workers=10) as ex:
    for f in as_completed([ex.submit(run, t) for t in tasks]): print(f.result(), flush=True)
