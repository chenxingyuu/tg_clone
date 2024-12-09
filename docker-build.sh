#!/bin/bash

# 版本号文件路径
INIT_FILE="app/__init__.py"

# 检查文件是否存在
if [ ! -f "$INIT_FILE" ]; then
  echo "文件 $INIT_FILE 不存在，请确认路径。"
  exit 1
fi

# 提取版本号（兼容所有 grep 版本）
VERSION=$(grep '__version__' "$INIT_FILE" | sed -E 's/.*__version__\s*=\s*"([^"]+)".*/\1/')

# 检查是否成功提取版本号
if [ -z "$VERSION" ]; then
  echo "未能从 $INIT_FILE 中提取版本号，请检查 __version__ 的定义格式。"
  exit 1
fi

# 构建 Docker 镜像
IMAGE_NAME="tg_clone:$VERSION" # 将 myapp 替换为你的应用名
echo "正在构建 Docker 镜像: $IMAGE_NAME"

docker build -t "$IMAGE_NAME" .

if [ $? -eq 0 ]; then
  echo "Docker 镜像构建成功: $IMAGE_NAME"
else
  echo "Docker 镜像构建失败，请检查。"
  exit 1
fi