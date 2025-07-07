import pathlib
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from contextlib import asynccontextmanager

from app.api import vocabulary, quiz, auth
from app.scripts.import_words import import_words_if_empty
from app.db.mongodb import db
from app.db.init import create_indexes

# ─── 1. Locate the client/build directory ───────────────────────
PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[2]  # → .../server
BUILD_DIR    = PROJECT_ROOT / "client" / "build"
STATIC_DIR   = BUILD_DIR / "static"
INDEX_FILE   = BUILD_DIR / "index.html"

# ─── 2. Lifespan hook: initialize database at startup ────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 startup: import words and create indexes…")
    await import_words_if_empty()
    await create_indexes(db)
    yield
    print("🛑 shutdown")

# ─── 3. Create FastAPI application ──────────────────────────────
app = FastAPI(
    title="Te Reo Māori Learning API",
    version="1.0.0",
    lifespan=lifespan,
)

# ─── 4. Mount static files ─────────────────────────────────────
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# ─── 5. Include application routers ────────────────────────────
app.include_router(vocabulary.router, prefix="/vocabulary", tags=["Vocabulary"])
app.include_router(quiz.router,       prefix="/quiz",       tags=["Quiz"])
app.include_router(auth.router,       prefix="/auth",       tags=["Authentication"])

# ─── 6. Root path: serve the React frontend index ──────────────
@app.get("/", response_class=HTMLResponse)
async def serve_index():
    # Debug: print whether index.html exists
    exists = INDEX_FILE.exists()
    print(f"serve_index → {INDEX_FILE} exists? {exists}")
    if not exists:
        raise HTTPException(status_code=500, detail="index.html not found")
    return HTMLResponse(INDEX_FILE.read_text(encoding="utf-8"))

# ─── 7. SPA catch-all: return index for any unmatched frontend route ─
@app.get("/{full_path:path}", response_class=HTMLResponse)
async def spa_catchall(full_path: str):
    # These prefixes are handled by FastAPI or static files
    allowed_prefixes = (
        "static",       # static assets
        "vocabulary",   # API routes
        "quiz",
        "auth",
        "docs",         # Swagger UI
        "openapi.json", # OpenAPI spec
        "redoc",        # Redoc UI
    )
    if full_path.startswith(allowed_prefixes):
        # Delegate to FastAPI for 404 or docs
        raise HTTPException(status_code=404)
    # Otherwise serve the frontend index
    return HTMLResponse(INDEX_FILE.read_text(encoding="utf-8"))
