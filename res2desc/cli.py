"""
Module containing the commandline interface
"""
# pylint: disable=too-many-locals,import-outside-toplevel, too-many-arguments
import io
import subprocess

import pandas as pd
from ase.io.xyz import write_xyz
import numpy as np
import click

from res2desc import Atoms2Soap
from res2desc.res import read_stream


def cryan_out_adaptor(output, titl_list, desc_list, cryan_style):
    """Adapt the computed descriptors to the cryan style"""
    nelem = desc_list.shape[1]
    if cryan_style == '2':
        for titl, desc in zip(titl_list, desc_list):
            output.write(f'{nelem:d}\t')
            np.savetxt(output, desc, newline='\t', fmt='%0.6G')
            output.write('\n')
            output.write(titl)
    elif cryan_style == '1':
        for titl, desc in zip(titl_list, desc_list):
            output.write(f'{nelem:d}\n')
            np.savetxt(output, desc, newline='\t', fmt='%0.6G')
            output.write('\n')
            output.write(titl)
    else:
        raise RuntimeError(f'Unknown cryan style {cryan_style}')


def process_titl_list(titl_list, atoms_list):
    """Process the titl_list"""
    out_list = []
    for titl, atom in zip(titl_list, atoms_list):
        out_list.append('\t'.join([
            titl.label,
            str(titl.natoms),
            atom.get_chemical_formula(mode='hill', empirical=True),
            titl.symm.replace('(', "\"").replace(')', "\""),
            str(titl.volume),
            str(titl.enthalpy),
            titl.flag3,  # Number of times found
        ]) + '\n')
    return out_list


@click.group('res2desc',
             help='Commandline tool for converting SHELX files to descriptors')
@click.option(
    '--input_source',
    '-in',
    type=click.File('r'),
    default='-',
    show_default='STDIN',
)
@click.option('--output',
              '-out',
              type=click.File('w'),
              default='-',
              show_default='STDOUT')
@click.option('--cryan/--no-cryan',
              default=True,
              show_default=True,
              help=('Call cryan internally to obtain fully compatible output. '
                    'Should be disabled if cryan is not avaliable.'))
@click.option(
    '--cryan-style-in',
    help=
    'Style of the cryan input, 1 for 3 lines for structure, 2 for 2 lines per structure. Automatically fallback to 1 if 2 does not work.',
    default='2',
    type=click.Choice(['1', '2']),
    show_default=True,
)
@click.option(
    '--cryan-style-out',
    help=
    'Style of the cryan output, 1 for 3 lines for structure, 2 for 2 lines per structure. Default to 3 lines for compatibility with SHEAP',
    default='1',
    type=click.Choice(['1', '2']),
    show_default=True,
)
@click.option(
    '--cryan-args',
    type=str,
    default='-v -dr 0',
    show_default=True,
    help=
    'A string of the arges that should be passed to cryan, as if in the shell')
@click.pass_context
def cli(ctx, input_source, output, cryan, cryan_args, cryan_style_in,
        cryan_style_out):
    """
    Top level command, handles input_source and output streams
    """
    ctx.ensure_object(dict)
    ctx.obj['output'] = output
    # Check if using cryan compatible mode
    if cryan is True:
        # Read all input_source in a buffer
        if input_source.name == '<stdin>':
            if input_source.isatty():
                # nothing in stdin
                titl_lines = []
                titl_list = []
                atoms_list = []
                inp = None
            else:
                # Reading from stdin
                inp, titl_lines, titl_list, atoms_list = read_with_cryan(
                    input_source, cryan_args, cryan_style_in)

        else:
            # Reading from file
            inp, titl_lines, titl_list, atoms_list = read_with_cryan(
                input_source, cryan_args, cryan_style_in)
    # Reset the input stream
        ctx.obj['input_source'] = inp
        ctx.obj['titl_lines'] = titl_lines
    else:
        ctx.obj['input_source'] = input_source
        ctx.obj['titl_lines'] = None
        titl_list, atoms_list = read_stream(input_source)

    ctx.obj['titl_list'] = titl_list
    ctx.obj['atoms_list'] = atoms_list
    ctx.obj['cryan_style_out'] = cryan_style_out


def read_with_cryan(input_source, cryan_args, cryan_style):
    """Read stuff with cryan from a source
    :param input_source: file object to be read.
    :returns: a list of [inp, titl_lines, titl_list, atoms_list]"""
    inp = io.StringIO()
    inp.write(input_source.read())
    # We are getting piped inputs
    inp.seek(0)
    cryan_args = cryan_args.split()
    subp = subprocess.Popen(['cryan', *cryan_args],
                            stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE,
                            text=True)
    ops, _ = subp.communicate(inp.read())
    inp.seek(0)
    if cryan_style not in ('1', '2'):
        raise RuntimeError(f'Unkown cryan style: {cryan_style}')
    # First try style == 2, this is the standard cryan
    if cryan_style == '2':
        titl_lines = ops.splitlines(keepends=True)[1::2]
        # If it does not work, we try style == 1, this is the
        # style Ben describe with 3 lines per structure
        if len(titl_lines[0].split()) != 7:
            cryan_style = '1'
    if cryan_style == '1':
        titl_lines = ops.splitlines(keepends=True)[2::3]
    # Check titl again
    if len(titl_lines[0].split()) != 7:
        raise RuntimeError('Ill formated cryan input detected. Terminating.')
    titl_list, atoms_list = read_stream(inp)
    # Reset the buffer
    inp.seek(0)
    return inp, titl_lines, titl_list, atoms_list


