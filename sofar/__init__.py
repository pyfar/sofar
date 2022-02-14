# -*- coding: utf-8 -*-

"""Top-level package for sofar."""

__author__ = """The pyfar developers"""
__email__ = 'info@pyfar.org'
__version__ = '0.2.0'


from .sofar import (Sofa,
                    list_conventions,
                    read_sofa,
                    write_sofa,
                    equals)


__all__ = ['Sofa',
           'list_conventions',
           'read_sofa',
           'write_sofa',
           'equals']
