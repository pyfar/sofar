import contextlib
import os
import re
import glob
import json
import requests
from bs4 import BeautifulSoup


def update_conventions(conventions_path=None, assume_yes=False):
    """
    Update SOFA conventions.

    SOFA convention define what data is stored in a SOFA file and how it is
    stored. Updating makes sure that sofar is using the latest conventions.
    This is done in three steps

    1.
        Download official SOFA conventions as csv files from
        https://www.sofaconventions.org/conventions/ and
        https://www.sofaconventions.org/conventions/deprecated/.
    2.
        Convert csv files to json files to be read by sofar.
    3.
        Notify which conventions were newly added or updated.

    The csv and json files are stored at sofar/conventions. Sofar works only on
    the json files. To get a list of all currently available SOFA conventions
    and their paths see :py:func:`~sofar.list_conventions`.

    .. note::
        If the official convention contain errors, calling this function might
        break sofar. If this is the case sofar must be re-installed, e.g., by
        running ``pip install --force-reinstall sofar``. Be sure that you want
        to do this.

    Parameters
    ----------
    conventions_path : str, optional
        Path to the folder where the conventions are saved. The default is
        ``None``, which saves the conventions inside the sofar package.
        Conventions saved under a different path can not be used by sofar. This
        parameter was added mostly for testing and debugging.
    response : bool, optional

        ``True``
            Updating the conventions must be confirmed by typing "y".
        ``False``
            The conventions are updated without confirmation.

        The default is ``True``
    """

    if not assume_yes:
        # these lines were only tested manually. I was too lazy to write a test
        # coping with keyboard input
        print(("Are you sure that you want to update the conventions? "
               "Read the documentation before continuing. "
               "If updateing breaks sofar it has to be re-installed"
               "(y/n)"))
        response = input()
        if response != "y":
            print("Updating the conventions was canceled.")
            return

    # url for parsing and downloading the convention files
    urls = ("https://www.sofaconventions.org/conventions/",
            "https://www.sofaconventions.org/conventions/deprecated/")
    ext = 'csv'

    print(f"Reading SOFA conventions from {urls[0]} ...")

    # get file names of conventions from sofaconventions.org
    page = requests.get(urls[0]).text
    soup = BeautifulSoup(page, 'html.parser')
    standardized = [os.path.split(node.get('href'))[1]
                    for node in soup.find_all('a')
                    if node.get('href').endswith(ext)]
    page = requests.get(urls[1]).text
    soup = BeautifulSoup(page, 'html.parser')
    deprecated = [os.path.split(node.get('href'))[1]
                  for node in soup.find_all('a')
                  if node.get('href').endswith(ext)]

    conventions = standardized + deprecated

    # directory handling
    if conventions_path is None:
        conventions_path = os.path.join(
            os.path.dirname(__file__), "sofa_conventions", "conventions")
    if not os.path.isdir(conventions_path):
        os.mkdir(conventions_path)
    if not os.path.isdir(os.path.join(conventions_path, "deprecated")):
        os.mkdir(os.path.join(conventions_path, "deprecated"))

    # Loop and download conventions if they changed
    updated = False
    for convention in conventions:

        # exclude these conventions
        if convention.startswith(("General_", "GeneralString_")):
            continue

        # get filename and url
        is_standardized = convention in standardized
        standardized_csv = os.path.join(conventions_path, convention)
        deprecated_csv = os.path.join(
                conventions_path, "deprecated", convention)
        url = (
            f"{urls[0]}/{convention}"
            if is_standardized
            else f"{urls[1]}/{convention}"
        )

        # download SOFA convention definitions to package directory
        data = requests.get(url)
        # remove windows style line breaks and trailing tabs
        data = data.content.replace(b"\r\n", b"\n").replace(b"\t\n", b"\n")

        # check if convention needs to be added or updated
        if is_standardized and not os.path.isfile(standardized_csv):
            # add new standardized convention
            updated = True
            with open(standardized_csv, "wb") as file:
                file.write(data)
            print(f"- added convention: {convention[:-4]}")
        if is_standardized and os.path.isfile(standardized_csv):
            # check for update of a standardized convention
            with open(standardized_csv, "rb") as file:
                data_current = b"".join(file.readlines())
                data_current = data_current.replace(
                    b"\r\n", b"\n").replace(b"\t\n", b"\n")
            if data_current != data:
                updated = True
                with open(standardized_csv, "wb") as file:
                    file.write(data)
                print(f"- updated convention: {convention[:-4]}")
        elif not is_standardized and os.path.isfile(standardized_csv):
            # deprecate standardized convention
            updated = True
            with open(deprecated_csv, "wb") as file:
                file.write(data)
            os.remove(standardized_csv)
            os.remove(f"{standardized_csv[:-3]}json")
            print(f"- deprecated convention: {convention[:-4]}")
        elif not is_standardized and os.path.isfile(deprecated_csv):
            # check for update of a deprecated convention
            with open(deprecated_csv, "rb") as file:
                data_current = b"".join(file.readlines())
                data_current = data_current.replace(
                    b"\r\n", b"\n").replace(b"\t\n", b"\n")
            if data_current != data:
                updated = True
                with open(deprecated_csv, "wb") as file:
                    file.write(data)
                print(f"- updated deprecated convention: {convention[:-4]}")
        elif not is_standardized and not os.path.isfile(deprecated_csv):
            # add new deprecation
            updated = True
            with open(deprecated_csv, "wb") as file:
                file.write(data)
            print(f"- added deprecated convention: {convention[:-4]}")

    if updated:
        # compile json files from csv file
        _compile_conventions(conventions_path)
        print("... done.")
    else:
        print("... conventions already up to date.")


