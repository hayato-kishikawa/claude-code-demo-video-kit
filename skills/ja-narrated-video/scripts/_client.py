"""接続先（Azure OpenAI / OpenAI API）の切り替えと、実測ログ（costs.jsonl）への追記。
  PROVIDER=azure（既定）: AZURE_OPENAI_BASE_URL=https://<resource>.openai.azure.com/openai/v1, AZURE_OPENAI_API_KEY（ヘッダ api-key）
  PROVIDER=openai       : OPENAI_API_KEY, OPENAI_BASE_URL（省略時 https://api.openai.com/v1）（ヘッダ Authorization: Bearer）
  モデル名（Azure ではデプロイ名）: IMAGE_DEPLOYMENT（既定 gpt-image-2.5-flare）, REALTIME_DEPLOYMENT（既定 gpt-realtime-2.1）
  Azure のデプロイ種別（費用の集計用）: IMAGE_SKU / REALTIME_SKU = GlobalStandard（既定）| DataZoneStandard
  COST_LOG: 実測ログの出力先（既定 ./costs.jsonl。プロジェクト直下で実行する）"""
import json, os, sys, time


def provider():
    return os.environ.get("PROVIDER", "azure").lower()


def base_url():
    if provider() == "openai":
        base, key = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1"), os.environ.get("OPENAI_API_KEY", "")
    else:
        base, key = os.environ.get("AZURE_OPENAI_BASE_URL", ""), os.environ.get("AZURE_OPENAI_API_KEY", "")
    if not base or not key:
        sys.exit(f"ERROR: PROVIDER={provider()} の接続先と鍵が環境変数にありません（.env.example を参照し `set -a; . ./.env; set +a`）")
    return base.rstrip("/")


def headers():
    if provider() == "openai":
        return {"Authorization": "Bearer " + os.environ["OPENAI_API_KEY"]}
    return {"api-key": os.environ["AZURE_OPENAI_API_KEY"]}


def image_model():
    return os.environ.get("IMAGE_DEPLOYMENT", "gpt-image-2.5-flare")


def realtime_model():
    return os.environ.get("REALTIME_DEPLOYMENT", "gpt-realtime-2.1")


def sku(kind):
    """費用の集計用。OpenAI API は GlobalStandard と同額として扱う"""
    if provider() == "openai":
        return "GlobalStandard"
    return os.environ.get({"image": "IMAGE_SKU", "tts": "REALTIME_SKU"}[kind], "GlobalStandard")


def realtime_url():
    # https://host/openai/v1 → wss://host/openai/v1/realtime?model=…（OpenAI も同じ形）
    return "wss://" + base_url().split("://", 1)[1] + "/realtime?model=" + realtime_model()


def log(kind, **kw):
    rec = {"ts": time.strftime("%Y-%m-%dT%H:%M:%S"), "kind": kind, "provider": provider(), **kw}
    with open(os.environ.get("COST_LOG", "costs.jsonl"), "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
