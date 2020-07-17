FROM debian:buster
RUN apt-get update \
  && apt-get install -qy \
  default-jre-headless \
  iputils-ping \
  libexpat1 \
  openssh-client \
  procps \
  python3 \
  tcpdump \
  telnet \
  git \
  vim \
  python3-pip \
  xmlstarlet \
  && apt-get -qy autoremove \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/* /root/.cache \
  && update-alternatives --install /usr/bin/python python /usr/bin/python3 \
  && update-alternatives --install /usr/bin/pip pip /usr/bin/pip3

# This needs to be set based on what you download and where you put it.
# Then uncomment these next four lines.
#COPY $NSO_INSTALL_FILE /tmp/nso_installer.bin
#COPY setup_ncs.sh /tmp/setup_ncs.sh
#RUN sh /tmp/nso_installer.bin /opt/ncs
#RUN sh /tmp/setup_ncs.sh

CMD ["/bin/bash"]
