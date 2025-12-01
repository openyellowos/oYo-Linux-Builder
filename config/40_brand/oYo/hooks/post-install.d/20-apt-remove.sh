#!/bin/bash
#
# 他パッケージに付随してインストールされるアプリを削除する
#
# 【目的】:
#   - gnome系のアプリが、他パッケージとセットで自動インストールされるため、
#     不要なアプリを削除する
#
set -e

apt remove gnome-clocks -y
apt remove gnome-contacts -y
apt remove gnome-calendar -y
apt remove gnome-characters -y
apt remove gnome-maps -y
apt remove gnome-user-docs -y
apt remove totem -y
apt remove simple-scan -y
apt remove gnome-weather -y
apt remove yelp -y
apt remove gnome-snapshot -y

