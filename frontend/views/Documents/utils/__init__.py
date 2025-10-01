"""
Utilities Package for Document Management System

This package provides utility functions and classes for the document management interface.
"""

from .icon_utils import IconLoader, create_menu_button, create_search_button
from .role_utils import (
    RoleRouter,
    is_admin, 
    is_faculty,
    is_staff, 
    is_student, 
    has_sub_role
)

__all__ = [
    'IconLoader',
    'create_menu_button',
    'create_search_button',
    'RoleRouter',
    'is_admin',
    'is_faculty',
    'is_staff',
    'is_student',
    'has_sub_role'
]
