"""
This tests for consistent dimensions in the convention files.

All dimensions must be of the same length. E.g., the set of dimensions 'M, ME'
is invalud and should be 'MI, 'ME'.

This cannot be done as part of Sofa.verify, because it would make it impossible
to read SOFA files written with deprecated conventions that are containing
inconsistent dimensions.
"""
import sofar as sf
import numpy as np
import pytest
import json

convention_paths = sf.utils._get_conventions('path')


def check_dimensions_consistency(convention_path):
    """
    Check for consistent dimensions.

    Parameters
    ----------
    convention_path : str
        path to the SOFA convention to be checked. Must be a json file.

    Raises
    ------
    ValueError if one or more inconsistent dimensions are found.
    """

    with open(convention_path, "r") as file:
        convention = json.load(file)

    name = convention['GLOBAL:SOFAConventions']['default'] + ' v' + \
        convention['GLOBAL:SOFAConventionsVersion']['default']

    errors = []

    for key, value in convention.items():

        dimensions = value['dimensions']

        if dimensions is None:
            continue

        dim_length = [len(dim) for dim in dimensions.split(", ")]
        if len(np.unique(dim_length))  > 1:

            # get verbose string for error message containing the number of
            # dimensions and the actual dimensions, e.g., 2 (MR), 3 (MRE)
            dim_length_string = []
            for length, dim in zip(dim_length, dimensions.split(", ")):
                dim_length_string.append(f'{length} ({dim})')

            errors.append(f'{key}: {", ".join(dim_length_string)}')

    # raise error at the end in case there are multiple inconsistencies
    if len(errors):
        raise ValueError((f'Found dimensions of unequal length for {name}: '
                          f'{"; ".join(errors)}'))


@pytest.mark.parametrize('convention_path', convention_paths)
def test_dimensions_consistency(convention_path):
    """
    Check up to date conventions and skip deprecated.
    This must not raise errors.
    """

    if 'deprecated' in convention_path:
        return 0

    check_dimensions_consistency(convention_path)


def test_dimensions_consistency_error():
    """Check selected deprecated convention. This must raise and error."""

    for convention_path in convention_paths:
        if convention_path.endswith('FreeFieldDirectivityTF_1.0.json'):
            break

    with pytest.raises(ValueError, match='Found dimensions of unequal length'):
        check_dimensions_consistency(convention_path)
