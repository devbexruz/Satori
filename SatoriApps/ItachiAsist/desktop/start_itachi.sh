#!/usr/bin/env bash
# ========================================================
# SATORI ECOSYSTEM — ItachiAssist Launcher Script
# ========================================================

LOCKFILE="/tmp/itachi_assist.lock"

# Yagona nusxa tekshiruvi (Single Instance Check)
exec 200>"$LOCKFILE"
if ! flock -n 200; then
    echo "⚠️ ItachiAssist allaqachon ishlamoqda. Ikkinchi nusxa ochilmadi."
    exit 0
fi

# Grafik ish stoli, audio server (PipeWire) to'liq yuklanishini kutish
sleep 2

# Display va muhit o'zgaruvchilari
export DISPLAY="${DISPLAY:-:0}"
if [ -n "$WAYLAND_DISPLAY" ]; then
    export WAYLAND_DISPLAY="$WAYLAND_DISPLAY"
fi

# PyAutoGUI va xdotool uchun X11 huquqi
xhost +local: >/dev/null 2>&1 || true

BASE_DIR="/home/bexruz/Documents/MyProjects/Satori/SatoriApps/ItachiAsist/desktop"
cd "$BASE_DIR/itachi_core" || exit 1

# Virtual muhit orqali ishga tushirish
exec "$BASE_DIR/venv/bin/python" main.py
