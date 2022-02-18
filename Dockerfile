# curl -sSL https://bootstrap.pypa.io/get-pip.py -o get-pip.py
FROM python:3.8-bullseye
LABEL maintainer="chaochinghua@outlook.com"
ARG apt_sources="deb http://mirrors.aliyun.com/debian/ bullseye main non-free contrib\
    \ndeb-src http://mirrors.aliyun.com/debian/ bullseye main non-free contrib\
    \ndeb http://mirrors.aliyun.com/debian-security/ bullseye-security main\
    \ndeb-src http://mirrors.aliyun.com/debian-security/ bullseye-security main\
    \ndeb http://mirrors.aliyun.com/debian/ bullseye-updates main non-free contrib\
    \ndeb-src http://mirrors.aliyun.com/debian/ bullseye-updates main non-free contrib\
    \ndeb http://mirrors.aliyun.com/debian/ bullseye-backports main non-free contrib\
    \ndeb-src http://mirrors.aliyun.com/debian/ bullseye-backports main non-free contrib"
ARG supervisord_conf="[supervisord]\
    \nnodaemon=true\
    \n[program:sshd]\
    \ncommand=/usr/sbin/sshd -D"
ARG sshd_conf="PermitRootLogin yes"
EXPOSE 22 8000
WORKDIR /home
# 配置 Debian 更新源
RUN mv /etc/apt/sources.list /etc/apt/sources.list.bak && \
    echo ${apt_sources} > /etc/apt/sources.list
RUN DEBIAN_FRONTEND=noninteractive apt-get update && \
    apt-get install -y openssh-server
RUN python3 -m pip install -i https://mirror.baidu.com/pypi/simple \
    tornado supervisor
RUN mkdir -p /var/run/sshd && mkdir -p /var/log/supervisor
# 设定 root 密码，添加 supervisor 和 SSH 配置
RUN echo root:123 |chpasswd && \
    echo_supervisord_conf > /etc/supervisord.conf && \
    echo ${supervisord_conf} >> /etc/supervisord.conf && \
    echo ${sshd_conf} >> /etc/ssh/sshd_config
CMD ["supervisord", "-c", "/etc/supervisord.conf"]
