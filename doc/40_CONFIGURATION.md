# CONFIGURATION.md

oYo-Builder の設定ファイル／ディレクトリ構成の詳細リファレンスです。

---

## 1. packages.txt

- **役割**: chroot内にインストールするパッケージ一覧を指定  
- **場所**: 各レイヤーのルート（例: `config/10_common/packages.txt`, `config/20_gnome/packages.txt` など）  
- **書式**:
  - 1行に1パッケージ名（Debian/Ubuntuでapt installできる名前）
  - 空行や `#` で始まる行は無視
  - 複数レイヤー分は「レイヤー昇順に後勝ちでマージ」
- **注意**: 現在は `mmdebstrap` の `--include` でまとめて一括インストールしています
- **例**:
  ```text
  # 共通パッケージ
  sudo
  mmdebstrap

  # GNOME用
  gnome-session
  gnome-shell
  ```

---

## 2. Overlay ディレクトリ

- **役割**: chrootファイルシステムに直接ファイルを上書き／追加する仕組み  
- **場所**: 各レイヤーの `overlay/` 以下
- **動作**:
  - 各レイヤーのoverlayを順に chroot直下に `sudo rsync -a` でコピー（後勝ちで上書き）
  - 既存ファイルは上書き、ディレクトリはマージ
- **パス例**:
  ```
  config/20_gnome/overlay/usr/share/backgrounds/custom/background.png
  config/40_brand/myco/overlay/etc/dconf/db/local.d/00-brand-settings
  ```
- **豆知識**: `/etc/sudoers.d`の所有権はコピー後に強制的にroot:root/0440へ修正されます

---

## 3. Hooks（フック）機構

- **用途**: ベースシステム展開直後に任意のスクリプトを chroot内で実行
- **ディレクトリ**:
  ```
  config/<layer>/hooks/post-install.d/
  ```
- **実行タイミング**:
  - `post-install.d`: ベース展開・overlay・ユーザー作成後
- **ファイル名**:
  - 数字プレフィックス順（`10-`, `20-`など）で昇順に実行
  - 拡張子 `.sh` で実行権限のあるものだけ対象
- **動作**:
  1. ホスト→chroot `/tmp/`にコピー
  2. `chroot`コマンドで `sh /tmp/xxx.sh` を実行
- **例**:
  ```bash
  # config/common/hooks/post-install.d/10-flatpak.sh
  #!/bin/sh
  set -e
  apt-get update
  apt-get install -y ca-certificates flatpak
  flatpak remote-add --if-not-exists flathub https://dl.flathub.org/repo/flathub.flatpakrepo
  ```

---

## 4. Templates（テンプレート）機構

- **用途**: Jinja2テンプレート＋YAML変数から設定ファイルを動的生成
- **場所**:
  ```
  config/40_brand/<brand>/templates/
  ```
- **必須ファイル**:
  - `brand.yml`（テンプレートで使う変数定義。例: name, version, logo, theme, background など）
  - `<ファイル名>.j2`（Jinja2テンプレートファイル）
- **テンプレート例・主な出力先**:
  - `os-release.conf.j2` → `/etc/os-release`
  - `branding.desc.j2` → `/etc/calamares/branding/<brand>/branding.desc`
  - `grub.cfg.j2` → `ISO/boot/grub/grub.cfg`
  - `plymouth-theme.conf.j2` → `/usr/share/plymouth/themes/<theme>/theme`
- **brand.ymlの例**:
  ```yaml
  name: "MyCo Linux"
  pretty_name: "MyCo Linux 1.0"
  version_id: "1.0"
  logo: "myco-logo.png"
  theme: "custom"
  background: "/usr/share/backgrounds/myco_wall.png"
  ```
- **テンプレ内での参照例**:
  ```jinja
  PRETTY_NAME="{{ pretty_name }}"
  NAME="{{ name }}"
  VERSION_ID="{{ version_id }}"
  ID={{ name|lower }}
  ```
- **動作概要**:
  1. `_apply_os_release()`や`_apply_calamares_branding()`でテンプレート検出
  2. Jinja2でレンダリングし、所定パスへ出力
  3. レイヤー優先で後勝ち（brand > lang > flavor > common）

---

## 【Tips／補足】

- レイヤー合成順は `common → flavor → lang → brand`（後勝ち）。同じファイルが複数レイヤーにあれば「最後の（brand）が有効」。
- chroot内でのファイルパス指定は必ず「/」から始める（絶対パス）。
- テンプレート変数で独自の値もbrand.yml等で追加可能。
- 詳しい使い方・コマンド例は [USAGE.md](./30_USAGE.md) も併せて参照してください。

---
