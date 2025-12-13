from fastapi import FastAPI
from app.api.v1.router import api_router

app = FastAPI(
    title="E-commerce Shopping Cart API",
    description="高性能电商购物车微服务",
    version="1.0.0"
)

app.include_router(api_router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {"status": "healthy"}
