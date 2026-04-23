# dcv2nav

Discord Components v2 navigation views for [Red-DiscordBot](https://github.com/Cog-Creators/Red-DiscordBot) cogs.

Drop-in paginators that use `discord.ui.LayoutView` with the `◀ 1/N ▶` nav bar style. Works with plain text pages or pre-built component lists so you can have link buttons, separators, and other Components v2 elements on any page.

---

## Why

Every time you migrate a cog to Components v2, you end up rewriting the same nav button pattern. This package extracts it so all your cogs share one implementation. Bug fix once, fixed everywhere.

---

## Installation

from source:

```bash
pip install git+https://github.com/ltzmax/maxcogs-utils.git --break-system-packages
```

---

## Requirements

- Python 3.11+
- discord.py 2.x (the version shipped with Red-DiscordBot)

---

## Usage

### `LayoutViewPaginator` ◀ `1/N` ▶ nav bar

The standard paginator. Pages are either plain text strings or lists of discord components.

#### String pages

```python
from dcv2nav import LayoutViewPaginator

pages = [
    "## 🛡️ Shields\n**Wooden Shield ×2**\n-# Reduces loss by 3.0%",
    "## 🔧 Tools\n**Lockpick Kit ×1**\n-# +14% success on Museum Relic",
    "## 💰 Loot\n**Painting ×1**\n-# Sell for 20,000–80,000 credits",
]
view = LayoutViewPaginator(pages, ctx)
view.message = await ctx.send(view=view)
```

#### Component list pages (with link buttons, etc.)

```python
import discord
from dcv2nav import LayoutViewPaginator

pages = [
    [
        discord.ui.TextDisplay("## Article 1\nSummary of the first article."),
        discord.ui.ActionRow(
            discord.ui.Button(
                style=discord.ButtonStyle.link,
                label="Read More",
                url="https://example.com/1",
                emoji="🔗",
            )
        ),
    ],
    [
        discord.ui.TextDisplay("## Article 2\nSummary of the second article."),
        discord.ui.ActionRow(
            discord.ui.Button(
                style=discord.ButtonStyle.link,
                label="Read More",
                url="https://example.com/2",
                emoji="🔗",
            )
        ),
    ],
]
view = LayoutViewPaginator(pages, ctx)
view.message = await ctx.send(view=view)
```

---

### `SelectPaginator` select menu paginator

Use this when you want users to jump directly to a named page (e.g. scoreboard games, inventory sections or whatever you choose to do, just use F strings for your own stuff).

```python
from dcv2nav import SelectPaginator

pages = [
    "## Heat vs Lakers\nScore: 102–98 · Final",
    "## Celtics vs Nets\nScore: 110–105 · Final",
]
labels = ["Heat vs Lakers", "Celtics vs Nets"]

view = SelectPaginator(pages, labels, ctx)
view.message = await ctx.send(view=view)
```

You can also pass component list pages to `SelectPaginator` the same way as `LayoutViewPaginator`.

---

## License

MIT see [LICENSE](LICENSE).
