# oYo-Linux-Builder
Custom Linux ISO build tool


**oYo Linux Builder** は、open.Yellow.os 開発チーム が提供する  
「簡単にオリジナル Linux ISO を自動ビルドするツール」です。

---

## 🌟 特徴

- **フレーバー対応**: GNOME／Xfce／KDE など複数のデスクトップ環境を切り替え  
- **多言語対応**: 日本語（ja）／英語（en）など、言語リソースを選択  
- **ブランド対応**: 壁紙・アイコン・ブートアニメーションを `--brand` で差し替え  
- **Hook 機構**: `hooks/post-install.d/*.sh` で任意コマンドを自動実行  
- **テンプレート対応**: Jinja2＋YAML で `os-release` や `branding.desc` を自動生成  

---

## ⚙️ 前提要件

- Debian系Linux（Debian GNU/Linux 12 Bullseye 以降、open.Yellow.os Freesia 以降推奨）  
- Python 3.8+  
- root権限 または sudo  
- 以下パッケージ（ホスト側）  
  ```
  debootstrap rsync squashfs-tools grub-pc-bin grub-efi-amd64-bin xorriso dosfstools mtools python3.11-venv git
  ```

---

## 🚀 クイックスタート

1. リポジトリをクローン  
   ```bash
   git clone https://github.com/openyellowos/oYo-Linux-Builder.git
   cd oYo-Linux-Builder
   ```

2. 仮想環境を作成・有効化  
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. 依存ライブラリをインストール  
   ```bash
   pip install -r requirements.txt
   ```

4. 初期セットアップ  
   ```bash
   ./bin/oyo_builder.py init
   ```

5. ISO のビルド例（GNOME／日本語／Sample-gnome ブランド）  
   ```bash
   ./bin/oyo_builder.py \
     --flavor gnome \
     --lang ja \
     --brand Sample-gnome \
     build
   ```

6. QEMU でテスト起動  
#### BIOS モード
```bash
qemu-system-x86_64 \
  -enable-kvm \
  -m 2048 \
  -machine type=pc,accel=kvm \
  -cdrom *.iso \
  -boot menu=on \
  -vga qxl \
  -serial mon:stdio
```

#### UEFI モード
```bash
mkdir -p "$HOME/ovmf"
cp /usr/share/OVMF/OVMF_VARS.fd "$HOME/ovmf/OVMF_VARS.fd"

qemu-system-x86_64 \
  -enable-kvm \
  -m 2048 \
  -machine q35,accel=kvm \
  -drive if=pflash,format=raw,readonly=on,file=/usr/share/OVMF/OVMF_CODE.fd \
  -drive if=pflash,format=raw,file="$HOME/ovmf/OVMF_VARS.fd" \
  -cdrom *.iso \
  -boot menu=on \
  -vga qxl \
  -serial mon:stdio
```

---

## 📄 ライセンス

- MIT License  
- Copyright (c) 2025 open.Yellow.os Development Team  
- Copyright (c) 2025 Toshio  

詳細は [LICENSE](./LICENSE) をご覧ください。

---

## 🤝 コントリビュート

フォーク＆プルリク大歓迎！  
詳細は [CONTRIBUTING.md](./CONTRIBUTING.md) をご参照ください。
