"""
MIT License

Copyright (c) 2026-present ltzmax

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from __future__ import annotations

import contextlib
from typing import Any, Optional, Union

import discord
from red_commons.logging import getLogger


log = getLogger("red.dcv2nav.paginator")

# Pages can be either plain text strings or pre-built component lists.
PageType = Union[str, list]

# Default nav button labels
_DEFAULT_PREV = "\u25c4"
_DEFAULT_NEXT = "\u25ba"


class _NavBtn(discord.ui.Button):
    """Navigation button for any paginator-like view.

    Works with any object that exposes:
    - ``author`` - the user who invoked the view
    - ``current`` - current page index (int)
    - ``pages`` - list of pages
    - ``_build_content()`` - rebuilds the view

    Holds an explicit reference so it works correctly inside Containers.

    Parameters
    ----------
    direction:
        ``"prev"`` or ``"next"``.
    paginator:
        The paginator view that owns this button.
    disabled:
        Whether the button is disabled. Defaults to ``False``.
    emoji:
        Optional custom emoji instead of the default labels.
        Accepts a ``str`` (Unicode or ``<:name:id>`` format) or a
        ``discord.Emoji`` / ``discord.PartialEmoji`` instance.
        When set, the text label is hidden.
    """

    def __init__(
        self,
        direction: str,
        paginator: Any,
        disabled: bool = False,
        emoji: Optional[Union[str, discord.Emoji, discord.PartialEmoji]] = None,
    ) -> None:
        label = None if emoji else (_DEFAULT_PREV if direction == "prev" else _DEFAULT_NEXT)
        super().__init__(
            label=label,
            emoji=emoji,
            style=discord.ButtonStyle.secondary,
            disabled=bool(disabled),
        )
        self.direction = direction
        self.paginator = paginator

    async def callback(self, interaction: discord.Interaction) -> None:
        if interaction.user != self.paginator.author:
            return await interaction.response.send_message(
                "You are not the author of this paginator.", ephemeral=True
            )
        try:
            if self.direction == "prev" and self.paginator.current > 0:
                self.paginator.current -= 1
            elif self.direction == "next" and self.paginator.current < len(self.paginator.pages) - 1:
                self.paginator.current += 1
            self.paginator._build_content()
            await interaction.response.edit_message(view=self.paginator)
        except discord.HTTPException as e:
            log.error("Failed to edit paginator message: %s", e)
        except Exception as e:
            log.error("Unexpected error in _NavBtn callback: %s", e, exc_info=True)


class LayoutViewPaginator(discord.ui.LayoutView):
    """Drop-in Components v2 paginator for Red-DiscordBot cogs.

    Supports two page formats:

    **String pages** - each page is a plain text string rendered as a
    ``TextDisplay`` inside a ``Container``:

    .. code-block:: python

        pages = ["## Page 1\nSome content", "## Page 2\nMore content"]
        view = LayoutViewPaginator(pages, ctx)
        view.message = await ctx.send(view=view)

    **Component list pages** - each page is a list of discord UI components
    (``TextDisplay``, ``ActionRow``, ``Separator``, etc.) assembled directly
    into the ``Container``. Use this when pages need link buttons or other
    interactive components:

    .. code-block:: python

        pages = [
            [
                discord.ui.TextDisplay("## Article 1\nSummary here"),
                discord.ui.ActionRow(
                    discord.ui.Button(style=discord.ButtonStyle.link, label="Read", url="https://...")
                ),
            ],
        ]
        view = LayoutViewPaginator(pages, ctx)
        view.message = await ctx.send(view=view)

    The nav bar is always rendered at the bottom. Prev/next buttons are
    disabled automatically at the first and last page.

    Parameters
    ----------
    pages:
        List of page content. Each item is either a ``str`` or a ``list`` of
        discord UI components.
    ctx:
        The command context. Used to restrict nav interactions to the author.
    timeout:
        View timeout in seconds. Defaults to 120. Set to ``None`` for no timeout.
    prev_emoji:
        Optional custom emoji for the previous button instead of the default label.
    next_emoji:
        Optional custom emoji for the next button instead of the default label.
    """

    def __init__(
        self,
        pages: list[PageType],
        ctx,
        timeout: int | None = 120,
        prev_emoji: Optional[Union[str, discord.Emoji, discord.PartialEmoji]] = None,
        next_emoji: Optional[Union[str, discord.Emoji, discord.PartialEmoji]] = None,
    ) -> None:
        super().__init__(timeout=timeout)
        if not pages:
            raise ValueError("pages must not be empty")
        self.pages = pages
        self.current = 0
        self.message = None
        self.author = ctx.author
        self.prev_emoji = prev_emoji
        self.next_emoji = next_emoji
        self._build_content()

    def _build_content(self, disabled: bool = False) -> None:
        self.clear_items()

        page = self.pages[self.current]
        content_components: list = (
            [discord.ui.TextDisplay(page)] if isinstance(page, str) else list(page)
        )

        nav_row = discord.ui.ActionRow(
            _NavBtn("prev", self, disabled=bool(disabled or self.current == 0), emoji=self.prev_emoji),
            discord.ui.Button(
                label=f"{self.current + 1}/{len(self.pages)}",
                style=discord.ButtonStyle.secondary,
                disabled=True,
            ),
            _NavBtn("next", self, disabled=bool(disabled or self.current == len(self.pages) - 1), emoji=self.next_emoji),
        )

        self.add_item(discord.ui.Container(
            *content_components,
            discord.ui.Separator(),
            nav_row,
        ))

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        # Individual nav buttons do their own author check before editing.
        return True

    async def on_timeout(self) -> None:
        self._build_content(disabled=True)
        if self.message:
            with contextlib.suppress(discord.HTTPException, RuntimeError):
                await self.message.edit(view=self)
