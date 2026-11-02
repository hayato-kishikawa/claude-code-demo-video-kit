"""gpt-realtime-2 に音声を聞かせ、指定フレーズの発音を評価させる（TTS 出力の耳代わり。参考値）。
使い方: python3 rt_listen.py <wav> ["質問"]"""
import asyncio, json, base64, os, sys, subprocess
import websockets
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _client
def pcm24k(path):
    return subprocess.run(["ffmpeg","-loglevel","error","-i",path,"-f","s16le","-ac","1","-ar","24000","-"],capture_output=True,check=True).stdout
async def listen(path, question):
    pcm=pcm24k(path)
    async with websockets.connect(_client.realtime_url(), additional_headers=_client.headers(), max_size=None) as ws:
        await ws.send(json.dumps({"type":"session.update","session":{"type":"realtime","output_modalities":["text"],
            "instructions":"あなたは日本語ナレーションの音声品質を審査する審査員です。送られた音声を注意深く聞き、質問に日本語で簡潔に答えてください。",
            "audio":{"input":{"format":{"type":"audio/pcm","rate":24000}}}}}))
        await ws.send(json.dumps({"type":"conversation.item.create","item":{"type":"message","role":"user","content":[
            {"type":"input_audio","audio":base64.b64encode(pcm).decode()},{"type":"input_text","text":question}]}}))
        await ws.send(json.dumps({"type":"response.create"}))
        text=""
        while True:
            m=json.loads(await ws.recv()); t=m.get("type","")
            if t=="response.output_text.delta": text+=m.get("delta","")
            elif t=="error": print("ERROR", m, file=sys.stderr); break
            elif t=="response.done": break
        return text
if __name__=="__main__":
    q=sys.argv[2] if len(sys.argv)>2 else "この音声を聞こえたままカタカナで書き起こし、ナレーションとして不自然な読み・間・詰まりがないかを 1〜5 で採点し（5=自然）、問題があれば一言で理由を書いてください。形式: 『聞こえ: …／採点: N／理由: …』"
    print(asyncio.run(listen(sys.argv[1], q)))
