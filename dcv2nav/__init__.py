"""
dcv2nav - Discord Components v2 navigation views for Red-DiscordBot cogs.

Provides drop-in paginator views compatible with discord.py 2.x LayoutView.
"""

from .paginator import LayoutViewPaginator, _NavBtn
from .select_paginator import SelectPaginator, _SelectPaginatorSelect

__all__ = ["LayoutViewPaginator", "SelectPaginator", "_NavBtn", "_SelectPaginatorSelect"]
__version__ = "1.2.1"
__author__ = "ltzmax"
