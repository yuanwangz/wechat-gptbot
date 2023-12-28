# 使用 Python 官方镜像作为基础镜像
FROM python:3.8

# 设置工作目录
WORKDIR /app

# 复制项目文件到工作目录
COPY . /app

# 安装项目依赖
RUN pip install -r requirements.txt

# 复制启动脚本到容器
COPY entrypoint.sh /app

# 使启动脚本可执行
RUN chmod +x /app/entrypoint.sh

# 设置容器启动时执行的命令
ENTRYPOINT ["/app/entrypoint.sh"]
