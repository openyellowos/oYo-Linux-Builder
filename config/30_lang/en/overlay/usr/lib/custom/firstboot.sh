#!/bin/bash
set -e

LOG_TAG="oYo-firstboot"

log() {
    echo "[$LOG_TAG] $*"
}

log "English environment: minimal firstboot tasks"

#------------------------------------------------------------
# インストーラ関連パッケージ削除
#------------------------------------------------------------
log "Removing installer packages"

apt-get -y purge \
    oyo-calamares \
    calamares \
    calamares-settings-debian \
    gparted || true

#------------------------------------------------------------
# 不要依存削除
#------------------------------------------------------------
log "Running autoremove"

apt-get -y autoremove --purge || true

#------------------------------------------------------------
# apt cache cleanup
#------------------------------------------------------------
apt-get clean || true

#------------------------------------------------------------
# 自分自身を無効化
#------------------------------------------------------------
log "Disabling firstboot.service"

systemctl disable firstboot.service || true

log "firstboot finished"

exit 0
