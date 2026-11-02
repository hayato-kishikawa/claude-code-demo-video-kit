"""gpt-realtime-2 を TTS として使い、1 文を 24kHz mono の wav にする。接続先は _client.py（PROVIDER）。
使い方: python3 rt_tts.py "読み上げ文" out.wav [voice=marin]"""
import asyncio, json, base64, os, sys, time, wave
import websockets
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _client
async def tts(text, out, voice="marin"):
    t0 = time.time(); usage = None
    async with websockets.connect(_client.realtime_url(), additional_headers=_client.headers(), max_size=None) as ws:
        await ws.send(json.dumps({"type":"session.update","session":{"type":"realtime","output_modalities":["audio"],
            "instructions":"あなたはナレーターです。ユーザーが送る日本語の文章を、一字一句そのまま、落ち着いた明瞭なナレーション調で読み上げてください。前置き・相槌・追加の言葉は一切禁止。",
            "audio":{"output":{"voice":voice,"format":{"type":"audio/pcm","rate":24000}}}}}))
        await ws.send(json.dumps({"type":"conversation.item.create","item":{"type":"message","role":"user","content":[{"type":"input_text","text":text}]}}))
        await ws.send(json.dumps({"type":"response.create"}))
        pcm=bytearray(); transcript=""
        while True:
            m=json.loads(await ws.recv()); t=m.get("type","")
            if t=="response.output_audio.delta": pcm+=base64.b64decode(m["delta"])
            elif t=="response.output_audio_transcript.done": transcript=m.get("transcript","")
            elif t=="error": print("ERROR", m, file=sys.stderr); break
            elif t=="response.done": usage=m.get("response",{}).get("usage"); break
        with wave.open(out,"wb") as w:
            w.setnchannels(1); w.setsampwidth(2); w.setframerate(24000); w.writeframes(bytes(pcm))
        res={"out":out,"seconds":len(pcm)/2/24000,"transcript":transcript}
        _client.log("tts", model=_client.realtime_model(), chars=len(text), audio_s=round(res["seconds"],2),
                    wall_s=round(time.time()-t0,1), usage=usage)
        print(json.dumps(res,ensure_ascii=False))
        return res
if __name__=="__main__":
    asyncio.run(tts(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv)>3 else "marin"))
