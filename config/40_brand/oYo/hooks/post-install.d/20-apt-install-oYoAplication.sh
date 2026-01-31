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
install -d -m 0755 /etc/apt/keyrings
tee /etc/apt/sources.list.d/oyo.list >/dev/null <<'EOF'
deb [arch=amd64 signed-by=/etc/apt/keyrings/oyo-archive.gpg] https://deb.openyellowos.com kerria main
EOF

# 3) 更新
apt update

# 4) アプリケーションのインストール
apt install oyo-ui-changer
apt install oyo-sys-tools
apt install oyo-gjs-osk

