---
name: Discord bot library setup
description: This bot uses discord.py 2.x exclusively. py-cord was listed in requirements by mistake and conflicts.
---

## Rule
Use `discord.py @ git+https://github.com/Rapptz/discord.py` — NOT py-cord.

**Why:** The codebase uses discord.py 2.x-only APIs: `commands.hybrid_command`, `discord.TextStyle`, `app_commands`. py-cord is a fork that diverged and does not have these. Both install to the same `discord` namespace so they cannot coexist.

**How to apply:** Never add `py-cord` to requirements. If a dependency pulls in `discord.py` (jishaku, discord-ext-menus), install it with `--no-deps` or ensure discord.py git is installed last and wins.

## Other packages required (not in discord.py itself)
- `discord-ext-menus==1.1` — for `discord.ext.menus` (paginators)
- `discord-games` — for `discord_games` import in Games cog
- `reactionmenu` — used in some cogs
- `tasksio` — used in event cogs
- `jishaku @ git+https://github.com/Gorialis/jishaku` with `--no-deps`
