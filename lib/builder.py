#!/usr/bin/env python3
import os
import shutil
import subprocess
from pathlib import Path
import logging
import datetime
import re
import sys
import shutil as _shutil
import yaml
from jinja2 import Environment, FileSystemLoader
import typer
import atexit
import textwrap
import stat


# debootstrap などが /usr/sbin/ に入っている場合があるので、
# チェックを行う前に sbin を PATH に含める
os.environ["PATH"] = os.environ.get("PATH", "") + os.pathsep + "/usr/sbin"

ROOT     = Path(__file__).resolve().parent.parent
CFG_BASE = ROOT / "config"

# アンマウント対象を記録するリスト
_MOUNTS: list[Path] = []

def _register_unmount(path: Path):
    if path not in _MOUNTS:
        _MOUNTS.append(path)

def _cleanup_mounts():
    for m in reversed(_MOUNTS):
        subprocess.run(
            ["sudo", "umount", "-l", str(m)],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )

# プログラム終了時に必ず呼ぶ
atexit.register(_cleanup_mounts)

TMPFS_SIZE = os.getenv("OYO_TMPFS_SIZE", "8G")   # 例: 8G, 16G, 80%

def _mount_tmpfs(path: Path):
    "path を tmpfs にマウント（空でも中身があっても強制マウント）"
    _run(["sudo", "mount", "-t", "tmpfs",
          "-o", f"size={TMPFS_SIZE},mode=0755", "tmpfs", str(path)])
    print(f"Mounted tmpfs ({TMPFS_SIZE}) on {path}")
    _register_unmount(path)

def _render_brand_template(template_name: str, dest_path: Path, context: dict):
    """config/brand/<brand>/templates からテンプレートを探し、
       コンテキストでレンダリングして chroot 内に書き込む"""
    brand = os.getenv("OYO_BRAND", "default")

    # 数字付きプレフィックス付きディレクトリを優先して探す
    brand_layer = next(
        (d for d in CFG_BASE.iterdir()
         if d.is_dir() and d.name.split("_",1)[1] == "brand"),
        None
    )
    if not brand_layer:
        raise FileNotFoundError("config 配下に *_brand ディレクトリが見つかりません")
        
    tpl_dir = brand_layer / brand / "templates"

    env = Environment(loader=FileSystemLoader(str(tpl_dir)))
    tpl = env.get_template(template_name)
    rendered = tpl.render(**context)

    target = CHROOT / dest_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(rendered)
    print(f"Rendered {template_name} → {target}")

def get_configs() -> list[Path]:
    """
    config/配下を数字プレフィックス順にスキャンして、
    common→flavor→lang→brand を自動で選択・返却する。
    """
    flavor = os.getenv("OYO_FLAVOR", "common")
    lang   = os.getenv("OYO_LANG",    "en")
    brand  = os.getenv("OYO_BRAND",   "default")

    configs: list[Path] = []
    for grp in sorted(CFG_BASE.iterdir()):
        if not grp.is_dir() or "_" not in grp.name:
            continue
        # ディレクトリ名を "NN_key" に分割
        _num, key = grp.name.split("_", 1)

        # common レイヤー
        if key == "common":
            configs.append(grp)

        # flavor レイヤー（config/NN_flavor/<flavor> を探す）
        elif key == "flavor":
            sub = grp / flavor
            if sub.is_dir():
                configs.append(sub)

        # lang レイヤー（サブディレクトリ ja|en があるはず）
        elif key == "lang":
            sub = grp / lang
            if sub.is_dir():
                configs.append(sub)

        # brand レイヤー（サブディレクトリ default|myco があるはず）
        elif key == "brand":
            sub = grp / brand
            if sub.is_dir():
                configs.append(sub)

    return configs

