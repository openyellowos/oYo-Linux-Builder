#!/bin/bash
#
# firewallの有効化
#
# 【目的】:
#   - セキュリティ強化のため、デフォルトでfirewallを有効化する
#
set -e

#firewallの有効化
ufw enable

#gufwが起動しない問題を修正
chmod 755 /etc
chmod 755 /lib
