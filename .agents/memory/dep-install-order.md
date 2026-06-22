---
name: Dependency install order
description: Installation order matters — discord.py (git) must be installed LAST or other packages overwrite it with an older version.
---

## Rule
Always run `install.sh` (not plain `pip install -r requirements.txt`) in this project.

**Why:** jishaku, discord-ext-menus, and reactionmenu all declare `discord.py` as a pip dependency and pull in a pinned older version. When installed together, whichever runs last wins the `discord` module path. The git version of discord.py must win.

**How to apply:**
1. Install all other packages first
2. Install jishaku with `--no-deps` to prevent it pulling in the old discord.py
3. The discord.py git version stays as the winner

See `install.sh` for the correct sequence.
