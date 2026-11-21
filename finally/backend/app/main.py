from pathlib import Path

from fastapi import FastAPI, HTTPException, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="Polecat")

_frontend = Path(__file__).resolve().parents[2] / "frontend" / "out"

if (_frontend / "_next").is_dir():
    app.mount("/_next", StaticFiles(directory=_frontend / "_next"), name="next-assets")


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/{path:path}")
def frontend(path: str):
    requested = _frontend / path
    if path and requested.is_file():
        return FileResponse(requested)

    index = _frontend / "index.html"
    if index.is_file():
        return FileResponse(index)

    raise HTTPException(status_code=404, detail="Frontend export not found")