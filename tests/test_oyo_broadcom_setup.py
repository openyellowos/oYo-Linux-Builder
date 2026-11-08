"""Behavioral tests for the oYo-only, opt-in Broadcom STA first-boot helper.

Run: python3 -m pytest tests/test_oyo_broadcom_setup.py
Tests require no network access, root privileges, or kernel module builds.
"""
import hashlib
import os
import subprocess
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (
    ROOT
    / "config/40_brand/oYo/overlay/usr/libexec/oyo-broadcom-setup.sh"
)


def setup_env(tmp_path, pci_id="14e4:43a0", config="14e4:43a0\n"):
    devices = tmp_path / "pci"
    devices.mkdir()
    target = devices / "0000:01:00.0"
    target.mkdir()
    (target / "vendor").write_text(f"0x{pci_id[:4]}\n")
    (target / "device").write_text(f"0x{pci_id[5:]}\n")
    (target / "class").write_text("0x028000\n")
    ids = tmp_path / "ids.txt"
    ids.write_text(config)
    deb_dir = tmp_path / "packages"
    deb_dir.mkdir()
    mock_bin = tmp_path / "mock-bin"
    mock_bin.mkdir()
    env = dict(
        os.environ,
        OYO_BROADCOM_PCI_DIR=str(devices),
        OYO_BROADCOM_IDS_FILE=str(ids),
        OYO_BROADCOM_DEB_DIR=str(deb_dir),
        OYO_BROADCOM_MODULES_DIR=str(tmp_path / "modules"),
        PATH=f"{mock_bin}:{os.environ['PATH']}",
    )
    return env, target, mock_bin, deb_dir


def run_script(env, *args):
    return subprocess.run(["/bin/sh", str(SCRIPT), *args], env=env, text=True, capture_output=True)


def mock_command(mock_bin, name, body):
    path = mock_bin / name
    path.write_text("#!/bin/sh\nset -eu\n" + body + "\n")
    path.chmod(0o755)


def test_non_target_exits_without_packages(tmp_path):
    env, target, mock_bin, _ = setup_env(tmp_path, pci_id="14e4:4401")
    mock_command(mock_bin, "apt-get", "exit 99")
    result = run_script(env)
    assert result.returncode == 0, result.stderr
    assert "No wl-only PCI device" in result.stdout


def test_only_configured_ids_match_and_can_expand(tmp_path):
    env, target, _, _ = setup_env(tmp_path, pci_id="14e4:43b1")
    assert run_script(env, "--detect-only").returncode == 1
    (tmp_path / "ids.txt").write_text("# Approved PCI IDs\n14e4:43a0\n14e4:43b1\n")
    result = run_script(env, "--detect-only")
    assert result.returncode == 0, result.stderr
    assert "Matched PCI ID 14e4:43b1" in result.stdout


def test_invalid_config_fails_closed(tmp_path):
    env, _, _, _ = setup_env(tmp_path, config="14e4:43a0\nnot-an-id\n")
    result = run_script(env)
    assert result.returncode == 1
    assert "Invalid PCI ID list" in result.stderr


def test_broadcom_wired_adapter_prevents_installation(tmp_path):
    env, target, mock_bin, _ = setup_env(tmp_path)
    ethernet = target.parent / "0000:02:00.0"
    ethernet.mkdir()
    (ethernet / "vendor").write_text("0x14e4\n")
    (ethernet / "device").write_text("0x170c\n")
    (ethernet / "class").write_text("0x020000\n")
    mock_command(mock_bin, "apt-get", "exit 99")
    result = run_script(env)
    assert result.returncode == 0, result.stderr
    assert "refusing STA installation" in result.stdout


def setup_installed_mock(tmp_path, env, mock_bin):
    calls = tmp_path / "calls.txt"
    env["MOCK_CALLS"] = str(calls)
    mock_command(mock_bin, "dpkg-query", "printf 'install ok installed\\n'")
    mock_command(mock_bin, "modinfo", "exit 0")
    mock_command(mock_bin, "modprobe", 'echo "modprobe $*" >> "$MOCK_CALLS"')
    mock_command(mock_bin, "apt-get", "exit 99")
    return calls


def test_already_installed_avoids_apt_and_loads_module(tmp_path):
    env, target, mock_bin, _ = setup_env(tmp_path)
    calls = setup_installed_mock(tmp_path, env, mock_bin)
    driver = tmp_path / "wl"
    driver.mkdir()
    (target / "driver").symlink_to(driver, target_is_directory=True)
    result = run_script(env)
    assert result.returncode == 0, result.stderr
    assert "Broadcom STA ready" in result.stdout
    assert "modprobe wl" in calls.read_text()


