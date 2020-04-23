"""
Module containing the commandline interface
"""
import io
import subprocess

import numpy as np
import click

from res2desc import Atoms2Soap
from res2desc.res import read_stream


def cryan_out_adaptor(output, titl_list, desc_list):
    """Adapt the computed descriptors to the cryan style"""
    for titl, desc in zip(titl_list, desc_list):
        np.savetxt(output, desc, newline='\t', fmt='%0.6G')
        output.write('\n')
        output.write(titl)


def process_titl_list(titl_list, atoms_list):
    """Process the titl_list"""
    out_list = []
    for titl, atom in zip(titl_list, atoms_list):
        out_list.append('\t'.join([
            titl[0], titl[6],
            atom.get_chemical_formula(mode='hill', empirical=True),
            titl[7].replace('(', "\"").replace(')', "\""), titl[-1]
        ]) + '\n')
    return out_list


@click.group('res2desc',
             help='Commandline tool for converting SHELX files to descriptors')
@click.option('--input-source', type=click.File('r'), default='-')
@click.option('--output', type=click.File('w'), default='-')
@click.option('--cryan/--no-cryan', default=True)
@click.option(
    '--cryan-args',
    type=str,
    default='-v -dr 0',
    help=
    'A string of the arges that should be passed to cryan, as if in the shell')
@click.pass_context
def cli(ctx, input_source, output, cryan, cryan_args):
    """
    Top level command, handles input_source and output streams
    """
    ctx.ensure_object(dict)
    ctx.obj['output'] = output
    # Check if using cryan compatible mode
    if cryan is True:
        # Read all input_source in a buffer
        inp = io.StringIO()
        inp.write(input_source.read())
        inp.seek(0)
        cryan_args = cryan_args.split()
        subp = subprocess.Popen(['cryan', *cryan_args],
                                stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE,
                                text=True)
        ops, _ = subp.communicate(inp.read())
        titl_lines = ops.split('\n')[1::2]
        inp.seek(0)
        ctx.obj['input_source'] = inp
        ctx.obj['titl_lines'] = titl_lines
    else:
        ctx.obj['input_source'] = input_source
        ctx.obj['titl_lines'] = None


# pylint: disable=too-many-arguments
@cli.command('soap', help='Compute SOAP descriptors')
@click.option('--nprocs',
              '-np',
              help='Number of processes for parallelisation.',
              default=1)
@click.option('--l-max', default=4)
@click.option('--n-max', default=8)
@click.option('--cutoff', default=5)
@click.option('--atom-sigma', default=0.01)
@click.option('--crossover/--no-crossover',
              default=True,
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
    'Centres where the descriptor should be computed. If not specified, defaults to all atomic sites'
)
@click.option(
    '--average/--no-average',
    default=True,
    help=
    'Averaging descriptors for each structrure, rather than output those for individual sites.'
)
@click.option('--periodic/--no-periodic',
              default=True,
              help='Whether assuming periodic boundary conditions or not')
@click.pass_context
#  # pylint: disable=unused-argument
def cmd_soap(ctx, cutoff, l_max, n_max, atom_sigma, nprocs, centres_name,
             species_names, average, periodic, crossover):
    """
    Compute SOAP descriptors for res files, get the order or files from
    the `ca -v` commands for consistency.
    """
    click.echo('Reading res files', err=True)
    titl_list, atoms_list = read_stream(ctx.obj['input_source'])
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
    titl_lines = ctx.obj.get('title_lines')
    if titl_lines is None:
        titl_lines = process_titl_list(titl_list, atoms_list)
    cryan_out_adaptor(output, titl_lines, descs)
