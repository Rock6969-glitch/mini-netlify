import os
import zipfile
import uuid
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI()

UPLOAD_DIR = "published_sites"
os.makedirs(UPLOAD_DIR, exist_ok=True)

app.mount("/sites", StaticFiles(directory=UPLOAD_DIR), name="sites")

@app.get("/", response_class=HTMLResponse)
async def index():
    # index.html があればそれを返す（なければ url.html を返すように調整）
    target_file = "index.html" if os.path.exists("index.html") else "url.html"
    if os.path.exists(target_file):
        with open(target_file, "r", encoding="utf-8") as f:
            return f.read()
    return "<h3>HTMLファイルが見つかりません。</h3>"

@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    if not file.filename.endswith(".zip"):
        raise HTTPException(status_code=400, detail="ZIPファイルのみ対応しています。")
    
    site_id = str(uuid.uuid4())[:8]
    site_dir = os.path.join(UPLOAD_DIR, site_id)
    os.makedirs(site_dir, exist_ok=True)
    
    zip_path = os.path.join(site_dir, "temp.zip")
    with open(zip_path, "wb") as buffer:
        buffer.write(await file.read())
        
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(site_dir)
        
    os.remove(zip_path)
    
    access_url = f"/sites/{site_id}/index.html"
    return JSONResponse({"url": access_url})