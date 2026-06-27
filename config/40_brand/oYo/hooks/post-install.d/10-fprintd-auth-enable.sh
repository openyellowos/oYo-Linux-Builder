#!/bin/bash
#
# 指紋認証をシステム全体で有効化
#
# 【目的】:
#   - 管理者権限の必要な場面で指紋認証が利用できるようにする。
#
set -e

pam-auth-update --enable fprintd
