"""chrome-headless-shell を CDP で操作し、URL を開いて wait 秒後にスクショを撮る。
使い方: python cdp_shot.py URL out.png [w=1600] [h=1000] [wait=6] [scale=1]"""
import asyncio, base64, json, os, subprocess, sys, tempfile, time, urllib.request, glob
import websockets
url, out = sys.argv[1], sys.argv[2]
w, h = int(sys.argv[3]) if len(sys.argv) > 3 else 1600, int(sys.argv[4]) if len(sys.argv) > 4 else 1000
wait = float(sys.argv[5]) if len(sys.argv) > 5 else 6; scale = float(sys.argv[6]) if len(sys.argv) > 6 else 1
chrome = sorted(glob.glob(os.path.expanduser("~/.cache/hyperframes/chrome/chrome-headless-shell/*/*/chrome-headless-shell")))[-1]
port = 9333; prof = tempfile.mkdtemp()
p = subprocess.Popen([chrome, f"--remote-debugging-port={port}", f"--user-data-dir={prof}", "--disable-gpu", "--hide-scrollbars",
                      f"--window-size={w},{h}", "about:blank"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
try:
    for _ in range(50):
        try: tabs = json.load(urllib.request.urlopen(f"http://127.0.0.1:{port}/json")); break
        except Exception: time.sleep(0.2)
    ws_url = [t for t in tabs if t["type"] == "page"][0]["webSocketDebuggerUrl"]
    async def main():
        async with websockets.connect(ws_url, max_size=None) as ws:
            n = 0
            async def call(m, **params):
                nonlocal n; n += 1; i = n
                await ws.send(json.dumps({"id": i, "method": m, "params": params}))
                while True:
                    r = json.loads(await ws.recv())
                    if r.get("id") == i: return r.get("result", {})
            await call("Emulation.setDeviceMetricsOverride", width=w, height=h, deviceScaleFactor=scale, mobile=False)
            await call("Page.navigate", url=url)
            await asyncio.sleep(wait)
            r = await call("Page.captureScreenshot", format="png")
            open(out, "wb").write(base64.b64decode(r["data"]))
    asyncio.run(main()); print(out)
finally:
    p.terminate()
