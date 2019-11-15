#!/bin/bash
set -ex

# Current supported architectures
export ALL_TARGET_ARCH=(amd64 arm32v6 arm64v8)

# Architecture used in tags with no architecture especified (certbot/certbot:latest, certbot/cerbot:v0.35.0, ...)
export DEFAULT_ARCH=amd64

# Returns certbot version (ex. v0.35.0 returns 0.35.0)
# Usage: GetCerbotVersionFromTag <DOCKER_VERSION>
GetCerbotVersionFromTag() {
    TAG=$1
    echo "${TAG//v/}"
}

# Builds docker certbot plugin image for a specific architecture and certbot version (ex. 0.35.0).
# Usage: BuildDockerPluginImage [amd64|arm32v6|arm64v8] <CERTBOT_VERSION> <PLUGIN_NAME>
BuildDockerPluginImage() {
    ARCH=$1
    VERSION=$2
    PLUGIN=$3
    PLUGIN_VERSION=$4

    docker build \
        --build-arg CERTBOT_VERSION="${VERSION}" \
        --build-arg TARGET_ARCH="${ARCH}" \
        --build-arg PLUGIN_NAME="${PLUGIN}" \
        --build-arg PLUGIN_VERSION="${PLUGIN_VERSION}" \
        -f "${DOCKERFILE_PATH}" \
        -t certbot-dns-selectel \
        .
}

WORK_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"

CERTBOT_VERSION=0.40.1
PLUGIN_VERSION=0.0.1
PLUGIN_NAME="dns-selectel"

#for TARGET_ARCH in "${ALL_TARGET_ARCH[@]}"; do
#    BuildDockerPluginImage "${TARGET_ARCH}" "${CERTBOT_VERSION}" "${PLUGIN_NAME}"
#done

BuildDockerPluginImage "${DEFAULT_ARCH}" "${CERTBOT_VERSION}" "${PLUGIN_NAME}" "${PLUGIN_VERSION}"
