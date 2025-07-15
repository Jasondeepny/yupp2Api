# 使用官方Python 3.11镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
# RUN apt-get update && apt-get install -y \
#     curl \
#     && rm -rf /var/lib/apt/lists/*

# 复制requirements文件并安装Python依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY yyapi.py .

# 创建配置文件目录
RUN mkdir -p /app/config

# 暴露端口
EXPOSE 8001

# 设置环境变量
ENV PYTHONUNBUFFERED=1
ENV DEBUG_MODE=false

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8001/models || exit 1

# 启动命令
CMD ["python", "yyapi.py"] 