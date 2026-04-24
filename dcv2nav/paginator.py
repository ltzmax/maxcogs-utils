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
from typing import Any, Union

import discord


# Pages can be either plain text strings or pre-built component lists.
PageType = Union[str, list]


class _NavBtn(discord.ui.Button):
    """Navigation button for any paginator-like view.

    Works with any object that exposes:
    - ``author`` - the user who invoked the view
    - ``current`` - current page index (int)
    - ``pages`` - list of pages
    - ``_build_content()`` - rebuilds the view

    Holds an explicit reference so it works correctly inside Containers.
    """

    def __init__(
        self,
        direction: str,
        paginator: Any,
        disabled: bool = False,
    ) -> None:
        label = "◀" if direction == "prev" else "▶"
        super().__init__(
            label=label,
            style=discord.ButtonStyle.secondary,
            disabled=disabled,
        )
        self.direction = direction
        self.paginator = paginator

    async def callback(self, interaction: discord.Interaction) -> None:
        if interaction.user != self.paginator.author:
            return await interaction.response.send_message(
                "You are not the author of this paginator.", ephemeral=True
            )
        if self.direction == "prev" and self.paginator.current > 0:
            self.paginator.current -= 1
        elif self.direction == "next" and self.paginator.current < len(self.paginator.pages) - 1:
            self.paginator.current += 1
        self.paginator._build_content()
        await interaction.response.edit_message(view=self.paginator)


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
            [
                discord.ui.TextDisplay("## Article 2\nAnother summary"),
            ],
        ]
        view = LayoutViewPaginator(pages, ctx)
        view.message = await ctx.send(view=view)

    The ◀ ``current/total`` ▶ nav bar is always rendered. The ◀ and ▶ buttons
    are disabled automatically at the first and last page.

    Parameters
    ----------
    pages:
        List of page content. Each item is either a ``str`` or a ``list`` of
        discord UI components.
    ctx:
        The command context. Used to restrict nav interactions to the author.
    timeout:
        View timeout in seconds. Defaults to 120. Set to ``None`` for no timeout.
    """

    def __init__(
        self,
        pages: list[PageType],
        ctx,
        timeout: int | None = 120,
    ) -> None:
        super().__init__(timeout=timeout)
        if not pages:
            raise ValueError("pages must not be empty")
        self.pages = pages
        self.current = 0
        self.message = None
        self.author = ctx.author
        self._build_content()

    def _build_content(self, disabled: bool = False) -> None:
        self.clear_items()

        page = self.pages[self.current]
        if isinstance(page, str):
            content_components: list = [discord.ui.TextDisplay(page)]
        else:
            content_components = list(page)

        nav_row = discord.ui.ActionRow(
            _NavBtn("prev", self, disabled=disabled or self.current == 0),
            discord.ui.Button(
                label=f"{self.current + 1}/{len(self.pages)}",
                style=discord.ButtonStyle.secondary,
                disabled=True,
            ),
            _NavBtn("next", self, disabled=disabled or self.current == len(self.pages) - 1),
        )

        self.add_item(discord.ui.Container(
            *content_components,
            discord.ui.Separator(),
            nav_row,
        ))

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        # Individual nav buttons do their own author check before editing.
        # This base check is kept as a fallback for any other interactions.
        return True

    async def on_timeout(self) -> None:
        self._build_content(disabled=True)
        if self.message:
            with contextlib.suppress(discord.HTTPException):
                await self.message.edit(view=self)
