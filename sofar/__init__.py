# -*- coding: utf-8 -*-

"""Top-level package for sofar."""

__author__ = """The pyfar developers"""
__email__ = 'info@pyfar.org'
__version__ = '1.1.3'

from .sofa import Sofa

from .sofastream import Sofastream

from .io import read_sofa, read_sofa_as_netcdf, write_sofa

from .utils import (list_conventions,
                    equals,
                    version)

from .update_conventions import update_conventions


__all__ = ['Sofa',
           'Sofastream',
           'update_conventions',
           'list_conventions',
           'read_sofa',
           'read_sofa_as_netcdf',
           'write_sofa',
           'equals',
           'version']
