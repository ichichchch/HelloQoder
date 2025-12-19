# Stage 1: Build
FROM mcr.microsoft.com/dotnet/sdk:9.0 AS build
WORKDIR /src

# 复制项目文件并恢复依赖 (利用缓存)
COPY ["MindMates.sln", "./"]
COPY ["MindMates.Api/MindMates.Api.csproj", "MindMates.Api/"]
COPY ["MindMates.Application/MindMates.Application.csproj", "MindMates.Application/"]
COPY ["MindMates.Domain/MindMates.Domain.csproj", "MindMates.Domain/"]
COPY ["MindMates.Infrastructure/MindMates.Infrastructure.csproj", "MindMates.Infrastructure/"]

# 恢复依赖（dotnet restore 也可以配置源，但通常海外源在构建机上尚可）
RUN dotnet restore

# 复制全量代码并发布
COPY . .
WORKDIR /src/MindMates.Api
RUN dotnet publish -c Release -o /app/publish --no-restore

# Stage 2: Runtime
FROM mcr.microsoft.com/dotnet/aspnet:9.0 AS runtime
WORKDIR /app

# 🔧 修复关键：统一使用 bookworm 源，不再跨版本使用 trixie
RUN sed -i 's/deb.debian.org/mirrors.tuna.tsinghua.edu.cn/g' /etc/apt/sources.list.d/debian.sources || \
    sed -i 's/deb.debian.org/mirrors.tuna.tsinghua.edu.cn/g' /etc/apt/sources.list && \
    echo 'Acquire::Retries "3";' > /etc/apt/apt.conf.d/80-retries && \
    apt-get update && \
    apt-get install -y --no-install-recommends wget && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# 创建用户与权限设置
RUN adduser --disabled-password --gecos '' appuser
COPY --from=build /app/publish .
RUN chown -R appuser:appuser /app

USER appuser

# 环境变量优化
ENV ASPNETCORE_URLS=http://+:5000 \
    ASPNETCORE_ENVIRONMENT=Production \
    # 注意：如果你的应用涉及多语言处理（如日期格式化），请慎用 INVARIANT=1
    DOTNET_SYSTEM_GLOBALIZATION_INVARIANT=1 

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:5000/health || exit 1

ENTRYPOINT ["dotnet", "MindMates.Api.dll"]
