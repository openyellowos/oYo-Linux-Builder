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

- Debian系Linux（Debian GNU/Linux 12 Bookworm 以降、open.Yellow.os Freesia 以降推奨）  
- Python 3.8+  
- root権限 または sudo  
- 以下パッケージ（ホスト側）  
  ```
  mmdebstrap rsync squashfs-tools grub-pc-bin grub-efi-amd64-bin grub-efi-amd64-signed shim-signed xorriso dosfstools mtools python3-venv python3-pip git debian-archive-keyring
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

5. ISO のビルド例（GNOME／日本語／oYo ブランド）  
   ```bash
   ./bin/oyo_builder.py      --flavor gnome      --lang ja      --brand oYo      build
   ```

6. QEMU でテスト起動  
#### BIOS モード
```bash
qemu-system-x86_64   -enable-kvm   -m 2048   -machine type=pc,accel=kvm   -cdrom *.iso   -boot menu=on   -vga qxl   -serial mon:stdio
```

#### UEFI モード
```bash
mkdir -p "$HOME/ovmf"
cp /usr/share/OVMF/OVMF_VARS.fd "$HOME/ovmf/OVMF_VARS.fd"

qemu-system-x86_64   -enable-kvm   -m 2048   -machine q35,accel=kvm   -drive if=pflash,format=raw,readonly=on,file=/usr/share/OVMF/OVMF_CODE.fd   -drive if=pflash,format=raw,file="$HOME/ovmf/OVMF_VARS.fd"   -cdrom *.iso   -boot menu=on   -vga qxl   -serial mon:stdio
```

---

## 🛠 主なコマンド・オプション

- `init`  
  作業ディレクトリなどの初期セットアップを行います。
- `build`  
  ISOイメージをビルドします。`--flavor` `--lang` `--brand` などのオプションでカスタマイズ可。
- `clean`  
  一時作業ディレクトリを完全削除し、作業環境をリセットします。
- `--flavor`  
  使用するデスクトップ環境を指定（例: gnome, xfce, kde）。
- `--lang`  
  言語リソースを指定（例: ja, en）。
- `--brand`  
  ブランド（テーマ・壁紙セットなど）を指定。
- `--tmpfs`  
  作業ディレクトリをRAM上（tmpfs）にマウントし、ビルドを高速化します（十分なメモリがある場合推奨）。
- `--help`  
  コマンドラインヘルプを表示します。

---

## 📦 ビルド成果物

- 完成したISOイメージは**プロジェクトルート直下**に `os-バージョン-言語.iso` というファイル名で出力されます。  
  例:  
  ```
  openyellowos-1.0-ja.iso
  ```
- `work/iso` ディレクトリにも一時的な構築用ファイルが保存されます。

---

## 📚 詳細ドキュメント

- [設計方針・アーキテクチャ](./doc/10_ARCHITECTURE.md)
- [インストール/利用方法・詳細](./doc/30_USAGE.md)
- [設定・カスタマイズ・拡張方法](./doc/40_CONFIGURATION.md)
- [ブランド追加・テーマ拡張手順](./doc/50_EXTENDING.md)
- [コントリビュート・開発参加方法](./doc/60_CONTRIBUTING.md)
- [変更履歴・Changelog](./doc/99_CHANGELOG.md)

---

## 📄 ライセンス

- MIT License  
- Copyright (c) 2025 open.Yellow.os Development Team  
- Copyright (c) 2025 Toshio  

詳細は [LICENSE](./LICENSE) をご覧ください。

---

## 🤝 コントリビュート

フォーク＆プルリク大歓迎！  
詳細は [CONTRIBUTING.md](./doc/60_CONTRIBUTING.md) をご参照ください。
