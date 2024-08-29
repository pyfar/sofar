# -*- coding: utf-8 -*-
__author__ = """The pyfar developers"""
__email__ = 'info@pyfar.org'
__version__ = '1.2.0'

from .sofa import Sofa

from .sofastream import SofaStream

from .io import read_sofa, read_sofa_as_netcdf, write_sofa

from .utils import (list_conventions,
                    equals,
                    version)

from .update_conventions import update_conventions


__all__ = ['Sofa',
           'SofaStream',
           'update_conventions',
           'list_conventions',
           'read_sofa',
           'read_sofa_as_netcdf',
           'write_sofa',
           'equals',
           'version']
