# -*- coding: utf-8 -*-
"""
State management package.

Provides global state management and validation utilities.
"""

from .store import StateManager, init_state, get_state

__all__ = ['StateManager', 'init_state', 'get_state']
