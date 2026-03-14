#!/bin/bash
#
# update-initramfs を実行
#
# 【目的】:
#   - update-initramfs は必ず実行する
#
set -e

update-initramfs -u -k all

