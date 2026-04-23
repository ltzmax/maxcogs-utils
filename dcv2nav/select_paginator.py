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

import discord


class _SelectPaginatorSelect(discord.ui.Select):
    """Select menu for SelectPaginator. Holds explicit paginator reference."""

    def __init__(
        self,
        paginator: "SelectPaginator",
        options: list[discord.SelectOption],
        disabled: bool = False,
    ) -> None:
        super().__init__(
            placeholder=paginator.placeholder,
            options=options,
            disabled=disabled,
        )
        self.paginator = paginator

    async def callback(self, interaction: discord.Interaction) -> None:
        if interaction.user != self.paginator.author:
            return await interaction.response.send_message(
                "You are not the author of this select menu.", ephemeral=True
            )
        self.paginator.current = int(self.values[0])
        self.paginator._build_content()
        await interaction.response.edit_message(view=self.paginator)


class SelectPaginator(discord.ui.LayoutView):
    """Components v2 select-menu paginator for Red-DiscordBot cogs.

    Displays a select menu to jump directly to any page. Each option label
    is generated from the ``labels`` list you provide, making it easy to show
    meaningful game/match/item names.

    This is just example, not a real use case. You can put anything you want in the pages.

    .. code-block:: python

        pages = ["## Heat vs Lakers\nScore: 102–98", "## Celtics vs Nets\nScore: 110–105"]
        labels = ["Heat vs Lakers", "Celtics vs Nets"]
        view = SelectPaginator(pages, labels, ctx)
        view.message = await ctx.send(view=view)

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
    """

    def __init__(
        self,
        pages: list,
        labels: list[str],
        ctx,
        placeholder: str = "Choose a page...",
        timeout: int | None = 120,
    ) -> None:
        super().__init__(timeout=timeout)
        if not pages:
            raise ValueError("pages must not be empty")
        if len(pages) != len(labels):
            raise ValueError("pages and labels must be the same length")
        self.pages = pages
        self.current = 0
        self.message = None
        self.author = ctx.author
        self.placeholder = placeholder
        self._options = [
            discord.SelectOption(label=label[:100], value=str(i))
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
                _SelectPaginatorSelect(self, self._options, disabled=disabled)
            ),
        ))

    async def on_timeout(self) -> None:
        self._build_content(disabled=True)
        if self.message:
            with contextlib.suppress(discord.HTTPException):
                await self.message.edit(view=self)
