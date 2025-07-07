import pathlib
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from contextlib import asynccontextmanager

from app.api import vocabulary, quiz, auth
from app.scripts.import_words import import_words_if_empty
from app.db.mongodb import db
from app.db.init import create_indexes

# ─── 1. 定位 client/build ───────────────────────
# __file__ = .../server/app/main.py
PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[2]  # → .../server
PROJECT_ROOT = PROJECT_ROOT.parent                      # → project-root
BUILD_DIR    = PROJECT_ROOT / "client" / "build"
STATIC_DIR   = BUILD_DIR / "static"
INDEX_FILE   = BUILD_DIR / "index.html"

# ─── 2. 生命钩子（启动时初始化 DB）───────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 startup: import words and create indexes…")
    await import_words_if_empty()
    await create_indexes(db)
    yield
    print("🛑 shutdown")

# ─── 3. 创建应用 ─────────────────────────────────
app = FastAPI(
    title="Te Reo Māori Learning API",
    version="1.0.0",
    lifespan=lifespan,
)

# ─── 4. 挂载静态资源 ────────────────────────────
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# ─── 5. 挂载你的业务路由 ────────────────────────
app.include_router(vocabulary.router, prefix="/vocabulary", tags=["Vocabulary"])
app.include_router(quiz.router,       prefix="/quiz",       tags=["Quiz"])
app.include_router(auth.router,       prefix="/auth",       tags=["Authentication"])

# ─── 6. 根路径，返回前端首页 ────────────────────
@app.get("/", response_class=HTMLResponse)
async def serve_index():
    # 调试用：打印文件是否存在
    exists = INDEX_FILE.exists()
    print(f"serve_index → {INDEX_FILE} exists? {exists}")
    if not exists:
        raise HTTPException(status_code=500, detail="index.html not found")
    return HTMLResponse(INDEX_FILE.read_text(encoding="utf-8"))

# ─── 7. SPA 前端路由降级：剩余请求都返回 index.html ───
@app.get("/{full_path:path}", response_class=HTMLResponse)
async def spa_catchall(full_path: str):
    # 下面这些都放行，让 FastAPI 自己处理
    allowed_prefixes = (
        "static",       # 静态资源
        "vocabulary",   # API 路由
        "quiz",
        "auth",
        "docs",         # Swagger UI
        "openapi.json", # OpenAPI 描述
        "redoc",        # Redoc UI
    )
    if full_path.startswith(allowed_prefixes):
        # 交给 FastAPI 自己去返回 404 或者文档
        raise HTTPException(status_code=404)
    # 其它路径返回前端首页
    return HTMLResponse(INDEX_FILE.read_text(encoding="utf-8"))
