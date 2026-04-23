"""
dcv2nav - Discord Components v2 navigation views for Red-DiscordBot cogs.

Provides drop-in paginator views compatible with discord.py 2.x LayoutView.
"""

from .paginator import LayoutViewPaginator
from .select_paginator import SelectPaginator

__all__ = ["LayoutViewPaginator", "SelectPaginator"]
__version__ = "1.0.0"
__author__ = "ltzmax"