# pylint: disable=too-many-arguments
@cli.command('soap', help='Compute SOAP descriptors')
@click.option('--nprocs',
              '-np',
              help='Number of processes for parallelisation.',
              default=1)
@click.option('--l-max', default=4, show_default=True)
@click.option('--n-max', default=8, show_default=True)
@click.option('--cutoff', default=5, show_default=True)
@click.option('--atom-sigma', default=0.1, show_default=True)
@click.option('--crossover/--no-crossover',
              default=True,
              show_default=True,
              help='Whether do the crossover for multiple species')
@click.option('--species-names',
              '-sn',
              required=False,
              type=str,
              help='Symbols of all species to be considered, should be a list')
@click.option(
    '--centres-name',
    '-cn',
    required=False,
    type=str,
    multiple=True,
    help=
    'Centres where the descriptor should be computed. If not specified, defaults to all atomic sites. NOT IMPLEMENTED FOR NOW'
)
@click.option(
    '--average/--no-average',
    default=True,
    show_default=True,
    help=
    'Averaging descriptors for each structrure, rather than output those for individual sites.'
)
@click.option('--periodic/--no-periodic',
              default=True,
              show_default=True,
              help='Whether assuming periodic boundary conditions or not')
@click.pass_context
#  # pylint: disable=unused-argument
def cmd_soap(ctx, cutoff, l_max, n_max, atom_sigma, nprocs, centres_name,
             species_names, average, periodic, crossover):
    """
    Compute SOAP descriptors for res files, get the order or files from
    the `ca -v` commands for consistency.
    """
    titl_list, atoms_list = ctx.obj['titl_list'], ctx.obj['atoms_list']
    cryan_style = ctx.obj['cryan_style_out']
    if not species_names:
        species_names = set()
        for atoms in atoms_list:
            _ = [species_names.add(x) for x in atoms.get_chemical_symbols()]
    else:
        species_names = species_names.split()

    desc_settings = {
        'rcut': cutoff,
        'lmax': l_max,
        'nmax': n_max,
        'sigma': atom_sigma,
        'average': average,
        'species': species_names,
        'periodic': periodic,
        'crossover': crossover,
    }
    comp = Atoms2Soap(desc_settings)

    descs = comp.get_desc(atoms_list, nprocs)
    output = ctx.obj['output']
    # Process the tilt_lines
    titl_lines = ctx.obj.get('titl_lines')
    if titl_lines is None:
        # Not read from cryan, contruct these lines here
        titl_lines = process_titl_list(titl_list, atoms_list)
    cryan_out_adaptor(output, titl_lines, descs, cryan_style)


@cli.command('xyz', help='Create concatenated xyz files')
@click.option(
    '--label-file',
    help=
    'Filename for writing out the labels. CSV will be use if the file name has the right suffix.'
)
@click.pass_context
def cmd_xyz(ctx, label_file):
    """
    Commandline tool for creating a concatenated xyz files from res
    also, the labels for each strucure is saved
    """
    titl_list, atoms_list = ctx.obj['titl_list'], ctx.obj['atoms_list']
    output = ctx.obj['output']
    # Setup info for atoms
    for atoms, titl in zip(atoms_list, titl_list):
        atoms.info['label'] = titl.label
        atoms.info['enthalpy'] = titl.enthalpy
        atoms.info['pressure'] = titl.pressure
        atoms.info['symmetry'] = titl.symm

    # Write the xyz files
    write_xyz(output, atoms_list)

    # Write the label file
    from tabulate import tabulate
    if label_file:
        data = [[
            'label', 'natoms', 'enthalpy', 'volume', 'pressure', 'symmetry'
        ]]
        for titl in titl_list:
            data.append([
                titl.label, titl.natoms, titl.enthalpy / titl.natoms,
                titl.volume / titl.natoms, titl.pressure, titl.symm
            ])

        if label_file.endswith('.csv'):
            dataframe = pd.DataFrame(data[1:], columns=data[0])
            dataframe.to_csv(label_file, index=False)
        else:
            content = tabulate(data, headers='firstrow', tablefmt='plain')

            with open(label_file, 'w') as fhandle:
                fhandle.write('#')
                fhandle.write(content)


def shorten_titl(str_in, nout=5):
    """Shorten the title with *, so it can still be matched by
    glob"""
    if len(str_in) > nout * 2:
        str_out = str_in[:5] + '*' + str_in[-5:]
    else:
        str_out = str_in
    return str_out
