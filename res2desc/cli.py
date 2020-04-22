"""
Module containing the commandline interface
"""

import os
from subprocess import check_output

import click
from tqdm import tqdm

from ase.io import read
from res2desc import Atoms2Soap


def save_file(savename, desc_arrays, info):
    """
    Save the computed descriptor array
    """
    size = desc_arrays[0].size
    with open(savename, 'w') as fhandle:
        fhandle.write('{} {}\n'.format(len(desc_arrays), size))
        for desc in desc_arrays:
            fhandle.write(' '.join(map(str, desc[0])) + '\n')
        for line in info:
            fhandle.write(line + '\n')


def get_res_paths(workdir=None):
    """
    Get the paths of the res files
    """
    if workdir is None:
        workdir = './'
    output = check_output(['ca', '-r'], cwd=workdir).decode('utf-8').split(
        '\n')  # Run ca -v in shell and get outputs
    num_struct, _ = output[0].split()
    airss_info = output[int(num_struct) + 1:-1]
    fnames = [
        os.path.join(workdir,
                     l.split('\t')[0] + '.res') for l in airss_info
    ]
    return fnames, airss_info


# pylint: disable=too-many-arguments
@click.command(
    'res2soap',
    help=
    'Compute descriptors of the results uisng the QUIP package and output in a cryan format (e.g the same as ca -v)'
)
@click.argument('workdir')
@click.option('--nprocs',
              '-np',
              help='Number of processes for parallelisation.',
              default=4)
@click.option('--save-name', '-s', help='Save file name', default='soap_descs')
@click.option('--l-max', default=15)
@click.option('--n-max', default=15)
@click.option('--cutoff', default=5)
@click.option('--atom-sigma', default=0.01)
@click.option(
    '--centre-z',
    '-z',
    required=False,
    type=int,
    multiple=True,
    help=
    'Atomic numbers of the atoms that the local descriptor should be computed')
@click.option(
    '--species-z',
    '-sz',
    required=False,
    type=int,
    multiple=True,
    help='Atomic numbers of the enironment atoms that should be inlcuded')
def cmd_res2soap(cutoff, workdir, l_max, n_max, atom_sigma, nprocs, save_name,
                 centre_z, species_z):
    """
    Compute SOAP descriptors for res files, get the order or files from
    the `ca -v` commands for consistency.
    """
    desc_settings = {
        'rcut': cutoff,
        'lmax': l_max,
        'nmax': n_max,
        'sigma': atom_sigma,
        'average': True,
    }
    click.echo('Reading res files')
    fnames, airss_info = get_res_paths(workdir)
    atom_list = [[n, read(fn)] for n, fn in enumerate(tqdm(fnames))]

    comp = Atoms2Soap(desc_settings)
    descs = comp.get_desc(atom_list, nprocs)
    save_file(save_name, descs, airss_info)
