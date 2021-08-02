# -*- coding: utf-8 -*-

"""Top-level package for sofar."""

__author__ = """The pyfar developers"""
__email__ = 'info@pyfar.org'
__version__ = '0.1.0'


from .sofar import (update_conventions, list_conventions, get_convention,
    set_value)


__all__ = [
    'update_conventions',
    'list_conventions',
    'get_convention',
    'set_value']
