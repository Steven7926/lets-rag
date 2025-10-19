from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from app.rag.router import router as rag_router
import httpx
from contextlib import asynccontextmanager
import os
from typing import Dict
from starlette.responses import StreamingResponse
from starlette.background import BackgroundTask
import logging


logging.basicConfig(
    level=logging.INFO
)
logger = logging.getLogger("api")

app = FastAPI()
OLLAMA = os.getenv("UPSTREAM_OLLAMA_URL", "http://ollama:11434")

app.include_router(
    rag_router, 
    prefix="/rag", 
    tags=["RAG"], 
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://open-webui:8080",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

HOP_BY_HOP = {
    "host","content-length","connection","keep-alive",
    "proxy-authenticate","proxy-authorization","te",
    "trailers","transfer-encoding","upgrade","content-encoding"
}

def strip_hop(headers: Dict[str, str]) -> Dict[str, str]:
    return {k: v for k, v in headers.items() if k.lower() not in HOP_BY_HOP}

@app.get("/health")
def health():
    return {"ok": True}

@app.api_route("/api/{subpath:path}", methods=["GET","POST","PUT","PATCH","DELETE"])
async def proxy(subpath: str, request: Request):
    upstream_url = f"{OLLAMA}/api/{subpath}"
    method = request.method
    
    fwd_headers = strip_hop(dict(request.headers))
    params = request.query_params
    content = await request.body() if method in {"POST","PUT","PATCH"} else None
    
    logger.info(f"here: {content}")
    timeout = httpx.Timeout(300.0, connect=10.0, read=300.0)
    
    client = httpx.AsyncClient(timeout=timeout, follow_redirects=True)
    
    try:
        req = client.build_request(method, upstream_url, headers=fwd_headers, params=params, content=content)
        resp = await client.send(req, stream=True)
        
        out_headers = strip_hop(dict(resp.headers))
        out_headers.setdefault("Cache-Control", "no-cache")
        out_headers.setdefault("X-Accel-Buffering", "no")
        
        async def stream_body():
            try:
                async for chunk in resp.aiter_raw():
                    yield chunk
            except Exception as e:
                print(f"Stream error: {e}")
                raise
            finally:
                await resp.aclose()
                await client.aclose()
        
        return StreamingResponse(
            stream_body(),
            status_code=resp.status_code,
            headers=out_headers,
            media_type=resp.headers.get("content-type", "application/json"),
        )
    except Exception as e:
        await client.aclose()
        raise