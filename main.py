from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import gzip
from models import vidsrctoget, vidsrcmeget, info, fetch
from io import BytesIO
from fastapi.responses import StreamingResponse
import logging

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update with specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.get('/')
async def index():
    return await info()

@app.get('/vidsrc/{dbid}')
async def vidsrc(dbid: str, s: int = None, e: int = None):
    if dbid:
        return {
            "status": 200,
            "info": "success",
            "sources": await vidsrctoget(dbid, s, e)
        }
    else:
        raise HTTPException(status_code=404, detail=f"Invalid id: {dbid}")

@app.get('/vsrcme/{dbid}')
async def vsrcme(dbid: str = '', s: int = None, e: int = None, l: str = 'eng'):
    if dbid:
        return {
            "status": 200,
            "info": "success",
            "sources": await vidsrcmeget(dbid, s, e)
        }
    else:
        raise HTTPException(status_code=404, detail=f"Invalid id: {dbid}")

@app.get('/streams/{dbid}')
async def streams(dbid: str = '', s: int = None, e: int = None, l: str = 'eng'):
    if dbid:
        return {
            "status": 200,
            "info": "success",
            "sources": await vidsrcmeget(dbid, s, e) + await vidsrctoget(dbid, s, e)
        }
    else:
        raise HTTPException(status_code=404, detail=f"Invalid id: {dbid}")

@app.get("/subs")
async def subs(url: str):
    try:
        response = await fetch(url)
        response.raise_for_status()  # Ensure we catch HTTP errors
        with gzip.open(BytesIO(response.content), 'rt', encoding='utf-8') as f:
            subtitle_content = f.read()

        async def generate():
            yield subtitle_content.encode("utf-8")

        return StreamingResponse(generate(), media_type="application/octet-stream", headers={"Content-Disposition": "attachment; filename=subtitle.srt"})

    except Exception as e:
        logger.error(f"Error fetching subtitle: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching subtitle: {e}")