def get_hook_configs() -> list[Path]:
    """
    hooks（pre-install / post-install）の対象となる層をすべて返す。
    """
    flavor = os.getenv("OYO_FLAVOR", "common")
    lang   = os.getenv("OYO_LANG",    "en")
    brand  = os.getenv("OYO_BRAND",   "default")

    configs: list[Path] = []
    for grp in sorted(CFG_BASE.iterdir()):
        if not grp.is_dir() or "_" not in grp.name:
            continue
        _num, key = grp.name.split("_", 1)

        # 共通処理：各レイヤーの該当サブディレクトリを追加
        if key == "common":
            configs.append(grp)
        elif key == "flavor":
            sub = grp / flavor
            if sub.is_dir():
                configs.append(sub)
        elif key == "lang":
            sub = grp / lang
            if sub.is_dir():
                configs.append(sub)
        elif key == "brand":
            sub = grp / brand
            if sub.is_dir():
                configs.append(sub)

    return configs
    
def _run_hooks(stage: str):
    """
    common→flavor→lang→brand の各 config/hooks/<stage>.d/*.sh を
    chroot 内で順に実行する。
    """
    for cfg in get_hook_configs():
        hooks_dir = cfg / "hooks" / f"{stage}.d"
        if not hooks_dir.is_dir():
            continue
        # chroot 内の一時フォルダを用意
        tmpdir = CHROOT / "tmp"
        tmpdir.mkdir(parents=True, exist_ok=True)
        for script in sorted(hooks_dir.iterdir()):
            if script.suffix == ".sh" and script.is_file():
                dest = tmpdir / script.name
                print(f"→ hook: copying {script} to {dest}")
                _run(["sudo", "cp", str(script), str(dest)])
                print(f"→ hook: executing {script.name} in chroot")
                _run([
                    "sudo", "chroot", str(CHROOT),
                    "sh", f"/tmp/{script.name}"
                ])
    
def _render_brand_template(template_name: str, dest: Path, context: dict):
    """
    config/brand/<brand>/templates/<template_name> を
    Jinja2 でレンダリングし、CHROOT 内の dest に書き込む。
    """
    brand = os.getenv("OYO_BRAND", "default")
    # 同じく数字付きプレフィックス付き「*_brand」から拾う
    brand_layer = next(
        (d for d in CFG_BASE.iterdir() if d.is_dir() and d.name.split("_",1)[1] == "brand"),
        None
    )
    tpl_dir = brand_layer / brand / "templates"
    env = Environment(loader=FileSystemLoader(str(tpl_dir)))
    tpl = env.get_template(template_name)
    rendered = tpl.render(**context)

    target = CHROOT / dest
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(rendered)
    print(f"Rendered {template_name} → {target}")

LOG_DIR = ROOT / "log"
LOG_DIR.mkdir(parents=True, exist_ok=True)

# ビルドに必要な外部コマンド一覧
REQUIRED_COMMANDS = [
    "sudo",
    "debootstrap",
    "mmdebstrap",
    "grub-mkrescue",
    "mksquashfs",
    "xorriso",
    "cp",
    "mount",
    "umount",
    "rsync",
    "mtools",
]

def _check_host_dependencies():
    """ビルドに必須のホスト側コマンドがインストールされているかチェック"""
    missing = []
    for cmd in REQUIRED_COMMANDS:
        if _shutil.which(cmd) is None:
            missing.append(cmd)
    if missing:
        print(f"[ERROR] 以下のコマンドが見つかりません: {', '.join(missing)}")
        print("ビルドを続行するには、これらをインストールしてください。")
        sys.exit(1)

# 今回ビルドごとにタイムスタンプ付きログファイルを作成
ts = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
LOG_FILE = LOG_DIR / f"build_{ts}.log"

# logging の設定：ファイルとコンソールの両方に出力
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# (既存の) logger 設定 はそのまま
LOG_DIR = ROOT / "log"
LOG_DIR.mkdir(parents=True, exist_ok=True)

CONFIG = ROOT / "config"
WORK   = ROOT / "work"
CHROOT = WORK / "chroot"
ISO    = WORK / "iso"
LOG    = ROOT / "log"