def test_verified_bcma_bridge_is_switched_to_wl(tmp_path):
    env, target, mock_bin, _ = setup_env(tmp_path)
    calls = setup_installed_mock(tmp_path, env, mock_bin)
    driver = tmp_path / "bcma-pci-bridge"
    driver.mkdir()
    (target / "driver").symlink_to(driver, target_is_directory=True)
    wl = tmp_path / "wl"
    wl.mkdir()
    mock_command(mock_bin, "modprobe", '''echo "modprobe $*" >> "$MOCK_CALLS"
if [ "${1:-}" = "-r" ]; then
    rm "$MOCK_TARGET/driver"
else
    ln -s "$MOCK_WL" "$MOCK_TARGET/driver"
fi''')
    env.update(MOCK_TARGET=str(target), MOCK_WL=str(wl))
    result = run_script(env)
    assert result.returncode == 0, result.stderr
    assert "Broadcom STA ready" in result.stdout
    assert calls.read_text().splitlines() == [
        "modprobe -r b43 ssb bcma",
        "modprobe wl",
    ]


def test_unexpected_driver_is_not_unbound(tmp_path):
    env, target, mock_bin, _ = setup_env(tmp_path)
    calls = setup_installed_mock(tmp_path, env, mock_bin)
    driver = tmp_path / "some-other-driver"
    driver.mkdir()
    (target / "driver").symlink_to(driver, target_is_directory=True)
    result = run_script(env)
    assert result.returncode == 1
    assert "unexpected driver" in result.stderr
    assert not calls.exists(), "must not touch an unexpected bound device"


def test_bcma_switch_refused_when_another_bridge_is_bound(tmp_path):
    env, target, mock_bin, _ = setup_env(tmp_path)
    calls = setup_installed_mock(tmp_path, env, mock_bin)
    driver = tmp_path / "bcma-pci-bridge"
    driver.mkdir()
    (target / "driver").symlink_to(driver, target_is_directory=True)
    other = target.parent / "0000:02:00.0"
    other.mkdir()
    (other / "driver").symlink_to(driver, target_is_directory=True)
    result = run_script(env)
    assert result.returncode == 1
    assert "Another PCI device" in result.stderr
    assert not calls.exists()


def test_switch_refused_for_unverified_pci_id(tmp_path):
    env, target, mock_bin, _ = setup_env(
        tmp_path, pci_id="14e4:43b1", config="14e4:43b1\n"
    )
    calls = setup_installed_mock(tmp_path, env, mock_bin)
    driver = tmp_path / "bcma-pci-bridge"
    driver.mkdir()
    (target / "driver").symlink_to(driver, target_is_directory=True)
    result = run_script(env)
    assert result.returncode == 1
    assert "unverified" in result.stderr
    assert not calls.exists()


def test_switch_failure_does_not_load_wl(tmp_path):
    env, target, mock_bin, _ = setup_env(tmp_path)
    calls = setup_installed_mock(tmp_path, env, mock_bin)
    driver = tmp_path / "bcma-pci-bridge"
    driver.mkdir()
    (target / "driver").symlink_to(driver, target_is_directory=True)
    mock_command(mock_bin, "modprobe", '''echo "modprobe $*" >> "$MOCK_CALLS"
[ "${1:-}" = "-r" ] && exit 1
exit 0''')
    result = run_script(env)
    assert result.returncode == 1
    assert "Cannot release" in result.stderr
    assert calls.read_text().splitlines() == ["modprobe -r b43 ssb bcma"]


def test_missing_headers_do_not_install(tmp_path):
    env, target, mock_bin, _ = setup_env(tmp_path)
    mock_command(mock_bin, "dpkg-query", "exit 1")
    mock_command(mock_bin, "apt-get", "exit 99")
    result = run_script(env)
    assert result.returncode == 1
    assert "Kernel headers are missing" in result.stderr


