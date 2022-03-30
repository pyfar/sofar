# -*- coding: utf-8 -*-

"""Top-level package for sofar."""

__author__ = """The pyfar developers"""
__email__ = 'info@pyfar.org'
__version__ = '0.3.1'

from .sofa import Sofa

from .io import (read_sofa, write_sofa)

from .utils import (update_conventions,
                    list_conventions,
                    equals)


__all__ = ['Sofa',
           'update_conventions',
           'list_conventions',
           'read_sofa',
           'write_sofa',
           'equals']
