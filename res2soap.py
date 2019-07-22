#!/usr/bin/env python2

from ase.io import read
import quippy
from tqdm import tqdm
import os
from multiprocessing import Pool
from subprocess import check_output
import click

DESC_INIT = False


class Res2SOAP(object):
    def __init__(self, desc_dict):
        """
        """
        self.desc_settings = desc_dict

    @property
    def desc_string(self):
        settings = []
        for key, value in self.desc_settings.items():
            settings.append('{}={}'.format(key, value))
        return 'soap ' + ' '.join(settings)

    def init_desc(self):
        """Initialize the descriptor object"""
        self._desc = quippy.descriptors.Descriptor(self.desc_string)
        # Set the module level parameter for parallelisation
        global DESC_INIT
        DESC_INIT = True

    @property
    def desc(self):
        if not self._desc or DESC_INIT is False:
            self.init_desc()
        return self._desc

    def get_soap_desc(self, args):

        n, atoms = args
        if not isinstance(atoms, quippy.Atoms):
            atoms = quippy.Atoms(atoms)
        cut_off = int(self.desc_settings['cutoff']) + 1
        atoms.set_cutoff(cut_off)
        atoms.calc_connect()
        return n, self.desc.calc(atoms)['descriptor']


def save_file(savename, desc_arrays, info):
    size = desc_arrays[0].size
    with open(savename, 'w') as fh:
        fh.write('{} {}\n'.format(len(desc_arrays), size))
        for desc in desc_arrays:
            fh.write(' '.join(map(str, desc[0])) + '\n')
        for line in info:
            fh.write(line + '\n')


def get_res_paths(workdir=None):
    if workdir is None:
        workdir = './'
    output = check_output(['ca', '-v'], cwd=workdir).split(
        '\n')  # Run ca -v in shell and get outputs
    num_struct, _ = output[0].split()
    airss_info = output[int(num_struct) + 1:-1]
    fnames = [
        os.path.join(workdir,
                     l.split('\t')[0] + '.res') for l in airss_info
    ]
    return fnames, airss_info


@click.command('res2soap')
@click.argument('--workdir')
@click.option('--nprocs', '-np', help='Number of processes for parallelisation.', defualt=4)
@click.option('--save-name', '-s', help='Save file name', default='soap_desc.xyz')
@click.option('--l-max', default=15)
@click.option('--n-max', default=15)
@click.option('--atoms-sigma', default=0.01)
@click.option('--n-species', default=1)
@click.option('--Z', '-z', required=True, type=int)
@click.option('--species_Z', '-sz', required=True, type=int, mutiple=True)
def main(cutoff, workdir, l_max, n_max, atoms_sigma, n_species, Z,
         nprocs, save_name, species_Z):
    """
    Compute SOAP descriptors for res files, get the order or files from
    the `ca -v` commands for consistency.
    """
    desc_settings = {
        'cutoff': cutoff,
        'l_max': l_max,
        'n_max': n_max,
        'atoms_sigma': atoms_sigma,
        'average': 'T',
        'n_species': n_species,
        'Z': Z,
        'species_Z': ','.join(species_Z)
    }
    comp = Res2SOAP(desc_settings)
    fnames, airss_info = get_res_paths(workdir)
    click.echo('Reading res files')
    atom_list = [[n, read(fn)] for n, fn in enumerate(tqdm(fnames))]
    pool = Pool(nprocs)
    click.echo('Computing descriptors in {} way parallel'.format(nprocs))
    par_res = list(pool.imap_unordered(comp.get_soap_desc, tqdm(atom_list)))
    par_res.sort(key=lambda x: x[0])
    _, descs = zip(*par_res)
    click.echo('Saving files')
    save_file(save_name, descs, airss_info)


if __name__ == '__main__':
    main()
