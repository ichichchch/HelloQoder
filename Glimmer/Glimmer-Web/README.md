# GLIMMER Web - Backend

GLIMMER GUI Automation Agent 后端服务。

## 安装

```bash
cd Glimmer-Web
pip install -r requirements.txt
```

## 运行

```bash
# 启动 API 服务
python server.py --port 5000
```

## API 端点

- `GET /api/health` - 健康检查
- `GET /api/screenshot` - 获取当前屏幕截图
- `POST /api/execute` - 执行一步操作
- `POST /api/reset` - 重置代理状态
- `POST /api/config` - 更新配置
