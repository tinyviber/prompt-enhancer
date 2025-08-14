from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware # 导入CORS中间件
import os

from api.endpoints import router as api_router
from services.state_manager import state_manager

# 定义前端文件所在的目录
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")

app = FastAPI(title="Local Memory Manager")

# --- 中间件配置 ---

# 1. CORS 中间件 (重要!)
# 允许所有来源，这在本地开发中是安全的
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. 检查服务是否启用的中间件
@app.middleware("http")
async def check_service_enabled(request: Request, call_next):
    # 对API路由和静态文件/根路径放行
    if request.url.path.startswith("/api") or request.url.path == "/" or "." in request.url.path:
         # 对 /enable 接口本身放行
        if request.url.path == "/api/enable" or state_manager.is_enabled():
            response = await call_next(request)
            return response
        
        # 如果服务被禁用，但请求是API请求（非enable），则返回错误
        if request.url.path.startswith("/api"):
             return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={"detail": "Service is disabled via /api/enable endpoint."},
            )
    
    # 对于所有非API请求（主要是前端资源），直接放行
    return await call_next(request)


# --- API 路由 ---
# 将我们的API路由挂载到 /api 前缀下，与前端路由区分
app.include_router(api_router, prefix="/api")

# --- 静态文件服务 ---

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# 2. 创建一个根路由，以确保访问 http://127.0.0.1:8000 时返回 index.html
@app.get("/", include_in_schema=False)
async def read_index():
    index_path = os.path.join(STATIC_DIR, "index.html")
    if not os.path.exists(index_path):
         raise HTTPException(status_code=404, detail="index.html not found")
    return FileResponse(index_path)