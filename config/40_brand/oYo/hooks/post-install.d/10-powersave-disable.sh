#!/bin/bash
#
# 省電力機能の無効化
#
# 【目的】:
#   - Wi-Fiが切れることがある問題の修正
#
set -e

pm-powersave false
