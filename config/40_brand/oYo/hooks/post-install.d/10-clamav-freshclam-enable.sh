#!/bin/bash
#
# ClamAV の定義ファイル更新サービスを有効化するスクリプト
#
# 【目的】:
#   - clamav-freshclam サービスを有効化し、
#     システム起動時に自動でウイルス定義を更新できるようにする
#
set -e

# clamav-freshclam サービスを有効化（次回起動時から自動実行）
systemctl enable clamav-freshclam
