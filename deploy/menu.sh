#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "$0")/.."

unit=ai-briefing.service
url=http://localhost:8765/
export BRIEFING_PORT=8765

pause() {
    if [[ -t 0 ]]; then
        read -r -p '按回车关闭此窗口。' || true
    fi
}

if [[ "${1:-}" == stop ]]; then
    if systemctl --user is-active --quiet "$unit"; then
        systemctl --user stop "$unit" || { pause; exit 1; }
    fi
    printf 'AI 大事已停止。\n'
    pause
    exit 0
fi

if ! systemctl --user is-active --quiet "$unit"; then
    if ! systemd-run --user --collect --unit="$unit" --working-directory="$PWD" \
        --setenv=BRIEFING_PORT="$BRIEFING_PORT" "$PWD/start.sh"; then
        pause
        exit 1
    fi
fi

for attempt in {1..90}; do
    if curl -fs --max-time 1 "$url" -o /dev/null; then
        printf 'AI 大事已启动。\n%s\n' "$url"
        if [[ -t 0 ]]; then
            xdg-open "$url" >/dev/null 2>&1 || pause
        fi
        exit 0
    fi
    if ! systemctl --user is-active --quiet "$unit"; then
        break
    fi
    sleep 1
done

printf '启动未完成。\n'
journalctl --user -u "$unit" --no-pager -o cat -n 12
pause
exit 1
