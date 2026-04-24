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


log = getLogger("red.dcv2nav.select_paginator")


class _SelectPaginatorSelect(discord.ui.Select):
    """Select menu for any paginator-like view.

    Works with any object that exposes:
    - ``author`` - the user who invoked the view
    - ``current`` - current page index (int), set to the selected value
    - ``_build_content()`` - rebuilds the view

    Holds an explicit reference so it works correctly inside Containers.

    Parameters
    ----------
    paginator:
        The paginator view that owns this select.
    options:
        List of ``discord.SelectOption`` items to display.
    placeholder:
        Placeholder text shown when nothing is selected.
    disabled:
        Whether the select is disabled. Defaults to ``False``.
    """

    def __init__(
        self,
        paginator: Any,
        options: list[discord.SelectOption],
        placeholder: str = "Choose a page...",
        disabled: bool = False,
    ) -> None:
        super().__init__(
            placeholder=placeholder,
            options=options,
            disabled=bool(disabled),
        )
        self.paginator = paginator

    async def callback(self, interaction: discord.Interaction) -> None:
        if interaction.user != self.paginator.author:
            return await interaction.response.send_message(
                "You are not the author of this select menu.", ephemeral=True
            )
        try:
            self.paginator.current = int(self.values[0])
            self.paginator._build_content()
            await interaction.response.edit_message(view=self.paginator)
        except discord.HTTPException as e:
            log.error("Failed to edit select paginator message: %s", e)
        except Exception as e:
            log.error("Unexpected error in _SelectPaginatorSelect callback: %s", e, exc_info=True)


class SelectPaginator(discord.ui.LayoutView):
    """Components v2 select-menu paginator for Red-DiscordBot cogs.

    Displays a select menu to jump directly to any page. Each option label
    is generated from the ``labels`` list you provide, making it easy to show
    meaningful game/match/item names.

    .. code-block:: python

        pages = ["## Heat vs Lakers\nScore: 102-98", "## Celtics vs Nets\nScore: 110-105"]
        labels = ["Heat vs Lakers", "Celtics vs Nets"]
        view = SelectPaginator(pages, labels, ctx)
        view.message = await ctx.send(view=view)

    Each option in the select menu can optionally have a custom emoji set via
    the ``option_emojis`` parameter.

    Parameters
    ----------
    pages:
        List of page content. Each item is either a ``str`` or a ``list`` of
        discord UI components.
    labels:
        List of human-readable option labels shown in the select menu.
        Must be the same length as ``pages``. Labels are truncated to 100
        characters automatically.
    ctx:
        The command context.
    placeholder:
        Placeholder text shown in the select menu when nothing is selected.
        Defaults to ``"Choose a page..."``.
    timeout:
        View timeout in seconds. Defaults to 120.
    option_emojis:
        Optional list of emojis, one per page option. Each item can be a
        ``str``, ``discord.Emoji``, or ``discord.PartialEmoji``. If provided,
        must be the same length as ``pages``. Use ``None`` entries to skip
        an emoji for a specific option.
    """

    def __init__(
        self,
        pages: list,
        labels: list[str],
        ctx,
        placeholder: str = "Choose a page...",
        timeout: int | None = 120,
        option_emojis: Optional[list[Optional[Union[str, discord.Emoji, discord.PartialEmoji]]]] = None,
    ) -> None:
        super().__init__(timeout=timeout)
        if not pages:
            raise ValueError("pages must not be empty")
        if len(pages) != len(labels):
            raise ValueError("pages and labels must be the same length")
        if option_emojis is not None and len(option_emojis) != len(pages):
            raise ValueError("option_emojis must be the same length as pages")
        self.pages = pages
        self.current = 0
        self.message = None
        self.author = ctx.author
        self.placeholder = placeholder
        self._options = [
            discord.SelectOption(
                label=label[:100],
                value=str(i),
                emoji=option_emojis[i] if option_emojis else None,
            )
            for i, label in enumerate(labels)
        ]
        self._build_content()

    def _build_content(self, disabled: bool = False) -> None:
        self.clear_items()

        page = self.pages[self.current]
        content_components: list = (
            [discord.ui.TextDisplay(page)] if isinstance(page, str) else list(page)
        )

        self.add_item(discord.ui.Container(
            *content_components,
            discord.ui.Separator(),
            discord.ui.ActionRow(
                _SelectPaginatorSelect(
                    self, self._options, placeholder=self.placeholder, disabled=bool(disabled)
                )
            ),
        ))

    async def on_timeout(self) -> None:
        self._build_content(disabled=True)
        if self.message:
            with contextlib.suppress(discord.HTTPException, RuntimeError):
                await self.message.edit(view=self)
