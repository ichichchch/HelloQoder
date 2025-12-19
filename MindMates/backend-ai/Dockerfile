# MindMates AI Backend Dockerfile
FROM python:3.13-slim

WORKDIR /app

# 🔧 修复 apt-get：使用 sed 替换现有源（适配新旧两种 Debian 源格式）
RUN sed -i 's/deb.debian.org/mirrors.tuna.tsinghua.edu.cn/g' /etc/apt/sources.list.d/debian.sources || \
    sed -i 's/deb.debian.org/mirrors.tuna.tsinghua.edu.cn/g' /etc/apt/sources.list && \
    echo 'Acquire::Retries "3";' > /etc/apt/apt.conf.d/80-retries && \
    apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# 创建非 root 用户
RUN adduser --disabled-password --gecos '' appuser

# 复制依赖文件并安装 (使用清华源)
COPY requirements.txt .
RUN pip install --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt

# 复制应用代码
COPY . .
RUN chown -R appuser:appuser /app

USER appuser

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONFAULTHANDLER=1

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
