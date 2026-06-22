#!/bin/bash
# DILBAR < 3 — Dependency installer
# Run ONCE on a fresh environment before start.sh

set -e

echo "[install] Installing all dependencies..."
pip install -q \
    "discord.py @ git+https://github.com/Rapptz/discord.py" \
    "discord-ext-menus==1.1" \
    "discord-games" \
    "reactionmenu" \
    "tasksio" \
    "Flask>=3.0.0" \
    "requests==2.28.1" \
    "async-timeout==4.0.2" \
    "python-dotenv==1.0.0" \
    "psutil>=5.9.0" \
    "httpx>=0.23.0" \
    "wavelink==1.3.3" \
    "import_expression" \
    "braceexpand" \
    "tabulate"

echo "[install] Installing jishaku (no-deps to avoid version conflicts)..."
pip install --no-deps -q "jishaku @ git+https://github.com/Gorialis/jishaku"

echo "[install] Done!"
python3 -c "import discord; print('[install] discord.py version:', discord.__version__)"
