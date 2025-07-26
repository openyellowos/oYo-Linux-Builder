#!/bin/bash
set -e

#-----------------------------
#grubの背景設定
#-----------------------------
GRUB_FILE="/etc/default/grub"
THEME_IMG="/usr/share/desktop-base/custom-theme/grub/grub-16x9.png"

if [ -f "$GRUB_FILE" ] && [ -f "$THEME_IMG" ]; then
    sed -i '/^GRUB_BACKGROUND=/d' "$GRUB_FILE"
    echo "GRUB_BACKGROUND=\"$THEME_IMG\"" >> "$GRUB_FILE"
fi

#-----------------------------
# ライブ起動時のロックスクリーンの無効化を、元に戻す
#-----------------------------
gsettings set org.gnome.desktop.lockdown disable-lock-screen false

#-----------------------------
# 最初のブート時に一度だけ動くサービスのファイルを配置
#-----------------------------
cp /usr/lib/custom/firstboot.service /etc/systemd/system/firstboot.service
systemctl enable firstboot.service

#-----------------------------
#calamaresをアンインストール
#-----------------------------
sudo apt remove -y calamares

#gparted をアンインストール
sudo apt remove -y gparted
