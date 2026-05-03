#!/bin/bash
set -eu

#*****************************************************************************************************************
#
# インストール後、初回起動時のみ実行される処理
#
# 役割:
#   1. Calamares が残したキーボード設定を整理
#   2. gjsosk / dconf /  を最終レイアウトに合わせて修正
#   3. インストーラ関連パッケージを削除
#   4. autoremove / clean を実行
#   5. 自分自身を無効化
#
# 想定:
#   - systemd の oneshot service として root で実行
#   - そのため sudo は使わない
#
#*****************************************************************************************************************

STAMP_FILE="/var/lib/oYo/firstboot.done"
LOG_TAG="oYo-firstboot"

KEYBD="/etc/default/keyboard"
XORG="/etc/X11/xorg.conf.d/00-keyboard.conf"
GJSOSK_DCONF="/etc/dconf/db/local.d/10-gjsosk"
INPUT_SOURCES_DCONF="/etc/dconf/db/local.d/10-input-sources"
SESSION_DCONF="/etc/dconf/db/local.d/20-session"

SERVICE_NAME="firstboot.service"

log() {
    echo "[$LOG_TAG] $*"
}

# すでに完了済みなら何もしない
if [ -e "$STAMP_FILE" ]; then
    log "already completed: $STAMP_FILE"
    exit 0
fi

mkdir -p /var/lib/oYo

#----------------------------------------------------------------------------------------------------------------
# 1) 現在のキーボード設定を読み込む
#    Calamares で "us,jp" のように入ることがあるため、末尾要素を採用する
#----------------------------------------------------------------------------------------------------------------
XKBMODEL="pc105"
XKBLAYOUT="jp"

if [ -f "$KEYBD" ]; then
    # shellcheck disable=SC1090
    . "$KEYBD"
fi

IFS=',' read -r -a LAYOUTS <<< "${XKBLAYOUT:-jp}"
FINAL_LAYOUT="${LAYOUTS[${#LAYOUTS[@]}-1]:-${XKBLAYOUT:-jp}}"

log "keyboard layout: '${XKBLAYOUT:-}' -> '${FINAL_LAYOUT}' (model: ${XKBMODEL:-pc105})"

#----------------------------------------------------------------------------------------------------------------
# 2) gjsosk のレイアウトを設定
#    jp のとき: 11
#    それ以外: 10
#----------------------------------------------------------------------------------------------------------------
if [ "$FINAL_LAYOUT" = "jp" ]; then
    GJSOSK_LAYOUT_VAL=11
else
    GJSOSK_LAYOUT_VAL=10
fi

log "gjsosk layout => $GJSOSK_LAYOUT_VAL"

mkdir -p "$(dirname "$GJSOSK_DCONF")"
cat > "$GJSOSK_DCONF" <<EOF
[org/gnome/shell/extensions/gjsosk]
layout-landscape=$GJSOSK_LAYOUT_VAL
layout-portrait=$GJSOSK_LAYOUT_VAL
EOF

#----------------------------------------------------------------------------------------------------------------
# 3) /etc/default/keyboard を更新
#----------------------------------------------------------------------------------------------------------------
if [ -f "$KEYBD" ]; then
    if grep -q '^XKBLAYOUT=' "$KEYBD"; then
        sed -E -i "s/^XKBLAYOUT=.*/XKBLAYOUT=\"${FINAL_LAYOUT}\"/" "$KEYBD"
    else
        echo "XKBLAYOUT=\"${FINAL_LAYOUT}\"" >> "$KEYBD"
    fi

    if grep -q '^XKBMODEL=' "$KEYBD"; then
        sed -E -i "s/^XKBMODEL=.*/XKBMODEL=\"${XKBMODEL}\"/" "$KEYBD"
    else
        echo "XKBMODEL=\"${XKBMODEL}\"" >> "$KEYBD"
    fi
else
    mkdir -p "$(dirname "$KEYBD")"
    cat > "$KEYBD" <<EOF
XKBMODEL="${XKBMODEL}"
XKBLAYOUT="${FINAL_LAYOUT}"
EOF
fi

#----------------------------------------------------------------------------------------------------------------
# 4) /etc/X11/xorg.conf.d を生成
#----------------------------------------------------------------------------------------------------------------
mkdir -p "$(dirname "$XORG")"
cat > "$XORG" <<EOF
Section "InputClass"
    Identifier "Keyboard defaults"
    MatchIsKeyboard "on"
    Option "XkbModel"   "${XKBMODEL}"
    Option "XkbLayout"  "${FINAL_LAYOUT}"
EndSection
EOF

#----------------------------------------------------------------------------------------------------------------
# 5) dconf の input sources を更新
#----------------------------------------------------------------------------------------------------------------
if [ -f "$INPUT_SOURCES_DCONF" ]; then
    tmp="$(mktemp)"
    sed -E "s/'xkb', '[^']*'/'xkb', '${FINAL_LAYOUT}'/g" "$INPUT_SOURCES_DCONF" > "$tmp"
    mv "$tmp" "$INPUT_SOURCES_DCONF"
fi

#----------------------------------------------------------------------------------------------------------------
# 5.5) dconf のスクリーンロック / アイドル設定を追加
#----------------------------------------------------------------------------------------------------------------
mkdir -p "$(dirname "$SESSION_DCONF")"
cat > "$SESSION_DCONF" <<EOF
[org/gnome/desktop/screensaver]
lock-enabled=true
lock-delay=uint32 0

[org/gnome/desktop/session]
idle-delay=uint32 300
EOF

# dconf DB 更新
if command -v dconf >/dev/null 2>&1; then
    dconf update || true
fi

#----------------------------------------------------------------------------------------------------------------
# 6) インストーラ関連パッケージを削除
#    post-install ではなく firstboot で実行する
#----------------------------------------------------------------------------------------------------------------
log "purging installer packages"

APT_GET="apt-get -y -o Dpkg::Use-Pty=0"

# 存在するものだけ削除したいので、失敗しても継続
$APT_GET purge oyo-calamares gparted calamares calamares-settings-debian || true

#----------------------------------------------------------------------------------------------------------------
# 7) 不要依存を整理
#----------------------------------------------------------------------------------------------------------------
log "autoremove purge"
$APT_GET autoremove --purge || true

# 任意: パッケージキャッシュ整理
log "clean apt cache"
apt-get clean || true

#----------------------------------------------------------------------------------------------------------------
# 8) 完了印を作成
#----------------------------------------------------------------------------------------------------------------
date > "$STAMP_FILE"

#----------------------------------------------------------------------------------------------------------------
# 9) 自分自身を無効化
#----------------------------------------------------------------------------------------------------------------
log "disabling ${SERVICE_NAME}"
systemctl disable "$SERVICE_NAME" || true

# 念のため service ファイルを消したい場合は下を有効化
# rm -f "/etc/systemd/system/${SERVICE_NAME}"
# systemctl daemon-reload || true

log "completed"
exit 0