def _compile_conventions(conventions_path=None):
    """
    Compile SOFA conventions (json files) from source conventions (csv files
    from SOFA SOFAtoolbox), i.e., only do step 2 from `update_conventions`.
    This is a helper function for debugging and developing and might break
    sofar.

    Parameters
    ----------
    conventions_path : str
        Path to the `conventions`folder containing csv and json files. The
        default ``None`` uses the default location inside the sofar package.
    """
    # directory handling
    if conventions_path is None:
        conventions_path = os.path.join(
            os.path.dirname(__file__), "sofa_conventions", "conventions")
    if not os.path.isdir(conventions_path):
        raise ValueError(f"{conventions_path} does not exist")

    # get list of source conventions
    csv_files = glob.glob(os.path.join(conventions_path, "*.csv")) + \
        glob.glob(os.path.join(conventions_path, "deprecated", "*.csv"))

    for csv_file in csv_files:

        # convert SOFA conventions from csv to json
        convention_dict = _convention_csv2dict(csv_file)
        with open(f"{csv_file[:-3]}json", 'w') as file:
            json.dump(convention_dict, file, indent=4)


def _convention_csv2dict(file: str):
    """
    Read a SOFA convention as csv file from the official Matlab/Octave API for
    SOFA (SOFAtoolbox) and convert them to a Python dictionary. The dictionary
    can be written for example to a json file using

    import json

    with open(filename, 'w') as file:
        json.dump(dictionary, file, indent=4)

    Parameters
    ----------
    file : str
        filename of the SOFA convention

    Returns
    -------
    convention : dict
        SOFA convention as nested dictionary. Each attribute is a sub
        dictionary with the keys `default`, `flags`, `dimensions`, `type`, and
        `comment`.
    """

    # read the file
    # (encoding should be changed to utf-8 after the SOFA conventions repo is
    # clean.)
    # TODO: add explicit test for this function that checks the output
    with open(file, 'r', encoding="windows-1252") as fid:
        lines = fid.readlines()

    # write into dict
    convention = {}
    for idl, line in enumerate(lines):

        try:
            # separate by tabs
            line = line.strip().split("\t")
            # parse the line entry by entry
            for idc, cell in enumerate(line):
                # detect empty cells and leading trailing white spaces
                cell = None if cell.replace(' ', '') == '' else cell.strip()
                # nothing to do for empty cells
                if cell is None:
                    line[idc] = cell
                    continue
                # parse text cells that do not contain arrays
                if cell[0] != '[':
                    # check for numbers
                    with contextlib.suppress(ValueError):
                        cell = float(cell) if '.' in cell else int(cell)
                    line[idc] = cell
                    continue

                # parse array cell
                # remove brackets
                cell = cell[1:-1]

                if ';' not in cell:
                    # get rid of white spaces
                    cell = cell.strip()
                    cell = cell.replace(' ', ',')
                    cell = cell.replace(' ', '')
                    # create flat list of integers and floats
                    numbers = cell.split(',')
                    cell = [float(n) if '.' in n else int(n) for n in numbers]
                else:
                    # create a nested list of integers and floats
                    # separate multidimensional arrays
                    cell = cell.split(';')
                    cell_nd = [None] * len(cell)
                    for idx, cc in enumerate(cell):
                        # get rid of white spaces
                        cc = cc.strip()
                        cc = cc.replace(' ', ',')
                        cc = cc.replace(' ', '')
                        numbers = cc.split(',')
                        cell_nd[idx] = [float(n) if '.' in n else int(n)
                                        for n in numbers]

                    cell = cell_nd

                # write parsed cell to line
                line[idc] = cell

            # first line contains field names
            if idl == 0:
                fields = line[1:]
                continue

            # add blank comment if it does not exist
            if len(line) == 5:
                line.append("")
            # convert empty defaults from None to ""
            if line[1] is None:
                line[1] = ""

            # make sure some unusual default values are converted for json
            if line[1] == "permute([0 0 0 1 0 0; 0 0 0 1 0 0], [3 1 2]);":
                # Field Data.SOS in SimpleFreeFieldHRSOS and SimpleFreeFieldSOS
                line[1] = [[[0, 0, 0, 1, 0, 0], [0, 0, 0, 1, 0, 0]]]
            if line[1] == "permute([0 0 0 1 0 0], [3 1 2]);":
                # Field Data.SOS in GeneralSOS
                line[1] = [[[0, 0, 0, 1, 0, 0]]]
            if line[1] == "{''}":
                line[1] = ['']
            # convert versions to strings
            if "Version" in line[0] and not isinstance(line[1], str):
                line[1] = str(float(line[1]))

            # write second to last line
            convention[line[0]] = {}
            for ff, field in enumerate(fields):
                convention[line[0]][field.lower()] = line[ff + 1]

        except: # noqa
            raise ValueError((f"Failed to parse line {idl}, entry {idc} in: "
                              f"{file}: \n{line}\n"))

    # reorder the fields to be nicer to read and understand
    # 1. Move everything to the end that is not GLOBAL
    keys = list(convention.keys())
    for key in keys:
        if "GLOBAL" not in key:
            convention[key] = convention.pop(key)
    # 1. Move Data entries to the end
    for key in keys:
        if key.startswith("Data"):
            convention[key] = convention.pop(key)

    return convention


