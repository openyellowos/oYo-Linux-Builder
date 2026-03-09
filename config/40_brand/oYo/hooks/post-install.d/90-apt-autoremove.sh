#!/bin/bash
#
# apt autoremove を実行
#
# 【目的】:
#   - apt autoremove は必ず実行する
#

echo "apt autoremove"
apt autoremove -y --purge

