# backend/utils.py
import hashlib, time, os, httpx, dotenv, pathlib

# 读取 .env
BASE_DIR = pathlib.Path(__file__).resolve().parents[1]
dotenv.load_dotenv(BASE_DIR / ".env")

AUTH_KEY    = os.getenv("AUTH_KEY")
AUTH_SECRET = os.getenv("AUTH_SECRET")
HOST        = os.getenv("HOST", "").rstrip("/")

def _gen_headers() -> dict:
    ts  = str(int(time.time() * 1000))
    md5 = hashlib.md5((AUTH_KEY + AUTH_SECRET + ts).encode()).hexdigest()
    return {"authKey": AUTH_KEY, "timestamp": ts, "sign": md5}

async def agentify_sync(prompt: str) -> str:
    """
    调用 Agentify 同步接口，返回 content 字符串
    """
    url = f"{HOST}/openapi/agents/chat/completions/v1"
    payload = {
        "agentId": AUTH_KEY,      # 如有独立 agentId 请替换
        "chatId" : None,
        "userChatInput": prompt,
        "state": {},
        "debug": False
    }

    async with httpx.AsyncClient() as cli:
        r = await cli.post(url, headers=_gen_headers(), json=payload, timeout=30)
        r.raise_for_status()
        data = r.json()
        if isinstance(data.get("choices"), list) and data["choices"]:
            return data["choices"][0].get("content", "")
        raise RuntimeError("Agentify 返回空结果")
