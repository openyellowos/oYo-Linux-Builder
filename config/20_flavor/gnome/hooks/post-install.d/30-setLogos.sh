#!/bin/bash
#
# /custom-theme/ディレクトリのロゴ/テーマ等を必要に応じてリサイズして、gnomeに登録する
#
# 【目的】:
#   - サイズ違いのロゴファイルを用意するのは手間なので、/custom-theme/ディレクトリに
#     svgファイルを置いておき、このスクリプトでリサイズして各所に配置する。
#
set -e

#vendor-logos
mkdir -p /usr/share/desktop-base/custom-logos
cp /custom-theme/logos/logo.svg /usr/share/desktop-base/custom-logos/logo.svg
cp /custom-theme/logos/logo-text.svg /usr/share/desktop-base/custom-logos/logo-text.svg
cp /custom-theme/logos/logo-text.svg /usr/share/desktop-base/custom-logos/logo-text-version.svg

rsvg-convert  -w 64 -h 64 -o /usr/share/desktop-base/custom-logos/logo-64.png /custom-theme/logos/logo.svg
rsvg-convert  -w 128 -h 128 -o /usr/share/desktop-base/custom-logos/logo-128.png /custom-theme/logos/logo.svg
rsvg-convert  -w 256 -h 256 -o /usr/share/desktop-base/custom-logos/logo-256.png /custom-theme/logos/logo.svg
rsvg-convert  -h 64 -o /usr/share/desktop-base/custom-logos/logo-text-64.png /custom-theme/logos/logo-text.svg
rsvg-convert  -h 128 -o /usr/share/desktop-base/custom-logos/logo-text-128.png /custom-theme/logos/logo-text.svg
rsvg-convert  -h 256 -o /usr/share/desktop-base/custom-logos/logo-text-256.png /custom-theme/logos/logo-text.svg
rsvg-convert  -h 64 -o /usr/share/desktop-base/custom-logos/logo-text-version-64.png /custom-theme/logos/logo-text-version.svg
rsvg-convert  -h 128 -o /usr/share/desktop-base/custom-logos/logo-text-version-128.png /custom-theme/logos/logo-text-version.svg
rsvg-convert  -h 256 -o /usr/share/desktop-base/custom-logos/logo-text-version-256.png /custom-theme/logos/logo-text-version.svg

update-alternatives --install /usr/share/images/vendor-logos vendor-logos /usr/share/desktop-base/custom-logos 60 \
 --slave /usr/share/icons/vendor/64x64/emblems/emblem-vendor.png emblem-vendor-64 /usr/share/desktop-base/custom-logos/logo-64.png \
 --slave /usr/share/icons/vendor/128x128/emblems/emblem-vendor.png emblem-vendor-128 /usr/share/desktop-base/custom-logos/logo-128.png \
 --slave /usr/share/icons/vendor/256x256/emblems/emblem-vendor.png emblem-vendor-256 /usr/share/desktop-base/custom-logos/logo-256.png \
 --slave /usr/share/icons/vendor/scalable/emblems/emblem-vendor.svg emblem-vendor-scalable /usr/share/desktop-base/custom-logos/logo.svg \
 --slave /usr/share/icons/vendor/64x64/emblems/emblem-vendor-symbolic.png emblem-vendor-symbolic-64 /usr/share/desktop-base/custom-logos/logo-64.png \
 --slave /usr/share/icons/vendor/128x128/emblems/emblem-vendor-symbolic.png emblem-vendor-symbolic-128 /usr/share/desktop-base/custom-logos/logo-128.png \
 --slave /usr/share/icons/vendor/256x256/emblems/emblem-vendor-symbolic.png emblem-vendor-symbolic-256 /usr/share/desktop-base/custom-logos/logo-256.png \
 --slave /usr/share/icons/vendor/scalable/emblems/emblem-vendor-symbolic.svg emblem-vendor-symbolic-scalable /usr/share/desktop-base/custom-logos/logo.svg \
 --slave /usr/share/icons/vendor/64x64/emblems/emblem-vendor-white.png emblem-vendor-white-64 /usr/share/desktop-base/custom-logos/logo-64.png \
 --slave /usr/share/icons/vendor/128x128/emblems/emblem-vendor-white.png emblem-vendor-white-128 /usr/share/desktop-base/custom-logos/logo-128.png \
 --slave /usr/share/icons/vendor/256x256/emblems/emblem-vendor-white.png emblem-vendor-white-256 /usr/share/desktop-base/custom-logos/logo-256.png \
 --slave /usr/share/icons/vendor/scalable/emblems/emblem-vendor-white.svg emblem-vendor-white-scalable /usr/share/desktop-base/custom-logos/logo.svg

#Debian-logos
cp /custom-theme/logos/logo.svg /usr/share/desktop-base/debian-logos/logo.svg
cp /custom-theme/logos/logo-text.svg /usr/share/desktop-base/debian-logos/logo-text.svg
cp /custom-theme/logos/logo-text.svg /usr/share/desktop-base/debian-logos/logo-text-version.svg

rsvg-convert  -w 64 -h 64 -o /usr/share/desktop-base/debian-logos/logo-64.png /custom-theme/logos/logo.svg
rsvg-convert  -w 128 -h 128 -o /usr/share/desktop-base/debian-logos/logo-128.png /custom-theme/logos/logo.svg
rsvg-convert  -w 256 -h 256 -o /usr/share/desktop-base/debian-logos/logo-256.png /custom-theme/logos/logo.svg
rsvg-convert  -h 64 -o /usr/share/desktop-base/debian-logos/logo-text-64.png /custom-theme/logos/logo-text.svg
rsvg-convert  -h 128 -o /usr/share/desktop-base/debian-logos/logo-text-128.png /custom-theme/logos/logo-text.svg
rsvg-convert  -h 256 -o /usr/share/desktop-base/debian-logos/logo-text-256.png /custom-theme/logos/logo-text.svg
rsvg-convert  -h 64 -o /usr/share/desktop-base/debian-logos/logo-text-version-64.png /custom-theme/logos/logo-text-version.svg
rsvg-convert  -h 128 -o /usr/share/desktop-base/debian-logos/logo-text-version-128.png /custom-theme/logos/logo-text-version.svg
rsvg-convert  -h 256 -o /usr/share/desktop-base/debian-logos/logo-text-version-256.png /custom-theme/logos/logo-text-version.svg

#calamares logo
rsvg-convert  -w 128 -h 128 -o /etc/calamares/branding/custom/logo.png /custom-theme/logos/logo.svg
cp /custom-theme/logos/logo.svg /usr/share/icons/hicolor/scalable/apps/calamares.svg

update-initramfs -u
