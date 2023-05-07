import os
import sys
import json
sys.path.insert(0, os.path.abspath(os.path.join('..', '..')))

import sofar as sf  # noqa

base_dir = os.path.dirname(__file__)

# get convention paths, names, and version ------------------------------------
paths = sf.utils._get_conventions('path')
names_versions = sf.utils._get_conventions('name_version')

upgrade_rules = os.path.join(
    base_dir, '..', '..', 'sofar', 'sofa_conventions', 'rules', 'upgrade.json')
with open(upgrade_rules, "r") as file:
    upgrade_rules = json.load(file)

# write general information ---------------------------------------------------
docs = (
    '.. _conventions_introduction:\n\n'
    'Introduction\n============\n\n'
    'SOFA conventions specify what data and metadata must be stored in a SOFA '
    'file. Different conventions can be used to store different types of data,'
    'e.g., head-related impulse responses or musical instrument directivities.'
    'It is advised to always use the conventions that is most specific for the'
    'data.\n\n'
    'In the following, SOFA conventions are described in tables with the '
    'information\n\n'
    '* **Name:** The Name of the data. The prefix *GLOBAL* denotes global '
    'attribute, i.e., attributes that pertain the entire data set. Underscores'
    ' denote attributes that are data specific. E.g., *SourcePosition_Units* '
    'denotes the *Units* of the data *SourcePosition*.\n'
    '* **Type:** The Type of the data.\n\n'
    '  * **Attribute:** A verbose description given by a string\n'
    '  * **Double:** A numeric array of data\n'
    '  * **String:** A string array of data\n\n'
    '* **Default:** The default value\n'
    '* **Dimensions:** The dimensions of the data. Lower case letters denote '
    'the data that sets the dimension.\n\n'
    '  * **E:** Number of emitters\n'
    '  * **R:** Number of receivers\n'
    '  * **M:** Number of measurements\n'
    '  * **N:** Number of samples or frequency bins of the data\n'
    '  * **C:** Number of coordinates (always 3)\n'
    '  * **I:** Unity dimentions (always 1)\n'
    '  * **S:** Lengths of the longest string contained in the data '
    '(detected automatically)\n\n'
    '* **Flags:**\n\n'
    '  * **r:** read only data. Data can be written if flag is missing.\n'
    '  * **m:** mandatory data. Data is optional if flag is missing\n\n')

# write table of content ------------------------------------------------------
docs += '.. _conventions:\n\nConventions\n===========\n\n'
for path, name_version in zip(paths, names_versions):
    name, version = name_version

    label = f'{name} v{version}'
    if 'deprecated' in path:
        label += ' (deprecated)'
    reference = f'{name}_v{version}'

    docs += f'* :ref:`{label} <{reference}>`\n'

# write conventions -----------------------------------------------------------
docs += '\nCurrent\n=======\n\n'

# loop conventions
deprecated = False
for path, name_version in zip(paths, names_versions):
    name, version = name_version

    # read convention from json file
    with open(path, 'r') as file:
        convention = json.load(file)

    # write section title
    if 'deprecated' in path and not deprecated:
        docs += 'Deprecated\n==========\n\n'
        deprecated = True

    # write convention name, version
    docs += f'.. _{name}_v{version}:\n\n'
    docs += f'**{name} v{version}**\n\n'

    # name new convention if current convention is deprecated
    if deprecated:
        if name not in upgrade_rules:
            upgrade_to = None
        for upgrade in upgrade_rules[name]['from_to']:
            if version in upgrade[0]:
                upgrade_to = upgrade[1]
                docs += ('This convention is deprecated. '
                         f'Use **{", ".join(upgrade_to)}** instead.\n\n')

    # name purpose of the convention
    docs += f'{convention["GLOBAL:SOFAConventions"]["comment"]}\n\n'

    # write header
    docs += (
        '.. list-table::\n'
        '   :widths: 20 50 25 30 100\n'
        '   :header-rows: 1\n\n'
        '   * - Name (Type)\n'
        '     - Default\n'
        '     - Dim.\n'
        '     - Flags\n'
        '     - Comment\n')

    # loop entries
    for key, value in convention.items():

        if value["dimensions"] is None:
            dimensions = ""
        else:
            dimensions = value["dimensions"]

        if value["flags"] is None:
            flags = ""
        elif len(value["flags"]) > 1:
            flags = f'{value["flags"][0]}, {value["flags"][1]}'
        else:
            flags = value["flags"]

        if key == "GLOBAL:SOFAConventions":
            value["comment"] = ""

        if value["type"] == 'attribute':
            type_str = 'attr.'
        elif value["type"] == 'double':
            type_str = 'doub.'
        else:
            type_str = 'str.'

        docs += (
            f'   * - {key.replace(":", "_").replace(".", "_")} '
            f'(*{value["type"]}*)\n'
            f'     - {value["default"]}\n'
            f'     - {dimensions}\n'
            f'     - {flags}\n'
            f'     - {value["comment"]}\n')

    docs += '\n:ref:`back to top <conventions>`\n\n'

# write docs to rst file ------------------------------------------------------
docs_file = os.path.join(base_dir, 'conventions.rst')
with open(docs_file, 'w') as file:
    file.writelines(docs)
