#!/usr/bin/env bash


set -o errexit
set -o nounset
set -o pipefail

KUBE_ROOT=$(pwd)

KUBERNETES_RELEASE_URL="${KUBERNETES_RELEASE_URL:-https://storage.googleapis.com/kubernetes-release/release}"
KUBERNETES_RELEASE=v1.5.1
KUBERNETES_DOWNLOAD_URL_PREFIX="${KUBERNETES_RELEASE_URL}/${KUBERNETES_RELEASE}"

CLIENT_PLATFORM="linux"
CLIENT_ARCH="amd64"


function download_tarball() {
  local -r download_path="$1"
  local -r file="$2"
  local -r url_prefix="$3"
  url="${url_prefix}/${file}"
  mkdir -p "${download_path}"
  if [[ $(which curl) ]]; then
    curl -fL --retry 3 --keepalive-time 2 "${url}" -o "${download_path}/${file}"
  elif [[ $(which wget) ]]; then
    wget "${url}" -O "${download_path}/${file}"
  else
    echo "Couldn't find curl or wget.  Bailing out." >&2
    exit 4
  fi
  # TODO: add actual verification
}

CLIENT_TAR="kubernetes-client-${CLIENT_PLATFORM}-${CLIENT_ARCH}.tar.gz"

echo "Kubernetes release: ${KUBERNETES_RELEASE}"
echo "Client: ${CLIENT_PLATFORM}/${CLIENT_ARCH}"
echo

# download client tar

if [ ! -f ${KUBE_ROOT}/${CLIENT_TAR} ]; then
    DOWNLOAD_CLIENT_TAR=true
    echo "Will download  ${CLIENT_TAR} from ${KUBERNETES_DOWNLOAD_URL_PREFIX}"
fi


if "${DOWNLOAD_CLIENT_TAR}"; then
  download_tarball "${KUBE_ROOT}" "${CLIENT_TAR}" "${KUBERNETES_DOWNLOAD_URL_PREFIX}"
fi

## extract binaries 

mkdir ${KUBE_ROOT}/client
tar xvf ${KUBE_ROOT}/${CLIENT_TAR}    --strip-components 3 -C ${KUBE_ROOT}/client
