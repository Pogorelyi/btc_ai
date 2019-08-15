FROM centos:7.5.1804

RUN yum install -y epel-release \
    && yum update -y \
    && yum install -y python36 python36-libs python36-devel python36-setuptools \
    libargon2 wget git2u supervisor vim tmux pv nc htop gettext mc zip unzip sudo \
    thrift tkinter tk-devel mysql gcc libcurl-devel openssl-devel

RUN easy_install-3.6 pip
RUN pip install --upgrade pip setuptools
RUN pip install pipenv
RUN pip install tensorflow
RUN pip install numpy
RUN pip install requests
RUN pip install bitmex-ws

ARG UNAME=bitmex
ARG UID=1001
ARG GID=1001
RUN groupadd -g $GID bitmex \
    && useradd -u $UID -g $GID bitmex \
    && echo '%bitmex ALL=(ALL) NOPASSWD:ALL' > /etc/sudoers \
    && chown -R bitmex:bitmex /home/bitmex \
    && mkdir -p /home/bitmex/.local/bin/

RUN ln -s /usr/local/bin/pipenv /home/bitmex/.local/bin/pipenv

ENV LC_ALL=en_US.utf8 \
 LANG=en_US.utf8 \
 PIPENV_VENV_IN_PROJECT=1 \
 PYCURL_SSL_LIBRARY=openssl \
 LDFLAGS=-L/usr/local/opt/openssl/lib \
 CPPFLAGS=-I/usr/local/opt/openssl/include

EXPOSE 8185/tcp

CMD supervisord -n
#ENTRYPOINT ["top", "-b"]
#CMD ["-c"]