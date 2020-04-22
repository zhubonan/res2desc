"""
Reader for SHELX file
The functions are adapted from ase.io.res module
"""
import re

from ase.geometry import cellpar_to_cell
from dscribe.core.system import System


def read_res(lines):
    """
    Reads a res file from a string

    Args:
        lines (str): A list of lines containing Res data.

    Returns:
        System object that is used internally by Dscribe
    """
    abc = []
    ang = []
    species = []
    coords = []
    info = dict()
    coord_patt = re.compile(
        r"""(\w+)\s+
                                ([0-9]+)\s+
                                ([0-9\-\.]+)\s+
                                ([0-9\-\.]+)\s+
                                ([0-9\-\.]+)\s+
                                ([0-9\-\.]+)""", re.VERBOSE)
    line_no = 0
    while line_no < len(lines):
        line = lines[line_no]
        tokens = line.split()
        if tokens:
            if tokens[0] == 'TITL':
                # Skip the TITLE line, the information is not used
                # in this package
                pass
            elif tokens[0] == 'CELL' and len(tokens) == 8:
                abc = [float(tok) for tok in tokens[2:5]]
                ang = [float(tok) for tok in tokens[5:8]]
            elif tokens[0] == 'SFAC':
                for atom_line in lines[line_no:]:
                    if line.strip() == 'END':
                        break
                    match = coord_patt.search(atom_line)
                    if match:
                        species.append(match.group(1))  # 1-indexed
                        xyz = match.groups()[2:5]
                        coords.append([float(c) for c in xyz])
                    line_no += 1  # Make sure the global is updated
        line_no += 1

    return System(symbols=species,
                  scaled_positions=coords,
                  cell=cellpar_to_cell(list(abc) + list(ang)),
                  pbc=True,
                  info=info)


def read_stream(stream):
    """
    Read from a stream of RES file contents, and resturn a
    list of System object
    """
    lines = []
    atoms_list = []
    in_file = False
    for line in stream:
        line = line.strip()
        # Skip any empty lines
        if not line:
            continue
        if 'TITL' in line:
            if in_file is True:
                # read the current file
                atoms_list.append(read_res(lines))
                lines = []
            in_file = True
        if in_file:
            lines.append(line.strip())
    # Reached the end parse the last file
    atoms_list.append(read_res(lines))
    return atoms_list
