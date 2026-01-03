# GLIMMER UI - Frontend

Vue 前端界面，与 GLIMMER Web 后端配合使用。

## 安装

```bash
cd Glimmer-UI
npm install
```

## 运行

```bash
# 开发模式
npm run dev

# 或使用启动脚本
./start.bat  # Windows
./start.sh   # Linux/macOS
```

## 构建

```bash
npm run build
```

## 配置

开发服务器默认运行在 `http://localhost:3000`，API 请求会代理到 `http://localhost:5000`（Glimmer-Web 后端）。

## 完整运行

1. 启动后端：
```bash
cd ../Glimmer-Web
python server.py --port 5000
```

2. 启动前端：
```bash
cd ../Glimmer-UI
npm run dev
```

3. 访问 http://localhost:3000
