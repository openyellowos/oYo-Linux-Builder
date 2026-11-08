#!/bin/sh
# Install Broadcom STA from the bundled deb only on explicitly approved PCI IDs.
# Standard Debian drivers and modprobe settings remain untouched on other PCs.
set -eu

PACKAGE=broadcom-sta-dkms
DEB_DIR=${OYO_BROADCOM_DEB_DIR:-/usr/share/openyellowos/offline-drivers/broadcom}
IDS_FILE=${OYO_BROADCOM_IDS_FILE:-$DEB_DIR/wl-pci-ids.txt}
PCI_DIR=${OYO_BROADCOM_PCI_DIR:-/sys/bus/pci/devices}
MODULES_DIR=${OYO_BROADCOM_MODULES_DIR:-/lib/modules}

log() { printf '%s\n' "[oyo-broadcom] $*"; }
fail() { log "ERROR: $*" >&2; exit 1; }

case "${1:-}" in
    '') ;;
    --detect-only) ;;
    *) fail "usage: $0 [--detect-only]" ;;
esac

[ -r "$IDS_FILE" ] || fail "Missing PCI ID list: $IDS_FILE"
[ -d "$PCI_DIR" ] || fail "Missing PCI sysfs directory: $PCI_DIR"

# Fail closed on a mistyped ID rather than silently ignoring the configuration.
if grep -nEv '^([[:space:]]*|[[:space:]]*#.*|[[:xdigit:]]{4}:[[:xdigit:]]{4})$' "$IDS_FILE"; then
    fail "Invalid PCI ID list format: $IDS_FILE"
fi

TARGET=
MATCHED_ID=
for pci in "$PCI_DIR"/*; do
    [ -r "$pci/vendor" ] && [ -r "$pci/device" ] || continue
    vendor=$(cat "$pci/vendor")
    device=$(cat "$pci/device")
    id="${vendor#0x}:${device#0x}"
    if grep -Fxiq "$id" "$IDS_FILE"; then
        TARGET=$pci
        MATCHED_ID=$id
        log "Matched PCI ID $id (${pci##*/})"
        break
    fi
done

if [ -z "$TARGET" ]; then
    [ "${1:-}" = --detect-only ] && exit 1
    log "No wl-only PCI device found; keeping standard Debian drivers"
    exit 0
fi

# This option is useful for non-mutating hardware-detection tests.
[ "${1:-}" = --detect-only ] && exit 0

# Debian's broadcom-sta-dkms blacklists b44/ssb as well as Wi-Fi drivers.
# Preserve Broadcom wired networking, and do not change module ownership on
# multi-adapter systems until that combination has been separately tested.
for pci in "$PCI_DIR"/*; do
    [ -r "$pci/vendor" ] && [ -r "$pci/class" ] || continue
    [ "$(cat "$pci/vendor")" = 0x14e4 ] || continue
    class=$(cat "$pci/class")
    if [ "$class" = 0x020000 ]; then
        log "WARNING: Broadcom PCI Ethernet (${pci##*/}) detected; refusing STA installation to protect b44"
        exit 0
    fi
    if [ "$pci" != "$TARGET" ]; then
        case "$class" in
            0x02*)
                log "WARNING: additional Broadcom network adapter (${pci##*/}) detected; refusing STA installation"
                exit 0
                ;;
        esac
    fi
done

KVER=$(uname -r)

if dpkg-query -W -f='${Status}' "$PACKAGE" 2>/dev/null |
        grep -qx 'install ok installed'; then
    log "$PACKAGE is already installed"