def initialize(use_tmpfs: bool = False):
    """work/ と log/ のディレクトリを作成"""
    # ホスト依存チェック
    _check_host_dependencies()

    # ① 先に mount ポイント（WORK）を作成
    WORK.mkdir(parents=True, exist_ok=True)
    # ② フラグが True のときだけ tmpfs をマウント
    if use_tmpfs:
        _mount_tmpfs(WORK)
        print("tmpfs created")
    for d in (WORK, ISO, CHROOT, LOG):
        d.mkdir(parents=True, exist_ok=True)
    print(f"Created work and log directories: {WORK}, {LOG}")

# スクリプトが root で実行中か
IS_ROOT = (os.geteuid() == 0)

def _run(cmd, **kwargs):
    """
    外部コマンド実行のラッパー。
    - root 実行時は先頭の sudo を自動で除去
    - 標準出力・エラーをログに流す
    """
    # root なら sudo を外す
    if IS_ROOT and cmd and cmd[0] == "sudo":
        cmd = cmd[1:]
    logger.info(">> %s", " ".join(cmd))
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        **kwargs
    )
    # プロセスから出力される行をすべてログに
    for line in proc.stdout:
        logger.info(line.rstrip())
    proc.wait()
    if proc.returncode != 0:
        raise subprocess.CalledProcessError(proc.returncode, cmd)

def _get_codename_from_os_release() -> str:
    """common→flavor の順で os-release を探し、VERSION_CODENAME を返す"""
    # 1) os-release ファイルを検索
    for cfg in get_configs():
        src = cfg / "os-release"
        if src.exists():
            break
    else:
        paths = ", ".join(str(p / "os-release") for p in get_configs())
        raise FileNotFoundError(
            f"以下のいずれにも os-release が見つかりません:\n  {paths}\n"
            "config/common/os-release をご確認ください。"
        )

    # 2) 中身をパースして VERSION_CODENAME を探す
    for line in src.read_text().splitlines():
        if line.startswith("VERSION_CODENAME="):
            codename = line.split("=",1)[1].strip().strip('"')
            if codename:
                return codename
    raise RuntimeError(
        f"{src} に VERSION_CODENAME が見つかりません。\n"
        "例：VERSION_CODENAME=bookworm\n"
        "を追記してください。"
    )
    
def _get_iso_filename() -> str:
    """
    common→flavor の順で os-release を探し、
    見つかったファイルから ISO のファイル名を決定する
    """
    # 1) os-release ファイルを検索
    for cfg in get_configs():
        src = cfg / "os-release"
        if src.exists():
            break
    else:
        paths = "\n  ".join(str(p / "os-release") for p in get_configs())
        raise FileNotFoundError(
            f"以下のいずれにも os-release が見つかりません:\n  {paths}\n"
            "config/common/os-release をご確認ください。"
        )

    # 2) simple parse
    info: dict[str,str] = {}
    for line in src.read_text().splitlines():
        if "=" not in line or line.strip().startswith("#"):
            continue
        k, v = line.split("=", 1)
        info[k] = v.strip().strip('"')

    name    = info.get("NAME", "os").lower()
    version = info.get("VERSION_ID", "")
    base    = f"{name}-{version}" if version else name
    # 不正文字をアンダースコアに置換
    safe    = re.sub(r'[^A-Za-z0-9._-]+', '_', base)
    # 環境変数 OYO_LANG から言語コードを取得（デフォルト en）
    lang    = os.getenv("OYO_LANG", "en")
    # 最終的なファイル名に言語コードを追加
    return f"{safe}-{lang}.iso"

