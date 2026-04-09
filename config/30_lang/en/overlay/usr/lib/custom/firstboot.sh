#!/bin/bash
set -e

LOG_TAG="oYo-firstboot"
SESSION_DCONF="/etc/dconf/db/local.d/20-session"

log() {
    echo "[$LOG_TAG] $*"
}

log "English environment: minimal firstboot tasks"

#------------------------------------------------------------
# Configure GNOME screen lock / idle defaults
#------------------------------------------------------------
mkdir -p "$(dirname "$SESSION_DCONF")"
cat > "$SESSION_DCONF" <<EOF
[org/gnome/desktop/screensaver]
lock-enabled=true
lock-delay=uint32 0

[org/gnome/desktop/session]
idle-delay=uint32 300
EOF

if command -v dconf >/dev/null 2>&1; then
    dconf update || true
fi

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