else
    [ -f "$MODULES_DIR/$KVER/build/Makefile" ] ||
        fail "Kernel headers are missing for $KVER"

    # Exactly one bundled package, from the ISO built with the matching kernel.
    set -- "$DEB_DIR"/broadcom-sta-dkms_*.deb
    [ "$#" -eq 1 ] && [ -f "$1" ] ||
        fail "Expected one bundled broadcom-sta-dkms deb under $DEB_DIR"
    DEB=$1
    [ -r "$DEB.sha256" ] || fail "Missing sha256 file: $DEB.sha256"

    # Verify both files before invoking APT. APT still owns dpkg/DKMS/configuration.
    (cd "$DEB_DIR" && sha256sum -c "${DEB##*/}.sha256") ||
        fail "Bundled deb checksum verification failed"

    # Isolate APT's sources, so it cannot fetch dependencies from the network.
    # Deliberately do NOT pass --no-download: it breaks local-deb installs on apt.
    APT_TEMP=$(mktemp -d /run/oyo-broadcom-apt.XXXXXX) ||
        fail 'Cannot create temporary APT sources directory'
    trap 'rm -rf -- "$APT_TEMP"' EXIT
    mkdir -p "$APT_TEMP/sources.list.d"
    : > "$APT_TEMP/sources.list"

    log "Installing bundled ${DEB##*/} (offline)"
    DEBIAN_FRONTEND=noninteractive apt-get -y \
        -o "Dir::Etc::sourcelist=$APT_TEMP/sources.list" \
        -o "Dir::Etc::sourceparts=$APT_TEMP/sources.list.d" \
        -o Dpkg::Use-Pty=0 \
        -o DPkg::Lock::Timeout=120 \
        -o APT::Install-Recommends=false \
        install "$DEB" || fail 'Offline Broadcom STA installation failed'

    if ! dpkg-query -W -f='${Status}' "$PACKAGE" 2>/dev/null |
            grep -qx 'install ok installed'; then
        fail 'APT returned without an installed Broadcom STA package'
    fi
fi

# After a kernel update, Debian's DKMS mechanism usually rebuilds wl itself.
# Recover conservatively if a correctly installed package has no current module.
if ! modinfo -k "$KVER" wl >/dev/null 2>&1; then
    log "No wl module for $KVER; invoking DKMS autoinstall"
    [ -f "$MODULES_DIR/$KVER/build/Makefile" ] ||
        fail "Kernel headers are missing for $KVER"
    dkms autoinstall -k "$KVER" || fail 'DKMS rebuild failed'
fi
modinfo -k "$KVER" wl >/dev/null 2>&1 ||
    fail "wl module is not available for $KVER"

if [ -L "$TARGET/driver" ]; then
    CURRENT=$(basename "$(readlink "$TARGET/driver")")
    case "$CURRENT" in
        wl)
            log "Target PCI device is already bound to wl"
            ;;
        bcma-pci-bridge)
            # Confirmed by a live BCM4360 (14e4:43a0) test: releasing these
            # modules and loading wl makes the wireless adapter usable.
            # Never generalize this operation to new allowlisted IDs without
            # hardware validation. Do not force removal of busy modules.
            [ "$MATCHED_ID" = 14e4:43a0 ] ||
                fail "Automatic bcma-to-wl switching is unverified for $MATCHED_ID"

            # modprobe -r affects modules system-wide. Refuse to remove bcma
            # when another PCI device is also directly using its bridge.
            for pci in "$PCI_DIR"/*; do
                [ "$pci" != "$TARGET" ] && [ -L "$pci/driver" ] || continue
                other_driver=$(basename "$(readlink "$pci/driver")")
                if [ "$other_driver" = bcma-pci-bridge ]; then
                    fail "Another PCI device (${pci##*/}) uses bcma-pci-bridge; refusing switch"
                fi
            done

            log "Switching BCM4360 from bcma-pci-bridge to wl"
            modprobe -r b43 ssb bcma ||
                fail 'Cannot release b43/ssb/bcma (possibly used by another device); not forcing removal'
            if [ -L "$TARGET/driver" ]; then
                fail 'Target is still bound after releasing the conflicting modules'
            fi
            ;;
        *)
            fail "Target is bound to unexpected driver $CURRENT; refusing automatic switch"
            ;;
    esac
fi

# Use the Debian-owned module; do not add any global modprobe blacklist here.
modprobe wl || fail 'Unable to load wl (check kernel/DKMS/Secure Boot and conflicting modules)'

if [ ! -L "$TARGET/driver" ] ||
   [ "$(basename "$(readlink "$TARGET/driver")")" != wl ]; then
    fail "wl loaded but did not bind the PCI device (${TARGET##*/}); inspect journalctl -u oyo-broadcom-setup"
fi

log "Broadcom STA ready on ${TARGET##*/}"
