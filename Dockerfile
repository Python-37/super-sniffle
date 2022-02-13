# curl -sSL https://bootstrap.pypa.io/get-pip.py -o get-pip.py
FROM ubuntu:18.04
LABEL maintainer="chaochinghua@outlook.com"
ARG apt_sources="deb http://mirrors.aliyun.com/ubuntu/ bionic main multiverse restricted universe\
    \ndeb http://mirrors.aliyun.com/ubuntu/ bionic-backports main multiverse restricted universe\
    \ndeb http://mirrors.aliyun.com/ubuntu/ bionic-proposed main multiverse restricted universe\
    \ndeb http://mirrors.aliyun.com/ubuntu/ bionic-security main multiverse restricted universe\
    \ndeb http://mirrors.aliyun.com/ubuntu/ bionic-updates main multiverse restricted universe\
    \ndeb-src http://mirrors.aliyun.com/ubuntu/ bionic main multiverse restricted universe\
    \ndeb-src http://mirrors.aliyun.com/ubuntu/ bionic-backports main multiverse restricted universe\
    \ndeb-src http://mirrors.aliyun.com/ubuntu/ bionic-proposed main multiverse restricted universe\
    \ndeb-src http://mirrors.aliyun.com/ubuntu/ bionic-security main multiverse restricted universe\
    \ndeb-src http://mirrors.aliyun.com/ubuntu/ bionic-updates main multiverse restricted universe"
EXPOSE 8000
WORKDIR /home
COPY get-pip.py /home
RUN mv /etc/apt/sources.list /etc/apt/sources.list.bak && echo $apt_sources > /etc/apt/sources.list
RUN apt-get update && apt-get install -y software-properties-common
RUN add-apt-repository -y ppa:deadsnakes/ppa
RUN apt-get update && apt-get install -y python3.8 python3.8-distutils
RUN python3.8 ./get-pip.py --prefix=/usr/local/ -i https://mirror.baidu.com/pypi/simple
RUN python3.8 -m pip config set global.index-url https://mirror.baidu.com/pypi/simple
RUN python3.8 -m pip install tornado
