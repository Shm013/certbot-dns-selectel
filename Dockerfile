# Docker Arch (amd64, arm32v6, ...)
ARG TARGET_ARCH
ARG CERTBOT_VERSION
FROM certbot/certbot:${TARGET_ARCH}-v${CERTBOT_VERSION}

ARG PLUGIN_NAME
ARG PLUGIN_VERSION

# Retrieve Certbot DNS plugin code
RUN wget -O certbot-${PLUGIN_NAME}-${PLUGIN_VERSION}.tar.gz https://github.com/shm013/certbot-dns-selectel/archive/v${PLUGIN_VERSION}.tar.gz \
 && tar xf certbot-${PLUGIN_NAME}-${PLUGIN_VERSION}.tar.gz \
 && cp -r certbot-${PLUGIN_NAME}-${PLUGIN_VERSION} /opt/certbot/src/certbot-${PLUGIN_NAME} \
 && rm -rf certbot-${PLUGIN_NAME}-${PLUGIN_VERSION}.tar.gz certbot-${PLUGIN_NAME}-${PLUGIN_VERSION}

# Install the DNS plugin
RUN pip install --constraint /opt/certbot/docker_constraints.txt --no-cache-dir --editable /opt/certbot/src/certbot-${PLUGIN_NAME}