def _prepare_chroot(codename: str):
    """chroot をクリアして debootstrap でベースシステムを投入"""

    # 古い chroot をまるごと削除
    if CHROOT.exists():
        # ─── 念のため残存マウントをアンマウント ───
        for m in ("dev/pts", "dev/shm", "dev/mqueue", "dev/hugepages",
                  "dev", "sys", "proc", "run"):
            target = CHROOT / m
            if target.exists():
                # lazy unmount でリソースビジーを回避
                subprocess.run(
                    ["sudo", "umount", "-l", str(target)],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
        # すべてアンマウントしたあとにディレクトリ削除
        _run(["sudo", "rm", "-rf", str(CHROOT)])

    # chroot ディレクトリを再作成
    CHROOT.mkdir(parents=True, exist_ok=True)

    # ── 1) パッケージ一覧を収集 ──
    pkg_list: list[str] = []
    for cfg in get_configs():
        pkgfile = cfg / "packages.txt"
        if pkgfile.exists():
            pkg_list += [
                p.strip() for p in pkgfile.read_text().splitlines()
                if p.strip() and not p.strip().startswith("#")
            ]

    # ── 2) mmdebstrap に渡す必須パッケージ群 ──
    base_pkgs = ["bash", "coreutils"]
    include_pkgs = sorted(set(base_pkgs + pkg_list))

    #signed kernel を探して include_pkgs に追加
    print("Probing for latest linux-image-*-signed package…")
    try:
        result = subprocess.run(
            ["apt-cache", "search", "^linux-image-.*-signed$"],
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, check=True
        )
        candidates = [line.split()[0] for line in result.stdout.strip().splitlines()]
        if candidates:
            selected_kernel = sorted(candidates)[-1]
            print(f"Detected signed kernel: {selected_kernel}")
            include_pkgs.append(selected_kernel)
        else:
            print("[Warning] No signed kernel found in apt-cache")
    except Exception as e:
        print(f"[Warning] Could not detect signed kernel automatically: {e}")

    #include_opt を定義する
    include_opt = "--include=" + ",".join(include_pkgs)

    print("Deploying base system via mmdebstrap (incl. all packages)…")
    _run([
        "sudo", "mmdebstrap",
        "--architectures=amd64",
        "--variant=important",

        # ── 並列ダウンロード・リトライ設定 ──
        "--aptopt=Acquire::Queue-Mode \"host\";",
        "--aptopt=Acquire::Retries \"3\";",

        # ── あらかじめ集めたパッケージ群 ──
        include_opt,

        # ── その他の引数 ──
        codename,
        str(CHROOT),
        "http://deb.debian.org/debian"
    ])

    print(f"Base system + packages deployed via mmdebstrap ({codename}).")

def _copy_overlay():
    """common→flavor の overlay を順に chroot にコピー"""
    for cfg in get_configs():
        overlay = cfg / "overlay"
        if overlay.exists():
            print(f"Applying overlay from {overlay} …")
            # rsync -a なら既存のファイル／シンボリックリンクを上書き削除してくれる
            _run([
                "sudo", "rsync", "-a",
                f"{overlay}/",  # Trailing slash: 中身すべてを
                str(CHROOT) + "/"  # chroot 直下にコピー
            ])
            
    # --- ここで必ず sudoers.d の所有者を root:root に戻す ---
    print("Fixing ownership on /etc/sudoers.d …")
    _run([
        "sudo", "chroot", str(CHROOT),
        "chown", "-R", "root:root", "/etc/sudoers.d"
    ])


    print("Overlay files copied.")

def _apply_os_release():
    """os-release をテンプレート or overlay から設定"""
    # 1) brand.yml を読み込んで context 作成
    brand = os.getenv("OYO_BRAND", "default")

    # 数字接頭辞付きの「*_brand」ディレクトリを探す
    brand_layer = next(
        (d for d in CFG_BASE.iterdir()
         if d.is_dir() and d.name.split("_",1)[1] == "brand"),
        None
    )
    if not brand_layer:
        raise FileNotFoundError("config 配下に *_brand ディレクトリが見つかりません")

    # この下に各ブランド設定フォルダ（Sample-gnome など）がある想定
    brand_dir = brand_layer / brand
        
     # 1) brand.yml を読み込んで context 作成
    brand_yml = brand_dir / "brand.yml"

    context = {}
    if brand_yml.exists():
        context = yaml.safe_load(brand_yml.read_text())

    # 2) テンプレートがあれば優先してレンダリング
    tpl = brand_dir / "templates" / "os-release.conf.j2"
    if tpl.exists():
        _render_brand_template(
            "os-release.conf.j2",
            Path("etc") / "os-release",
            context
        )
        return

    # 3) なければ従来通り common→flavor→lang overlay からコピー
    for cfg in get_configs():
        src = cfg / "os-release"
        if src.exists():
            _run(["sudo", "cp", str(src), str(CHROOT / "etc/os-release")])
            print(f"Applied os-release from {src}")
            return
    raise FileNotFoundError("config/common/os-release をご確認ください。")

def _apply_calamares_branding():
    """
    Calamares の branding.desc を
    1) config/brand/<brand>/templates/branding.desc.j2 からレンダリング
       → chroot/etc/calamares/branding/<brand>/branding.desc に書き込む
    2) もしテンプレートがなければ overlay の既存ファイルをそのまま使う
    """
    brand = os.getenv("OYO_BRAND", "default")

    # 数字付きプレフィックスの「*_brand」ディレクトリを探す
    brand_layer = next(
        (d for d in CFG_BASE.iterdir() if d.is_dir() and d.name.split("_",1)[1] == "brand"),
        None
    )
    # brand.yml から変数を読み込む
    yml = brand_layer / brand / "brand.yml" if brand_layer else CFG_BASE / "brand" / brand / "brand.yml"

    context = {}
    if yml.exists():
        context = yaml.safe_load(yml.read_text())
    # テンプレートがあればレンダリング
    tpl = brand_layer / brand / "templates" / "branding.desc.j2" if brand_layer else CFG_BASE / "brand" / brand / "templates" / "branding.desc.j2"
    if tpl.exists():
         dest = Path("etc") / "calamares" / "branding" / brand / "branding.desc"
         _render_brand_template("branding.desc.j2", dest, context)
    if tpl.exists():
        # Calamares の overlay で使われているディレクトリ名をそのまま使います
        dest = Path("etc") / "calamares" / "branding" / brand / "branding.desc"
        _render_brand_template("branding.desc.j2", dest, context)
    else:
        print(f"No branding.desc.j2 for brand={brand}, skipping template.")

def build_iso():
    """ISO ビルドのメインフロー"""
    logger.info("=== Build started ===")
    codename = _get_codename_from_os_release()

    _prepare_chroot(codename)

    print("Copying overlay…")
    _copy_overlay()
    
    print("User add live…")
    create_live_user()

    # ─── Calamares branding.desc をテンプレートで生成する ───
    print("Applying Calamares branding template…")
    _apply_calamares_branding()
    
    # ——— chroot 内に /proc /sys /dev をバインドマウント ———
    print("Mounting /proc, /sys, /dev into chroot…")
    for fs in ("proc", "sys", "dev"):
        target = CHROOT / fs
        target.mkdir(exist_ok=True)
        _run(["sudo", "mount", "--bind", f"/{fs}", str(target)])
        _register_unmount(target)
        
    # ホストの APT キャッシュを使う (/var/cache/apt/archives)
    print("Binding host APT cache into chroot…")
    apt_cache = CHROOT / "var" / "cache" / "apt" / "archives"
    apt_cache.mkdir(parents=True, exist_ok=True)
    _run(["sudo", "mount", "--bind", "/var/cache/apt/archives", str(apt_cache)])
    _register_unmount(apt_cache)  

    # ——— post-install hooks を実行 ———
    print("Running pre-install hooks…")
    _run_hooks("pre-install")
    
    # ——— post-install hooks を実行 ———
    print("Running post-install hooks…")
    _run_hooks("post-install")

    # ─── GUI起動のための systemd 設定 ───
    print("Enabling graphical.target…")
    # 1) デフォルトターゲットを graphical.target に
    _run([
        "sudo", "chroot", str(CHROOT),
        "ln", "-sf",
        "/lib/systemd/system/graphical.target",
        "/etc/systemd/system/default.target"
    ])

    print("Applying OS release…")
    _apply_os_release()

    # ① live ディレクトリを作ってカーネルと initrd をワイルドカードで配置
    live_chroot = CHROOT / "live"
    _run(["sudo", "rm", "-rf", str(live_chroot)])
    live_chroot.mkdir(parents=True, exist_ok=True)

    kernel_files = sorted((CHROOT / "boot").glob("vmlinuz-*"))
    initrd_files = sorted((CHROOT / "boot").glob("initrd.img-*"))
    kernel_src = kernel_files[-1]
    initrd_src = initrd_files[-1]

    _run(["sudo", "cp", str(kernel_src), str(live_chroot / "vmlinuz")])
    _run(["sudo", "cp", str(initrd_src), str(live_chroot / "initrd.img")])
    print(f"Live kernel ({kernel_src.name}) and initrd ({initrd_src.name}) copied.")

    # ——— ISO ルートを作成 ———
    print("Preparing ISO root…")
    _run(["sudo", "rm", "-rf", str(ISO)])
    ISO.mkdir(parents=True, exist_ok=True)

    # 必要なディレクトリだけコピー（相対パスでマッチさせる）
    _run([
        "sudo", "rsync", "-a",
        # 1) boot/ 以下を丸ごと
        # "--include=boot/", "--include=boot/**",
        # 2) UEFI 用の EFI ディレクトリ
        "--include=EFI/",  "--include=EFI/**",
        # 3) GRUB モジュール（i386-pc, x86_64-efi など）
        "--include=usr/",                  # usr/lib 以下を辿るため
        "--include=usr/lib/",              # usr/lib ディレクトリ自体
        "--include=usr/lib/grub/",         # grub モジュール基本フォルダ
        "--include=usr/lib/grub/**",       # grubモジュール全ファイル
        "--include=usr/lib/shim/",         # shim モジュール基本フォルダ
        "--include=usr/lib/shim/**",       # shimモジュール全ファイル
        "--include=usr/share/",            # usr/share 以下を辿るため
        "--include=usr/share/grub/",       # シェアド・grub ディレクトリ
        "--include=usr/share/grub/**",     # テーマやロケール等
        "--include=usr/share/shim/",       # シェアド・shim ディレクトリ
        "--include=usr/share/shim/**",     # shim
        "--include=usr/lib/grub/i386-pc/",    "--include=usr/lib/grub/i386-pc/**",
        "--include=usr/lib/grub/x86_64-efi/", "--include=usr/lib/grub/x86_64-efi/**",
        # 4) squashfs の置き場 live/ 以下
        "--include=live/", "--include=live/**",
        # 5) それ以外は不要
        "--exclude=*",
        f"{CHROOT}/", f"{ISO}/"
    ])

    # ── Secure Boot 対応の shim + grub を配置 ──
    efi_boot = ISO / "EFI" / "BOOT"
    efi_boot.mkdir(parents=True, exist_ok=True)

    # Secure Boot 対応用の shim + grubx64.efi を配置
    shim_src  = CHROOT / "usr/lib/shim/shimx64.efi.signed"
    mm_src    = CHROOT / "usr/lib/shim/mmx64.efi"

    # GRUB EFI（Microsoft署名済）をそのままコピー
    signed_grub = CHROOT / "usr/lib/grub/x86_64-efi-signed/grubx64.efi.signed"
    _run(["sudo", "cp", str(signed_grub), str(efi_boot / "grubx64.efi")])
    print("署名付き grubx64.efi をコピーしました")

    # shimx64 を BOOTX64.EFI として配置
    _run(["sudo", "cp", str(shim_src), str(efi_boot / "BOOTX64.EFI")])
    _run(["sudo", "cp", str(mm_src), str(efi_boot / "mmx64.efi")])
#    shutil.copy2(shim_src, efi_boot / "BOOTX64.EFI")
#    shutil.copy2(mm_src,   efi_boot / "mmx64.efi")
    print("Secure Boot 用の shimx64.efi, grubx64.efi, mmx64.efi を配置しました")

    print("ISO root prepared (with /proc, /sys, /dev excluded).")

    # ─── Plymouth テンプレートがあればここで適用 ───
    # 1) brand レイヤーを探して paths を決定
    brand = os.getenv("OYO_BRAND", "default")
    brand_layer = next(
        (d for d in CFG_BASE.iterdir()
         if d.is_dir() and d.name.split("_",1)[1] == "brand"),
        None
    )
    if brand_layer:
        brand_dir = brand_layer / brand
        # context は brand.yml から
        context = {}
        yml = brand_dir / "brand.yml"
        if yml.exists():
            context = yaml.safe_load(yml.read_text())

        # ① plymouth-theme.conf.j2 → テーマ本体
        theme_tpl = brand_dir / "templates" / "plymouth-theme.conf.j2"
        if theme_tpl.exists():
            _render_brand_template(
                "plymouth-theme.conf.j2",
                Path("usr") / "share" / "plymouth" / "themes" / context.get("theme","default") / "theme",
                context
            )
            print(f"Applied Plymouth theme from {theme_tpl}")

        # ② plymouth-<theme>.conf.j2 → 設定ファイル
        for tpl in (brand_dir / "templates").glob("plymouth-*.conf.j2"):
            out_name = tpl.name[:-3]   # .j2 を外したファイル名
            _render_brand_template(
                tpl.name,
                Path("etc") / "plymouth" / out_name,
                context
            )
            print(f"Applied Plymouth config from {tpl}")
    
    # 【Brand テンプレートがあれば BIOS/UEFI 両方の grub.cfg を上書き
    brand = os.getenv("OYO_BRAND", "default")
    brand_layer = next(
        (d for d in CFG_BASE.iterdir() if d.is_dir() and d.name.endswith("_brand")),
        None
    )
    if brand_layer:
        brand_dir = brand_layer / brand
        grub_tpl = brand_dir / "templates" / "grub.cfg.j2"
        if grub_tpl.exists():
            # brand.yml からコンテキストを読み直す
            context = {}
            yml = brand_dir / "brand.yml"
            if yml.exists():
                context = yaml.safe_load(yml.read_text())

            # BIOS 向け grub.cfg
            _render_brand_template(
                "grub.cfg.j2",
                ISO / "boot" / "grub" / "grub.cfg",
                context
            )

    print(f"Applied branded grub.cfg from {grub_tpl} to BIOS and UEFI")
    
    # UEFI向けにも同じ grub.cfg をコピー
    uefi_grub_cfg_path = ISO / "EFI" / "BOOT" / "grub.cfg"
    _run([
        "sudo", "cp",
        str(ISO / "boot" / "grub" / "grub.cfg"),
        str(uefi_grub_cfg_path)
    ])
    print(f"Copied grub.cfg to UEFI path: {uefi_grub_cfg_path}")

    # ——— ISO ルートに live カーネル/初期RAMをコピー ———
    live_dir = ISO / "live"
    _run(["sudo", "rm", "-rf", str(live_dir)])
    live_dir.mkdir(parents=True, exist_ok=True)

    # chroot/boot 以下から最新のカーネルと initrd をワイルドカードで取得
    kernel_files = sorted((CHROOT / "boot").glob("vmlinuz-*"))
    initrd_files = sorted((CHROOT / "boot").glob("initrd.img-*"))
    if not kernel_files or not initrd_files:
        raise FileNotFoundError("chroot/boot に vmlinuz-* または initrd.img-* が見つかりません")
    kernel_src = kernel_files[-1]
    initrd_src = initrd_files[-1]

    _run(["sudo", "cp", str(kernel_src), str(live_dir / "vmlinuz")])
    _run(["sudo", "cp", str(initrd_src), str(live_dir / "initrd.img")])
    print(f"Copied live kernel ({kernel_src.name}) and initrd ({initrd_src.name}) into ISO root.")
    
    # squashfs イメージを作成（仮想FSを完全除外）
    # —— squashfs の前に chroot の仮想FSをアンマウント —— 
    print("Unmounting /proc, /sys, /dev from chroot before squashfs…")
    for fs in ("dev", "sys", "proc", "var/cache/apt/archives"):
        _run(["sudo", "umount", "-l", str(CHROOT / fs)])

    # squashfs イメージを作成
    squashfs = live_dir / "filesystem.squashfs"
    print("Creating squashfs image…")

    # squashfs 生成の高速化: LZ4 + 全コア使用
    cpus = os.cpu_count() or 1
    
    _run([
        "sudo", "mksquashfs",
        str(CHROOT),
        str(squashfs),
        "-comp", "lz4",             # 圧縮方式: lz4（高速）
        "-processors", str(cpus),   # 全コア数を指定（1以上）
        "-e", "live"                # /live は別途コピー
    ])
    print(f"Squashfs image created at {squashfs}")

    # ─── ISO イメージを作成 (BIOS＋UEFI のハイブリッド) ───
    logger.info("Creating hybrid ISO (BIOS + UEFI)…")
    _make_iso()

    # 終了ログ
    logger.info("=== Build finished ===")

def _make_iso():
    """grub-mkrescue で ISO イメージを作成。名前は os-release に従う"""
    # 動的にファイル名を決定
    iso_name = _get_iso_filename()
    iso_file = ROOT / iso_name
    # Root 権限で実行しないと、root:root のままのファイルを読めない
    _run([
        "sudo", "grub-mkrescue",
        "--output", str(iso_file),
        "--compress=xz",
        # モジュール名はスペース区切り（shell でまとめて渡す）
        "--modules=normal configfile iso9660 part_msdos loopback search",
        str(ISO)
    ])
    logger.info(f"ISO image created: {iso_file}")

def clean_work():
    """work/ 以下をクリーンアップ"""
    import subprocess, os
    devnull = subprocess.DEVNULL if os.path.exists(os.devnull) else None

    # ① まず残っている bind マウントを外す
    for fs in (
        "var/cache/apt/archives",
        "dev/pts",
        "dev/mqueue",
        "dev/hugepages",
        "dev/shm",
        "dev",
        "sys",
        "proc"
    ):
        target = CHROOT / fs
        # 存在していればアンマウントを試みる
        if target.exists():
            try:
                cmd = ["sudo", "umount", "-l", str(target)]
                subprocess.run(cmd, stdout=devnull, stderr=devnull, check=False)
            except FileNotFoundError:
                  # 念のため、失敗しても先に進める
                pass

    # ② tmpfs が残っている限り、二重マウントも含めてアンマウント
    while True:
        # mountpoint -q はマウントされていれば 0 を返します
        result = subprocess.run(["mountpoint", "-q", str(WORK)])
        if result.returncode != 0:
            break
        subprocess.run(["sudo", "umount", "-l", str(WORK)], check=False)

    # ③ work ディレクトリを丸ごと削除＆再作成
    if WORK.exists():
        _run(["sudo", "rm", "-rf", str(WORK)])
    WORK.mkdir(parents=True, exist_ok=True)

    print(f"Cleaned work directory (and unmounted tmpfs): {WORK}")
    
def create_live_user():
    """
    chroot 環境内に live ユーザーを作成し、パスワードも設定します。
    /etc/skel の内容が一部コピーされない問題があるため、明示的に再コピーも行います。
    """
    print("Creating 'live' user in chroot...")

    # live ユーザー作成
    _run([
        "sudo", "chroot", str(CHROOT),
        "useradd", "-m", "-s", "/bin/bash", "live"
    ])

    # パスワード設定
    _run([
        "sudo", "chroot", str(CHROOT),
        "sh", "-c", "echo 'live:live' | chpasswd"
    ])

    # skel の中身を強制コピー（useraddコマンドでコピーが漏れるケースがあったため）
    _run([
        "sudo", "cp", "-a", f"{CHROOT}/etc/skel/.", f"{CHROOT}/home/live/"
    ])
    _run([
        "sudo", "chroot", str(CHROOT),
        "chown", "-R", "live:live", "/home/live"
    ])

    print("ユーザー 'live' を作成し、/etc/skel の全内容を確実にコピーしました。")



