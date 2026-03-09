#!/bin/bash
#
# PCI ID リストの更新
#
# 【目的】:
#   - デバイス認識の向上
#
set -e

update-pciids

# 古いリストの削除
rm /usr/share/misc/pci.ids.old
