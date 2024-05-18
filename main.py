from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import gzip
from models import vidsrctoget, vidsrcmeget, info, fetch
from io import BytesIO
from fastapi.responses import StreamingResponse
import logging

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# CORS Middleware (configure as needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this to your needs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get('/')
async def index():
    try:
        return await info()
    except Exception as e:
        logger.error(f"Error in index route: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get('/vidsrc/{dbid}')
async def vidsrc(dbid: str, s: int = None, e: int = None):
    if dbid:
        try:
            sources = await vidsrctoget(dbid, s, e)
            return {"status": 200, "info": "success", "sources": sources}
        except Exception as e:
            logger.error(f"Error in vidsrc route: {e}")
            raise HTTPException(status_code=500, detail="Internal Server Error")
    else:
        raise HTTPException(status_code=404, detail=f"Invalid id: {dbid}")

@app.get('/vsrcme/{dbid}')
async def vsrcme(dbid: str = '', s: int = None, e: int = None, l: str = 'eng'):
    if dbid:
        try:
            sources = await vidsrcmeget(dbid, s, e)
            return {"status": 200, "info": "success", "sources": sources}
        except Exception as e:
            logger.error(f"Error in vsrcme route: {e}")
            raise HTTPException(status_code=500, detail="Internal Server Error")
    else:
        raise HTTPException(status_code=404, detail=f"Invalid id: {dbid}")

@app.get('/streams/{dbid}')
async def streams(dbid: str = '', s: int = None, e: int = None, l: str = 'eng'):
    if dbid:
        try:
            sources = await vidsrcmeget(dbid, s, e) + await vidsrctoget(dbid, s, e)
            return {"status": 200, "info": "success", "sources": sources}
        except Exception as e:
            logger.error(f"Error in streams route: {e}")
            raise HTTPException(status_code=500, detail="Internal Server Error")
    else:
        raise HTTPException(status_code=404, detail=f"Invalid id: {dbid}")

@app.get("/subs")
async def subs(url: str):
    try:
        response = await fetch(url)
        with gzip.open(BytesIO(response.content), 'rt', encoding='utf-8') as f:
            subtitle_content = f.read()

        async def generate():
            yield subtitle_content.encode("utf-8")

        return StreamingResponse(generate(), media_type="application/octet-stream", headers={"Content-Disposition": "attachment; filename=subtitle.srt"})
    except Exception as e:
        logger.error(f"Error in subs route: {e}")
        raise HTTPException(status_code=500, detail="Error fetching subtitle")
