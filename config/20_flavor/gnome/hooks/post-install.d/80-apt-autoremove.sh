#!/bin/bash
#
# apt autoremove + 古いカーネルの明示削除
#
# 【目的】
#   - apt autoremove は必ず実行する
#   - build用chroot内で古いカーネルが残るのを防ぐ
#   - ISO内 /boot に複数世代の kernel / initrd が残るのを防ぐ
#
# 【注意】
#   - uname -r は chroot 環境ではホスト側カーネルになるため使わない
#   - /vmlinuz のリンク先、または /boot/vmlinuz-* の最新版から残す版を決める
#

set -eu

echo "== 90-apt-autoremove.sh start =="

export DEBIAN_FRONTEND=noninteractive

# ----------------------------------------
# 残すカーネルバージョンを決定
# ----------------------------------------
KEEP_VERSION=""

# 1) /vmlinuz シンボリックリンクがあれば最優先で使う
if [ -L /vmlinuz ]; then
    TARGET="$(readlink -f /vmlinuz || true)"
    if [ -n "${TARGET}" ] && [ -e "${TARGET}" ]; then
        BASENAME="$(basename "${TARGET}")"
        case "${BASENAME}" in
            vmlinuz-*)
                KEEP_VERSION="${BASENAME#vmlinuz-}"
                ;;
        esac
    fi
fi

# 2) /vmlinuz で取れなければ /boot/vmlinuz-* の最新版を採用
if [ -z "${KEEP_VERSION}" ]; then
    CANDIDATE="$(ls -1 /boot/vmlinuz-* 2>/dev/null | sed 's#.*/vmlinuz-##' | sort -V | tail -n1 || true)"
    if [ -n "${CANDIDATE}" ]; then
        KEEP_VERSION="${CANDIDATE}"
    fi
fi

# 3) それでも取れなければ、インストール済み linux-image パッケージから最新版を採用
if [ -z "${KEEP_VERSION}" ]; then
    CANDIDATE="$(dpkg-query -W -f='${Package}\n' 'linux-image-[0-9]*-amd64' 2>/dev/null \
        | sed 's/^linux-image-//' \
        | sort -V \
        | tail -n1 || true)"
    if [ -n "${CANDIDATE}" ]; then
        KEEP_VERSION="${CANDIDATE}"
    fi
fi

if [ -z "${KEEP_VERSION}" ]; then
    echo "[WARN] keep対象の kernel version を特定できませんでした"
    echo "[WARN] 古い kernel の purge はスキップし、autoremove のみ実行します"
else
    echo "[INFO] keep kernel version: ${KEEP_VERSION}"

    # ----------------------------------------
    # purge対象パッケージを列挙
    # ----------------------------------------
    PURGE_LIST=""

    # linux-image-<version>-amd64
    for pkg in $(dpkg-query -W -f='${Package}\n' 'linux-image-[0-9]*-amd64' 2>/dev/null || true); do
        if [ "${pkg}" != "linux-image-${KEEP_VERSION}" ]; then
            PURGE_LIST="${PURGE_LIST} ${pkg}"
        fi
    done

    # linux-headers-<version>-amd64
    for pkg in $(dpkg-query -W -f='${Package}\n' 'linux-headers-[0-9]*-amd64' 2>/dev/null || true); do
        if [ "${pkg}" != "linux-headers-${KEEP_VERSION}" ]; then
            PURGE_LIST="${PURGE_LIST} ${pkg}"
        fi
    done

    # linux-headers-<version>-common
    for pkg in $(dpkg-query -W -f='${Package}\n' 'linux-headers-[0-9]*-common' 2>/dev/null || true); do
        case "${pkg}" in
            "linux-headers-${KEEP_VERSION%-amd64}-common")
                ;;
            *)
                PURGE_LIST="${PURGE_LIST} ${pkg}"
                ;;
        esac
    done

    # linux-modules-extra-<version>-amd64
    for pkg in $(dpkg-query -W -f='${Package}\n' 'linux-modules-extra-[0-9]*-amd64' 2>/dev/null || true); do
        if [ "${pkg}" != "linux-modules-extra-${KEEP_VERSION}" ]; then
            PURGE_LIST="${PURGE_LIST} ${pkg}"
        fi
    done

    # 重複除去
    PURGE_LIST="$(printf '%s\n' ${PURGE_LIST:-} | sed '/^$/d' | sort -u | xargs || true)"

    if [ -n "${PURGE_LIST}" ]; then
        echo "[INFO] purge old kernel packages:"
        for pkg in ${PURGE_LIST}; do
            echo "  - ${pkg}"
        done

        apt-get -y purge ${PURGE_LIST}
    else
        echo "[INFO] purge対象の old kernel package はありません"
    fi
fi

# ----------------------------------------
# autoremove 実行
# ----------------------------------------
echo "[INFO] apt-get autoremove --purge"
apt-get -y autoremove --purge

# ----------------------------------------
# 念のため /boot の状態を表示
# ----------------------------------------
echo "[INFO] /boot contents after purge/autoremove:"
ls -lh /boot || true

echo "== 90-apt-autoremove.sh done =="
