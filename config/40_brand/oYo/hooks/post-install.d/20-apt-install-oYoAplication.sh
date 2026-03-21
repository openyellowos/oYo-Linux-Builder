#!/bin/bash
#
# oYoオリジナルのアプリケーションをインストール
#
# 【目的】:
#   - oYoリポジトリの設定を行い、oYoの独自アプリケーションをインストールする
#
set -e

# 1) oYoリポジトリ接続用のキーリングをインストール
dpkg -i /usr/share/openyellowos/oyo-archive-keyring_1.0_all.deb

# 2) リポ登録（amd64 限定）
#    keyring deb は /usr/share/keyrings/oyo-archive.gpg を配置するため
#    signed-by も同一パスを参照する
tee /etc/apt/sources.list.d/oyo.list >/dev/null <<'EOF'
deb [arch=amd64 signed-by=/usr/share/keyrings/oyo-archive.gpg] https://deb.openyellowos.com kerria main
EOF

# 3) 更新
apt update

# 4) アプリケーションのインストール
apt install -y oyo-ui-changer
apt install -y oyo-sys-tools
apt install -y oyo-gjs-osk
apt install -y oyo-calamares
apt install -y oyo-portable-system-creator

