#!/usr/bin/env bash
# ================================================
#   AILab 網路磁碟機掛載 (Linux / macOS)
#   對應 Windows 版 lab_NAS.cmd
# ================================================
set -u

MOUNT_BASE="$HOME/AILab"
ERRFILE="$(mktemp 2>/dev/null || echo /tmp/nas_err.$$)"
OS="$(uname -s)"

echo "================================================"
echo "  AILab 網路磁碟機掛載 ($OS)"
echo "================================================"
echo

# Linux 需要 cifs-utils
if [ "$OS" = "Linux" ] && ! command -v mount.cifs >/dev/null 2>&1; then
    echo "  [提示] 未偵測到 cifs-utils，請先安裝："
    echo "         Ubuntu/Debian : sudo apt install -y cifs-utils"
    echo "         RHEL/CentOS   : sudo yum install -y cifs-utils"
    echo
fi

# map_mount <掛載名稱> <伺服器> <分享> <帳號> <密碼>
map_mount() {
    _name="$1"; _server="$2"; _share="$3"; _user="$4"; _pass="$5"
    _target="$MOUNT_BASE/$_name"
    _unc="//$_server/$_share"
    mkdir -p "$_target" 2>/dev/null

    if [ "$OS" = "Darwin" ]; then
        # macOS：先卸載舊的，再以 mount_smbfs 掛載
        umount "$_target" >/dev/null 2>&1
        if mount_smbfs "//$_user:$_pass@$_server/$_share" "$_target" 2>"$ERRFILE"; then
            echo "  [成功]  $_target  ->  $_unc"
        else
            echo "  [失敗]  $_target  ->  $_unc"
            sed 's/^/         /' "$ERRFILE"
        fi
    else
        # Linux：需要 root；逐一嘗試 SMB 協定版本
        sudo umount "$_target" >/dev/null 2>&1
        _ok=0
        for _vers in 3.1.1 3.0 2.1 1.0; do
            if sudo mount -t cifs "$_unc" "$_target" \
                -o username="$_user",password="$_pass",uid="$(id -u)",gid="$(id -g)",vers="$_vers" \
                2>"$ERRFILE"; then
                echo "  [成功]  $_target  ->  $_unc   (vers=$_vers)"
                _ok=1
                break
            fi
        done
        if [ "$_ok" -ne 1 ]; then
            echo "  [失敗]  $_target  ->  $_unc"
            sed 's/^/         /' "$ERRFILE"
        fi
    fi
}

echo
map_mount "ailab"     "140.123.106.219" "ailab"     "user"     "ailab120"
map_mount "temp"      "140.123.106.219" "temp"      "user"     "ailab120"
map_mount "DGX"       "140.123.106.247" "DGX"       "dgx_user" "w6V2lqW_"
map_mount "workspace" "140.123.106.247" "workspace" "dgx_user" "w6V2lqW_"

rm -f "$ERRFILE" 2>/dev/null

echo
echo "================================================"
echo "  目前掛載狀態"
echo "================================================"
if [ "$OS" = "Darwin" ]; then
    mount | grep -i smbfs || echo "  (無 SMB 掛載)"
else
    mount | grep -i cifs || echo "  (無 CIFS 掛載)"
fi
echo
echo "掛載點位於：$MOUNT_BASE"
