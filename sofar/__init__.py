# -*- coding: utf-8 -*-

"""Top-level package for sofar."""

__author__ = """The pyfar developers"""
__email__ = 'info@pyfar.org'
__version__ = '0.1.0'


from .sofar import (update_conventions, list_conventions, create_sofa,
                    set_value, update_api, read_sofa, write_sofa,
                    info, compare_sofa)


__all__ = [
    'update_conventions',
    'list_conventions',
    'create_sofa',
    'set_value',
    'update_api',
    'read_sofa',
    'write_sofa',
    'info',
    'compare_sofa']