def test_offline_local_deb_is_installed_once(tmp_path):
    env, target, mock_bin, deb_dir = setup_env(tmp_path)
    calls = tmp_path / "calls.txt"
    marker = tmp_path / "installed"
    env.update(MOCK_CALLS=str(calls), MOCK_MARKER=str(marker), MOCK_TMP=str(tmp_path), MOCK_PCI=str(target), MOCK_DRV=str(tmp_path / "wl"))
    (tmp_path / "wl").mkdir()
    kernel = subprocess.check_output(["uname", "-r"], text=True).strip()
    headers = tmp_path / "modules" / kernel / "build"
    headers.mkdir(parents=True)
    (headers / "Makefile").write_text("# test kernel headers\n")
    deb = deb_dir / "broadcom-sta-dkms_6.30.223.271-26_amd64.deb"
    deb.write_bytes(b"fake-local-deb")
    checksum = hashlib.sha256(deb.read_bytes()).hexdigest()
    (deb_dir / (deb.name + ".sha256")).write_text(f"{checksum}  {deb.name}\n")
    mock_command(mock_bin, "dpkg-query", 'if [ -f "$MOCK_MARKER" ]; then echo "install ok installed"; else exit 1; fi')
    mock_command(mock_bin, "modinfo", '[ -f "$MOCK_MARKER" ]')
    mock_command(mock_bin, "modprobe", 'echo "modprobe $*" >> "$MOCK_CALLS"; ln -s "$MOCK_DRV" "$MOCK_PCI/driver"')
    mock_command(mock_bin, "mktemp", '/usr/bin/mktemp -d "$MOCK_TMP/oyo-apt.XXXXXX"')
    mock_command(mock_bin, "apt-get", 'echo "apt-get $*" >> "$MOCK_CALLS"; touch "$MOCK_MARKER"')

    first = run_script(env)
    assert first.returncode == 0, first.stderr
    assert "Broadcom STA ready" in first.stdout
    assert str(deb) in calls.read_text()
    assert "--no-download" not in calls.read_text()
    assert calls.read_text().count("apt-get ") == 1

    second = run_script(env)
    assert second.returncode == 0, second.stderr
    assert calls.read_text().count("apt-get ") == 1


def test_additional_broadcom_wifi_prevents_installation(tmp_path):
    env, target, mock_bin, _ = setup_env(tmp_path)
    second = target.parent / "0000:02:00.0"
    second.mkdir()
    (second / "vendor").write_text("0x14e4\n")
    (second / "device").write_text("0x43b1\n")
    (second / "class").write_text("0x028000\n")
    mock_command(mock_bin, "apt-get", "exit 99")
    result = run_script(env)
    assert result.returncode == 0, result.stderr
    assert "additional Broadcom network adapter" in result.stdout


def test_offline_install_then_switches_verified_bcma_device(tmp_path):
    env, target, mock_bin, deb_dir = setup_env(tmp_path)
    calls = tmp_path / "calls.txt"
    marker = tmp_path / "installed"
    kernel = subprocess.check_output(["uname", "-r"], text=True).strip()
    headers = tmp_path / "modules" / kernel / "build"
    headers.mkdir(parents=True)
    (headers / "Makefile").write_text("# test kernel headers\n")
    deb = deb_dir / "broadcom-sta-dkms_6.30.223.271-26_amd64.deb"
    deb.write_bytes(b"fake-local-deb")
    checksum = hashlib.sha256(deb.read_bytes()).hexdigest()
    (deb_dir / (deb.name + ".sha256")).write_text(f"{checksum}  {deb.name}\n")
    bcma = tmp_path / "bcma-pci-bridge"
    bcma.mkdir()
    wl = tmp_path / "wl"
    wl.mkdir()
    (target / "driver").symlink_to(bcma, target_is_directory=True)
    env.update(MOCK_CALLS=str(calls), MOCK_MARKER=str(marker), MOCK_TARGET=str(target), MOCK_WL=str(wl), MOCK_TMP=str(tmp_path))
    mock_command(mock_bin, "dpkg-query", 'if [ -f "$MOCK_MARKER" ]; then echo "install ok installed"; else exit 1; fi')
    mock_command(mock_bin, "modinfo", '[ -f "$MOCK_MARKER" ]')
    mock_command(mock_bin, "mktemp", '/usr/bin/mktemp -d "$MOCK_TMP/oyo-apt.XXXXXX"')
    mock_command(mock_bin, "apt-get", 'echo "apt-get $*" >> "$MOCK_CALLS"; touch "$MOCK_MARKER"')
    mock_command(mock_bin, "modprobe", '''echo "modprobe $*" >> "$MOCK_CALLS"
if [ "${1:-}" = "-r" ]; then
    rm "$MOCK_TARGET/driver"
else
    ln -s "$MOCK_WL" "$MOCK_TARGET/driver"
fi''')
    result = run_script(env)
    assert result.returncode == 0, result.stderr
    assert "Broadcom STA ready" in result.stdout
    calls_list = calls.read_text().splitlines()
    assert calls_list[0].startswith("apt-get ")
    assert calls_list[1:] == ["modprobe -r b43 ssb bcma", "modprobe wl"]
