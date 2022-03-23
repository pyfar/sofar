# -*- coding: utf-8 -*-

"""Top-level package for sofar."""

__author__ = """The pyfar developers"""
__email__ = 'info@pyfar.org'
__version__ = '0.3.1'


from .sofar import (Sofa,
                    update_conventions,
                    list_conventions,
                    read_sofa,
                    write_sofa,
                    equals)


__all__ = ['Sofa',
           'update_conventions',
           'list_conventions',
           'read_sofa',
           'write_sofa',
           'equals']
