#!/bin/bash

#*****************************************************************************************************************
#
# インストール後、初回起動時のみ実行される処理
#
#*****************************************************************************************************************

#----------------------------------------------------------------------------------------------------------------
# calamaresでjpキーボードを選択した時
# /etc/default/keyboardファイルに、「us,jp」という設定を追加する
# 「us」は不要であるため、削除を行う
#
# 処理例
#   処理前      処理後
#   us,jp	jp
#   jp,us	us
#   us,de	de
#   us,us	us
#   us	        us
#   fr	        fr
#----------------------------------------------------------------------------------------------------------------

KEYBD=/etc/default/keyboard
XORG=/etc/X11/xorg.conf.d/00-keyboard.conf

# 1) 現在のキーボード設定を読み込む
XKBMODEL="pc105"
XKBLAYOUT="jp"
[ -f "$KEYBD" ] && . "$KEYBD"

# 2) カンマ区切りの末尾要素を採用
IFS=',' read -ra LAYOUTS <<< "$XKBLAYOUT"
FINAL_LAYOUT="${LAYOUTS[-1]:-$XKBLAYOUT}"

echo "[fix-keyboard] '$XKBLAYOUT' → '$FINAL_LAYOUT' (model: $XKBMODEL)"

# 3) /etc/default/keyboard を更新
sed -E -i "s/^XKBLAYOUT=.*/XKBLAYOUT=\"${FINAL_LAYOUT}\"/" "$KEYBD" \
  || echo "XKBLAYOUT=\"${FINAL_LAYOUT}\"" >> "$KEYBD"

# 4) /etc/X11/xorg.conf.d を生成
mkdir -p "$(dirname "$XORG")"
cat > "$XORG" <<EOF
Section "InputClass"
    Identifier "Keyboard defaults"
    MatchIsKeyboard "on"
    Option "XkbModel"   "${XKBMODEL}"
    Option "XkbLayout"  "${FINAL_LAYOUT}"
EndSection
EOF

#----------------------------------------------------------------------------------------------------------------
# fcitxのprofileファイルに
# calamaresで選択したキーボードレイアウトを設定する
#----------------------------------------------------------------------------------------------------------------

# 10-input-sourcesの「'xkb', 'XX'」を「'xkb', '$FINAL_LAYOUT'」に書き換え
cat /etc/dconf/db/local.d/10-input-sources | sed -e s/"'xkb', '.*'"/"'xkb', '$FINAL_LAYOUT'"/g > hoge.txt
mv hoge.txt /etc/dconf/db/local.d/10-input-sources
dconf update

# profileファイルの「Default Layout=」に「$FINAL_LAYOUT」をセット
cat /usr/lib/custom/profile | sed -e s/"Default Layout=.*"/"Default Layout=$FINAL_LAYOUT"/g > hoge.txt
mv hoge.txt /usr/lib/custom/profile

# profileファイルの「Name=keyboard-」に「$FINAL_LAYOUT」をセット
cat /usr/lib/custom/profile | sed -e s/"Name=keyboard-.*"/"Name=keyboard-$FINAL_LAYOUT"/g > hoge.txt
mv hoge.txt /usr/lib/custom/profile

#----------------------------------------------------------------------------------------------------------------
# インストール時に作成されるユーザーのhomeディレクトリのprofileファイルを
# 修正したファイルで上書き
#----------------------------------------------------------------------------------------------------------------
dir_path="/home/*"
#HOMEディレクトリ直下にあるディレクトリのパスを取得
dirs=`find $dir_path -maxdepth 0 -type d`

for dir in $dirs;
do
    #/home/[ユーザー名]からユーザー名を取得
    user=${dir:6}
    #skelディレクトリ配下を/home/[ユーザー名]にコピー
    cp /usr/lib/custom/profile $dir/.config/fcitx5/profile
     #所有者をユーザーに変更
    chown -R $user:$user $dir
done

#----------------------------------------------------------------------------------------------------------------
#skelディレクトリのprofileファイルを、修正したファイルで上書き
#----------------------------------------------------------------------------------------------------------------
cp /usr/lib/custom/profile /etc/skel/.config/fcitx5/profile