def _check_congruency(save_dir=None, branch="master"):
    """
    SOFA conventions are stored in two different places - is this a good idea?
    They should be identical, but let's find out.

    Prints warnings about incongruent conventions

    Parameters
    ----------
    save : str
        directory to save diverging conventions for further inspections
    """

    # urls for checking which conventions exist
    urls_check = ["https://www.sofaconventions.org/conventions/",
                  ("https://github.com/sofacoustics/SOFAtoolbox/tree/"
                   f"{branch}/SOFAtoolbox/conventions/")]
    # urls for loading the convention files
    urls_load = ["https://www.sofaconventions.org/conventions/",
                 ("https://raw.githubusercontent.com/sofacoustics/SOFAtoolbox/"
                  f"{branch}/SOFAtoolbox/conventions/")]
    subdirs = ["sofaconventions", "sofatoolbox"]

    # check save_dir
    if save_dir is not None:
        if not os.path.isdir(save_dir):
            raise ValueError(f"{save_dir} does not exist")
        for subdir in subdirs:
            if not os.path.isdir(os.path.join(save_dir, subdir)):
                os.makedirs(os.path.join(save_dir, subdir))

    # get file names of conventions from sofaconventions.org
    url = urls_check[0]
    page = requests.get(url).text
    soup = BeautifulSoup(page, 'html.parser')
    sofaconventions = [os.path.split(node.get('href'))[1]
                       for node in soup.find_all('a')
                       if node.get('href').endswith(".csv")]

    if not sofaconventions:
        raise ValueError(f"Did not find any conventions at {url}")

    # get file names of conventions from github
    url = urls_check[1]
    page = requests.get(url).text
    sofatoolbox = re.findall(
        r'"SOFAtoolbox/conventions/([^"]+\.csv)"', page)

    if not sofatoolbox:
        raise ValueError(f"Did not find any conventions at {url}")

    # check if lists are identical. Remove items not contained in both lists
    report = ""
    for convention in sofaconventions:
        if convention.startswith(("General_", "GeneralString_")):
            sofaconventions.remove(convention)
        elif convention not in sofatoolbox:
            sofaconventions.remove(convention)
            report += (f"- {convention} is missing in SOFAtoolbox\n")
    for convention in sofatoolbox:
        if convention.startswith(("General_", "GeneralString_")):
            sofatoolbox.remove(convention)
        elif convention not in sofaconventions:
            sofatoolbox.remove(convention)
            report += (f"- {convention} is missing on sofaconventions.org\n")

    # Loop and download conventions to check if they are identical
    for convention in sofaconventions:

        # download SOFA convention definitions to package directory
        data = [requests.get(url + convention) for url in urls_load]
        # remove trailing tabs and windows style line breaks
        data = [d.content.replace(b"\r\n", b"\n").replace(b"\t\n", b"\n")
                for d in data]

        # check for equality
        if data[0] != data[1]:
            report += f"- {convention} differs across platforms\n"

            # save diverging files
            if save_dir is not None:
                for subdir, d in zip(subdirs, data):
                    filename = os.path.join(save_dir, subdir, convention)
                    with open(filename, "wb") as file:
                        file.write(d)

    if report:
        print("Diverging conventions across platforms:\n" + report)
