FROM python:3

# 安装必要的软件包，包括 wireguard-tools 和 docker-ce-cli
RUN apt-get update && \
    apt-get install -y ca-certificates curl gnupg && \
    install -d /etc/apt/keyrings && \
    curl -fsSL 'https://download.docker.com/linux/debian/gpg' -o /etc/apt/keyrings/docker.asc && \
    chmod a+r /etc/apt/keyrings/docker.asc && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/debian \
    $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null && \
    apt-get update && \
    apt-get install -y wireguard-tools docker-ce-cli && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# 安装python相关依赖 \
RUN pip install Flask

COPY main.py /app/main.py

WORKDIR /app
CMD python main.py
