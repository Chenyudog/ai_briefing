#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "$0")/.."

applications="${XDG_DATA_HOME:-$HOME/.local/share}/applications"
mkdir -p "$applications"
cat > "$applications/ai-briefing.desktop" <<DESKTOP
[Desktop Entry]
Type=Application
Name=我的手记服务器
Comment=启动本机网站并在浏览器打开
Exec="$PWD/deploy/menu.sh"
Terminal=true
Icon=applications-internet
Categories=Network;
Actions=Stop;

[Desktop Action Stop]
Name=停止服务
Exec="$PWD/deploy/menu.sh" stop
DESKTOP
printf '已安装。打开 Ubuntu 应用菜单，搜索「我的手记服务器」。\n'
